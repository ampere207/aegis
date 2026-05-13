from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from ..schemas import repository as repo_schema
from ..schemas import analysis as analysis_schema
from ..services.github_client import GitHubClient
from ..utils.security import decode_session_token
from ..core import db
from ..models.user import User
from ..models.repository import Repository
from ..models.analysis import Analysis
from ..models.github_connection import GitHubConnection
from ..services.repository_service import RepositoryService
from ..services.ingestion_service import IngestionService
from ..ingest.tasks import schedule_ingest
from ..core.config import settings
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_current_user(request: Request) -> User | None:
    token = request.cookies.get("aegis_session")
    if not token:
        return None
    data = decode_session_token(token)
    if not data:
        return None
    user_id = data.get("user_id")
    async for session in db.get_db():
        res = await session.get(User, user_id)
        return res


@router.get("/available", response_model=List[repo_schema.RepositoryOut])
async def list_available_repos(request: Request, q: str | None = None):
    """List repositories available on GitHub for the authenticated user."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(GitHubConnection).filter(GitHubConnection.user_id == user.id).order_by(GitHubConnection.created_at.desc()).limit(1)
        res = await session.execute(stmt)
        conn = res.scalar()
        token = conn.access_token if conn else None
        break

    client = GitHubClient()
    repos = await client.list_user_repos(access_token=token, q=q)
    return repos


@router.get("/imported", response_model=List[repo_schema.RepositoryOut])
async def list_imported_repos(request: Request):
    """List repositories already imported by the user."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(Repository).where(Repository.user_id == user.id).limit(100)
        res = await session.execute(stmt)
        repos = res.scalars().all()
        return repos
        break


@router.post("/import")
async def import_repo(payload: repo_schema.RepositoryIn, request: Request, background: BackgroundTasks):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        repo_data = payload.model_dump(mode='json')
        repo_data["user_id"] = user.id
        repo_obj = await RepositoryService.create_repository(repo_data)
        logger.info(f"Repository created: {repo_obj.id} ({payload.full_name})")

        schedule_ingest(background, payload.full_name, str(payload.html_url))
        logger.info(f"Ingestion scheduled for {payload.full_name}")

        analysis_id = await IngestionService.schedule_ingestion(repo_obj.id, user.id)
        return {"status": "import_scheduled", "repo_id": repo_obj.id, "analysis_id": analysis_id}
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{repo_id}/analysis", response_model=List[analysis_schema.AnalysisOut])
async def get_repository_analyses(repo_id: int, request: Request):
    """Get analysis history for a repository."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(Analysis).filter(Analysis.repository_id == repo_id).order_by(Analysis.created_at.desc()).limit(20)
        res = await session.execute(stmt)
        analyses = res.scalars().all()
        return analyses


@router.get("/{repo_id}")
async def get_repository_details(repo_id: int, request: Request):
    """Get full details of a repository."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        stmt = select(Repository).where(Repository.id == repo_id).options(selectinload(Repository.analyses))
        res = await session.execute(stmt)
        repo = res.scalar_one_or_none()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Sort analyses descending to get the latest
        analyses_data = [
            {"id": a.id, "status": a.status.value, "created_at": a.created_at.isoformat()}
            for a in sorted(repo.analyses, key=lambda x: x.created_at, reverse=True)
        ]
        
        return {
            "id": repo.id,
            "full_name": repo.full_name,
            "html_url": repo.html_url,
            "description": repo.description,
            "analyses": analyses_data
        }


