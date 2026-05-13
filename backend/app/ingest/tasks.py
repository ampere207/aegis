import asyncio
from fastapi import BackgroundTasks
from pathlib import Path
from ..ingest.manager import IngestManager
from ..integrations.neo4j_client import Neo4jClient
from ..integrations.qdrant_client import QdrantWrapper
from ..utils.logger import setup_logging

logger = setup_logging()


async def run_ingest(repo_full_name: str, repo_url: str) -> dict:
    dest = IngestManager.create_workspace(repo_full_name)
    ok, msg = IngestManager.shallow_clone(repo_url, dest)
    if not ok:
        IngestManager.cleanup_workspace(dest)
        return {"status": "failed", "reason": msg}

    ok, msg = IngestManager.validate_workspace(dest)
    if not ok:
        IngestManager.cleanup_workspace(dest)
        return {"status": "failed", "reason": msg}

    # Initialize graph/vector clients (stubs) for future ingestion
    neo = Neo4jClient()
    qdr = QdrantWrapper()

    # For Phase 1 we just confirm repository is available and return a summary
    summary = {"status": "completed", "files": len(list(dest.rglob("**/*")))}

    # Cleanup workspace after processing
    IngestManager.cleanup_workspace(dest)
    return summary


def schedule_ingest(background: BackgroundTasks, repo_full_name: str, repo_url: str):
    """Schedule ingestion in FastAPI BackgroundTasks."""
    background.add_task(run_ingest, repo_full_name, repo_url)
