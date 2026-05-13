from neo4j import AsyncDriver, AsyncSession
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j graph database abstraction for code & architecture graphs."""

    def __init__(self):
        self.driver: AsyncDriver | None = None

    async def connect(self):
        """Initialize Neo4j connection."""
        if not settings.NEO4J_URI:
            logger.warning("Neo4j not configured; graph operations will be skipped")
            return
        try:
            from neo4j import AsyncGraphDatabase
            self.driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD) if settings.NEO4J_USER else None,
            )
            logger.info("Connected to Neo4j")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    async def close(self):
        """Close Neo4j connection."""
        if self.driver:
            await self.driver.close()

    async def create_repository_node(self, repo_id: int, repo_data: dict):
        """Create a repository node in the graph."""
        if not self.driver:
            return
        async with self.driver.session() as session:
            await session.run(
                "MERGE (r:Repository {repo_id: $repo_id}) SET r.data = $data",
                repo_id=repo_id,
                data=repo_data,
            )

    async def get_repository_graph(self, repo_id: int):
        """Retrieve repository graph structure."""
        if not self.driver:
            return None
        async with self.driver.session() as session:
            result = await session.run(
                "MATCH (r:Repository {repo_id: $repo_id}) RETURN r",
                repo_id=repo_id,
            )
            return await result.single()


neo4j_client = Neo4jClient()