@router.get("/{repo_id}/status")
async def get_repository_status(repo_id: int, request: Request):
    """Get the latest analysis status for a repository."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(Repository).where(Repository.id == repo_id)
        res = await session.execute(stmt)
        repo = res.scalar_one_or_none()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        stmt_analysis = select(Analysis).filter(Analysis.repository_id == repo_id).order_by(Analysis.created_at.desc()).limit(1)
        res_analysis = await session.execute(stmt_analysis)
        latest_analysis = res_analysis.scalar_one_or_none()
        
        return {
            "repository_id": repo.id,
            "full_name": repo.full_name,
            "analyses": [{"id": latest_analysis.id, "status": latest_analysis.status.value}] if latest_analysis else []
        }

@router.post("/{repo_id}/analyze")
async def trigger_analysis(repo_id: int, request: Request, background: BackgroundTasks):
    """Trigger the core intelligence analysis pipeline."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(Repository).where(Repository.id == repo_id)
        res = await session.execute(stmt)
        repo = res.scalar_one_or_none()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # In a real system, repo_path would be the path to the cloned repository
        # For this implementation, we'll assume a path or use a placeholder
        repo_path = f"{settings.REPOS_STORAGE_PATH}/{repo.full_name}"
        
        from ..intelligence.pipeline import AnalysisPipeline
        from .ws import manager as ws_manager
        
        async def run_analysis():
            pipeline = AnalysisPipeline(repo_id, repo_path)
            await ws_manager.broadcast(repo_id, {"stage": "started", "message": "Starting semantic analysis..."})
            
            try:
                # 1. Parsing
                await ws_manager.broadcast(repo_id, {"stage": "parsing", "message": "Parsing code structure with Tree-sitter..."})
                # 2. Graph Generation
                await ws_manager.broadcast(repo_id, {"stage": "graph", "message": "Building semantic security graph..."})
                # 3. Reasoning
                await ws_manager.broadcast(repo_id, {"stage": "reasoning", "message": "AI Reasoning with Gemini..."})
                
                findings = await pipeline.run()
                
                await ws_manager.broadcast(repo_id, {
                    "stage": "completed", 
                    "message": "Analysis completed successfully.",
                    "findings": findings
                })
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                await ws_manager.broadcast(repo_id, {"stage": "failed", "message": f"Analysis failed: {str(e)}"})

        background.add_task(run_analysis)
        return {"status": "analysis_started", "repo_id": repo_id}
@router.post("/{repo_id}/pr/{pr_number}/analyze")
async def trigger_pr_analysis(repo_id: int, pr_number: int, request: Request, background: BackgroundTasks):
    """Trigger a PR-specific architectural security analysis."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(Repository).where(Repository.id == repo_id)
        res = await session.execute(stmt)
        repo = res.scalar_one_or_none()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get access token
        stmt_conn = select(GitHubConnection).filter(GitHubConnection.user_id == user.id).order_by(GitHubConnection.created_at.desc()).limit(1)
        res_conn = await session.execute(stmt_conn)
        conn = res_conn.scalar()
        token = conn.access_token if conn else None
        
        from ..intelligence.pr_analyzer import PRAnalyzer
        from .ws import manager as ws_manager
        
        async def run_pr_analysis():
            analyzer = PRAnalyzer()
            await ws_manager.broadcast(repo_id, {"stage": "started", "message": f"Starting analysis for PR #{pr_number}..."})
            
            try:
                owner, name = repo.full_name.split("/")
                result = await analyzer.analyze_pr(owner, name, pr_number, token, repo_id)
                
                await ws_manager.broadcast(repo_id, {
                    "stage": "completed",
                    "message": "PR Analysis completed.",
                    "findings": result.get("findings", []),
                    "impacted_files": result.get("impacted_files", [])
                })
            except Exception as e:
                logger.error(f"PR Analysis failed: {e}")
                await ws_manager.broadcast(repo_id, {"stage": "failed", "message": f"PR Analysis failed: {str(e)}"})

        background.add_task(run_pr_analysis)
        return {"status": "pr_analysis_started", "repo_id": repo_id, "pr_number": pr_number}

@router.get("/{repo_id}/blast-radius/{entity_id}")
async def get_blast_radius(repo_id: int, entity_id: str, depth: int = 3):
    """Get the architectural blast radius for a compromised entity."""
    from ..services.neo4j_service import Neo4jService
    nodes = await Neo4jService.get_blast_radius(entity_id, depth)
    return {"entity_id": entity_id, "affected_nodes": nodes}

@router.get("/{repo_id}/attack-paths")
async def get_attack_paths(repo_id: int):
    """Identify potential attack paths in the security knowledge graph."""
    from ..services.neo4j_service import Neo4jService
    paths = await Neo4jService.get_attack_paths(repo_id)
    return {"repo_id": repo_id, "paths": paths}
@router.get("/{repo_id}/graph")
async def get_repo_graph(repo_id: int, request: Request):
    """Get the dynamic semantic graph for a repository."""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    from ..services.neo4j_service import Neo4jService
    graph_data = await Neo4jService.get_repository_graph(repo_id)
    return graph_data
