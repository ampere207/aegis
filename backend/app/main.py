from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .core.config import settings
from .api import auth, repos
from .utils.logger import setup_logging
from .core import db as _db
from .models import base as _base
from .models import user as _user_mod
from .models import repository as _repo_mod
from .models import github_connection as _ghconn
from .models import analysis as _analysis_mod
from .services.neo4j_service import Neo4jService
from .services.qdrant_service import QdrantService

setup_logging()

app = FastAPI(title="Aegis API", version="0.1.0")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(repos.router, prefix="/api/repos", tags=["repos"])
from .api.ws import router as ws_router
app.include_router(ws_router, prefix="/api", tags=["ws"])
from .api.store_token import router as store_token_router
app.include_router(store_token_router, prefix="/api", tags=["auth"])


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    # Ensure database tables exist for Phase 1
    async with _db.engine.begin() as conn:
        await conn.run_sync(_base.Base.metadata.create_all)
    
    # Initialize Neo4j and Qdrant services
    await Neo4jService.initialize()
    await QdrantService.initialize()


@app.on_event("shutdown")
async def on_shutdown():
    # Close database connections
    await _db.engine.dispose()
    await Neo4jService.close()
    await QdrantService.close()
