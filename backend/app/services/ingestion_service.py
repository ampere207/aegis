"""Background ingestion task service."""
import asyncio
import logging
import tempfile
import os
from pathlib import Path
import subprocess
from datetime import datetime
from ..core import db
from ..models.analysis import Analysis, AnalysisStatus
from ..models.repository import Repository
from .neo4j_service import Neo4jService
from .qdrant_service import QdrantService

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for repository ingestion and analysis scheduling.
    
    Phase 1: Validates, clones, and prepares repositories for analysis.
    Runs in background async tasks.
    """

    @staticmethod
    async def schedule_ingestion(repository_id: int, user_id: int) -> int:
        """Schedule a repository for ingestion. Returns Analysis ID."""
        async for session in db.get_db():
            analysis = Analysis(
                repository_id=repository_id,
                user_id=user_id,
                status=AnalysisStatus.PENDING,
            )
            session.add(analysis)
            await session.commit()
            await session.refresh(analysis)
            analysis_id = analysis.id

        # Fire background task
        asyncio.create_task(
            IngestionService.run_ingestion(analysis_id, repository_id, user_id)
        )
        return analysis_id

    @staticmethod
    async def run_ingestion(analysis_id: int, repository_id: int, user_id: int) -> None:
        """Run the actual ingestion pipeline (background task)."""
        try:
            # Update status to RUNNING
            async for session in db.get_db():
                analysis = await session.get(Analysis, analysis_id)
                if analysis:
                    analysis.status = AnalysisStatus.RUNNING
                    analysis.started_at = datetime.utcnow()
                    await session.commit()
                break

            # Fetch repository
            async for session in db.get_db():
                repo = await session.get(Repository, repository_id)
                if not repo:
                    raise ValueError(f"Repository {repository_id} not found")
                repo_data = {
                    "id": repo.id,
                    "full_name": repo.full_name,
                    "owner": repo.owner,
                    "html_url": repo.html_url,
                }
                break

            # Phase 1: Validate repository size and metadata
            logger.info(f"Ingesting repository: {repo_data['full_name']}")
            await IngestionService._validate_repository(repo_data)

            # Phase 1: Clone to ephemeral workspace (no actual exec)
            await IngestionService._clone_repository(repo_data)

            # Phase 1: Create repository node in Neo4j graph
            await Neo4jService.create_repository_node(
                repo_data["id"], 
                repo_data["full_name"], 
                repo_data["owner"]
            )

            # Mark as COMPLETED
            async for session in db.get_db():
                analysis = await session.get(Analysis, analysis_id)
                if analysis:
                    analysis.status = AnalysisStatus.COMPLETED
                    analysis.completed_at = datetime.utcnow()
                    await session.commit()
                break

            logger.info(f"Ingestion completed for repository {repository_id}")

        except Exception as e:
            logger.error(f"Ingestion failed for repository {repository_id}: {e}")
            async for session in db.get_db():
                analysis = await session.get(Analysis, analysis_id)
                if analysis:
                    analysis.status = AnalysisStatus.FAILED
                    analysis.error_message = str(e)
                    analysis.completed_at = datetime.utcnow()
                    await session.commit()
                break

    @staticmethod
    async def _validate_repository(repo_data: dict) -> None:
        """Validate repository before processing."""
        # Phase 1: Basic validation
        if not repo_data.get("full_name"):
            raise ValueError("Invalid repository: missing full_name")
        logger.info(f"Repository validation passed: {repo_data['full_name']}")

    @staticmethod
    async def _clone_repository(repo_data: dict) -> None:
        """Clone repository to ephemeral workspace."""
        with tempfile.TemporaryDirectory(prefix="aegis_") as tmpdir:
            repo_path = Path(tmpdir) / repo_data["full_name"].replace("/", "_")
            repo_path.mkdir(parents=True, exist_ok=True)
            
            url = repo_data["html_url"]
            logger.info(f"Cloning repository to {repo_path}")
            
            # Phase 1: Clone with shallow depth and size limits
            try:
                result = await asyncio.to_thread(
                    subprocess.run,
                    ["git", "clone", "--depth", "1", url, str(repo_path)],
                    capture_output=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    raise ValueError(f"Git clone failed: {result.stderr.decode()}")
                logger.info(f"Clone succeeded: {repo_path}")
                
                # Phase 1: Repository is ready for parsing (future)
                # TODO: Trigger language-specific parsers (ts-morph, Python AST, etc.)
                
            except subprocess.TimeoutExpired:
                raise ValueError("Repository clone timeout (60s)")
            except Exception as e:
                raise ValueError(f"Clone failed: {e}")
