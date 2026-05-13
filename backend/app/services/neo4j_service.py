"""Neo4j graph database service abstraction."""
from neo4j import AsyncDriver, AsyncSession
from ..core.config import settings
from ..core.cache import cache_response
import logging

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service for Neo4j graph operations.
    
    Phase 1: Stub implementation for future semantic graph analysis.
    Will expand to support:
    - AST node ingestion
    - Trust boundary mapping
    - API relationship graphs
    - Privilege flow analysis
    """
    
    _driver: AsyncDriver | None = None

    @classmethod
    async def initialize(cls) -> None:
        """Initialize Neo4j connection on startup."""
        if settings.NEO4J_URI:
            try:
                from neo4j import AsyncGraphDatabase
                cls._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                )
                logger.info("Neo4j connected")
            except Exception as e:
                logger.error(f"Neo4j connection failed: {e}")

    @classmethod
    async def close(cls) -> None:
        """Close Neo4j connection on shutdown."""
        if cls._driver:
            await cls._driver.close()

    @classmethod
    async def execute_query(cls, query: str, params: dict | None = None) -> list:
        """Execute a Cypher query. Phase 1: placeholder."""
        if not cls._driver:
            return []
        try:
            async with cls._driver.session() as session:
                result = await session.run(query, params or {})
                records = await result.fetch(256)
                return records
        except Exception as e:
            logger.error(f"Neo4j query failed: {e}")
            return []

    @classmethod
    async def create_repository_node(cls, repo_id: int, full_name: str, owner: str) -> None:
        """Create repository node in graph."""
        query = """
        MERGE (r:Repository {id: $id, name: $name, owner: $owner})
        RETURN r
        """
        await cls.execute_query(query, {"id": repo_id, "name": full_name, "owner": owner})

    @classmethod
    async def create_security_entity(cls, repo_id: int, entity: dict) -> None:
        """Create a security entity node linked to a repository."""
        query = """
        MATCH (r:Repository {id: $repo_id})
        MERGE (e:SecurityEntity {
            id: $entity_id,
            name: $name,
            type: $type,
            file_path: $file_path
        })
        MERGE (r)-[:CONTAINS]->(e)
        SET e += $metadata
        """
        params = {
            "repo_id": repo_id,
            "entity_id": f"{repo_id}_{entity['file_path']}_{entity['line_start']}",
            "name": entity["name"],
            "type": entity["type"],
            "file_path": entity["file_path"],
            "metadata": entity.get("metadata", {})
        }
        await cls.execute_query(query, params)

    @classmethod
    async def create_relationship(cls, from_id: str, to_id: str, rel_type: str, metadata: dict | None = None) -> None:
        """Create a relationship between two security entities."""
        query = f"""
        MATCH (a:SecurityEntity {{id: $from_id}})
        MATCH (b:SecurityEntity {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $metadata
        """
        await cls.execute_query(query, {
            "from_id": from_id,
            "to_id": to_id,
            "metadata": metadata or {}
        })
    @classmethod
    @cache_response("blast_radius", expire=1800)
    async def get_blast_radius(cls, entity_id: str, depth: int = 3) -> list:
        """Find all downstream entities affected by a compromise of the given entity."""
        query = f"""
        MATCH (e:SecurityEntity {{id: $entity_id}})
        MATCH (e)-[:CALLS|TRUSTS|DEPENDS_ON*1..{depth}]->(downstream)
        RETURN DISTINCT downstream
        """
        return await cls.execute_query(query, {"entity_id": entity_id})

    @classmethod
    @cache_response("attack_paths", expire=1800)
    async def get_attack_paths(cls, repo_id: int) -> list:
        """Identify potential attack paths from unauthenticated boundaries to sensitive sinks."""
        query = """
        MATCH (source:SecurityEntity {type: 'API_ROUTE'})
        WHERE source.is_authenticated = false OR source.auth_required = false
        MATCH (sink:SecurityEntity)
        WHERE sink.type IN ['DATABASE_OPERATION', 'SENSITIVE_SERVICE_CALL']
        MATCH path = shortestPath((source)-[:CALLS|TRUSTS*..10]->(sink))
        RETURN path
        """
        return await cls.execute_query(query, {"repo_id": repo_id})

    @classmethod
    async def get_repository_graph(cls, repo_id: int) -> dict:
        """Fetch all nodes and relationships for a repository."""
        query = """
        MATCH (r:Repository {id: $repo_id})-[:CONTAINS]->(e:SecurityEntity)
        OPTIONAL MATCH (e)-[rel]->(other:SecurityEntity)
        WHERE (r)-[:CONTAINS]->(other)
        RETURN e as node, rel as relationship, other as target
        """
        records = await cls.execute_query(query, {"repo_id": repo_id})
        
        nodes = {}
        edges = []
        
        for record in records:
            # Process main node
            n = record["node"]
            if n and n.get("id") not in nodes:
                nodes[n["id"]] = {
                    "id": n["id"],
                    "label": n.get("name", "Unknown"),
                    "type": n.get("type", "entity"),
                    "file_path": n.get("file_path", "")
                }
            
            # Process target node if exists
            t = record["target"]
            if t and t.get("id") not in nodes:
                nodes[t["id"]] = {
                    "id": t["id"],
                    "label": t.get("name", "Unknown"),
                    "type": t.get("type", "entity"),
                    "file_path": t.get("file_path", "")
                }
            
            # Process relationship
            r = record["relationship"]
            if r:
                edges.append({
                    "id": f"e_{n['id']}_{t['id']}",
                    "source": n["id"],
                    "target": t["id"],
                    "label": "CALLS" # Simplified for Phase 1
                })
        
        return {"nodes": list(nodes.values()), "edges": edges}
