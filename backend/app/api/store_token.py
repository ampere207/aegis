from fastapi import APIRouter, Depends, HTTPException, Request
from ..schemas.github import GitHubTokenIn
from ..utils.security import decode_session_token
from ..core import db
from ..models.github_connection import GitHubConnection

router = APIRouter()


@router.post("/store-token")
async def store_token(payload: GitHubTokenIn, request: Request):
    token = request.cookies.get("aegis_session")
    if not token:
        raise HTTPException(status_code=401)
    data = decode_session_token(token)
    if not data:
        raise HTTPException(status_code=401)
    user_id = data.get("user_id")

    async for session in db.get_db():
        conn = GitHubConnection(user_id=user_id, access_token=payload.access_token, scope=payload.scope, token_type=payload.token_type)
        session.add(conn)
        await session.commit()

    return {"status": "ok"}
