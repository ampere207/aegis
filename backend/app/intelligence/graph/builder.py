from typing import List, Dict
from ..parser.engine import SemanticEntity
from ...services.neo4j_service import Neo4jService
import logging

logger = logging.getLogger(__name__)

class GraphBuilder:
    def __init__(self, repo_id: int):
        self.repo_id = repo_id

    async def build_graph(self, entities: List[SemanticEntity]):
        """Build graph nodes and infer initial relationships."""
        # 1. Create nodes
        for entity in entities:
            await Neo4jService.create_security_entity(
                self.repo_id, 
                entity.model_dump()
            )
        
        # 2. Infer relationships (simplified for Phase 2)
        # In a real system, this would use data flow analysis.
        # Here we'll infer some based on simple heuristics.
        await self._infer_relationships(entities)

    async def _infer_relationships(self, entities: List[SemanticEntity]):
        # Example: if an API route calls an external service, link them.
        # This is where the 'semantic' part comes in.
        routes = [e for e in entities if e.type == "api_route"]
        calls = [e for e in entities if e.type == "service_call"]
        
        for route in routes:
            for call in calls:
                # If they are in the same file and the call is within the route function
                if route.file_path == call.file_path:
                    if route.line_start <= call.line_start <= route.line_end:
                        from_id = f"{self.repo_id}_{route.file_path}_{route.line_start}"
                        to_id = f"{self.repo_id}_{call.file_path}_{call.line_start}"
                        await Neo4jService.create_relationship(
                            from_id, to_id, "CALLS", 
                            {"inferred": True, "reason": "shared_context"}
                        )
