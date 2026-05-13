import asyncio
import json
import logging
from ..services.ingestion import ingestion_service
from ..services.neo4j_client import neo4j_client
from ..services.qdrant_client import qdrant_store
from ..services.redis_client import redis_client
from ..core import db
from ..models.analysis import Analysis, AnalysisStatus
from sqlalchemy import select

logger = logging.getLogger(__name__)


class BackgroundTaskQueue:
    """Async background task queue for ingestion jobs using Redis."""

    def __init__(self):
        self.running = False

    async def enqueue_ingestion(self, analysis_id: int, repo_url: str, branch: str = "main"):
        """Enqueue a repository ingestion task."""
        task_id = f"ingestion_{analysis_id}"
        await redis_client.set_task_status(
            task_id, "queued", {"analysis_id": str(analysis_id), "repo_url": repo_url, "branch": branch}
        )
        logger.info(f"Enqueued ingestion task: {task_id}")
        
        # For Phase 1, we still process async in the background event loop,
        # but state is now managed via Redis.
        asyncio.create_task(self._process_ingestion(task_id, analysis_id, repo_url, branch))

    async def _process_ingestion(self, task_id: str, analysis_id: int, repo_url: str, branch: str):
        """Process a single ingestion task."""
        try:
            await redis_client.set_task_status(task_id, "running")
            logger.info(f"Starting ingestion: {task_id}")

            # Update analysis status
            async for session in db.get_db():
                stmt = select(Analysis).where(Analysis.id == analysis_id)
                result = await session.execute(stmt)
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.status = AnalysisStatus.RUNNING
                    await session.commit()

            # Validate repository
            validation = await ingestion_service.validate_repository(repo_url, branch)
            if not validation["valid"]:
                raise Exception(f"Validation failed: {validation.get('reason')}")

            # Clone repository
            clone_result = await ingestion_service.clone_repository(repo_url, branch)
            if not clone_result["success"]:
                raise Exception(f"Clone failed: {clone_result.get('error')}")

            repo_path = clone_result["path"]

            # Extract metadata
            metadata = await ingestion_service.get_repository_metadata(repo_path)
            logger.info(f"Repository metadata: {metadata}")

            # Phase 1 Graph & Vector DB Integration Placeholders
            # 1. Neo4j Integration
            logger.info(f"Sending repository {repo_url} data to Neo4j...")
            await neo4j_client.create_repository_node(repo_id=analysis_id, repo_data=metadata)
            
            # 2. Qdrant Integration
            logger.info(f"Creating vector embeddings for {repo_url} in Qdrant...")
            collection_name = f"repo_{analysis_id}"
            await qdrant_store.create_collection(collection_name=collection_name, vector_size=1536)
            
            # Placeholder for actual code chunking and embedding generation
            # await qdrant_store.upsert_vector(collection_name, point_id=1, vector=[0.0]*1536, payload={"file": "README.md"})

            # In Phase 1, we don't parse yet—just validate the ingestion pipeline
            # Future: tree-sitter, ts-morph, Python AST parsing happens here
            # Future: AST → graph nodes → Neo4j, embeddings → Qdrant

            # Cleanup
            await ingestion_service.cleanup_repository(repo_path)

            # Mark analysis as completed
            async for session in db.get_db():
                stmt = select(Analysis).where(Analysis.id == analysis_id)
                result = await session.execute(stmt)
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.status = AnalysisStatus.COMPLETED
                    await session.commit()

            await redis_client.set_task_status(task_id, "completed")
            logger.info(f"Ingestion completed: {task_id}")

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            async for session in db.get_db():
                stmt = select(Analysis).where(Analysis.id == analysis_id)
                result = await session.execute(stmt)
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.status = AnalysisStatus.FAILED
                    await session.commit()
            
            await redis_client.set_task_status(task_id, "failed", {"error": str(e)})

    async def get_task_status(self, task_id: str):
        """Get the status of a task."""
        data = await redis_client.get_task_status(task_id)
        if not data:
            return "unknown"
        return data.get("status", "unknown")


task_queue = BackgroundTaskQueue()
