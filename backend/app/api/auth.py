from fastapi import APIRouter, Request, Response, status, Depends
from fastapi.responses import RedirectResponse
import httpx
from ..core.config import settings
from ..utils.security import create_session_token
from ..core import db
from ..models.user import User
from ..models.github_connection import GitHubConnection

router = APIRouter()


@router.get("/login")
async def login():
    # Redirect to GitHub authorize
    client_id = settings.GITHUB_CLIENT_ID
    scope = "repo read:org user:email"
    redirect_uri = f"{settings.BACKEND_ORIGIN}/api/auth/callback"
    url = (
        f"https://github.com/login/oauth/authorize?client_id={client_id}&scope={scope}&redirect_uri={redirect_uri}"
    )
    return RedirectResponse(url)


@router.get("/callback")
async def callback(code: str | None = None, response: Response = None):
    if not code:
        return {"error": "missing_code"}

    token_url = "https://github.com/login/oauth/access_token"
    async with httpx.AsyncClient() as client:
        r = await client.post(
            token_url,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        token_data = r.json()

    access_token = token_data.get("access_token")
    if not access_token:
        return {"error": "token_exchange_failed", "details": token_data}

    # fetch user info
    async with httpx.AsyncClient() as client:
        user_resp = await client.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
        user_json = user_resp.json()

    async for session in db.get_db():
        # create or update user
        github_id = str(user_json.get("id"))
        from sqlalchemy import text
        stmt = await session.execute(
            text("SELECT id FROM users WHERE github_id = :gid"),
            {"gid": github_id},
        )
        row = stmt.first()
        if row:
            user_id = row[0]
        else:
            user = User(github_id=github_id, login=user_json.get("login"), name=user_json.get("name"), email=user_json.get("email"))
            session.add(user)
            await session.commit()
            await session.refresh(user)
            user_id = user.id

        # persist github connection
        conn = GitHubConnection(user_id=user_id, access_token=access_token, scope=token_data.get("scope"), token_type=token_data.get("token_type"))
        session.add(conn)
        await session.commit()

    # create session cookie
    token = create_session_token({"user_id": user_id})
    response = RedirectResponse(url=f"{settings.FRONTEND_ORIGIN}/dashboard")
    response.set_cookie("aegis_session", token, httponly=True, secure=False, samesite="lax")
    return response

@router.get("/me")
async def get_me(request: Request):
    token = request.cookies.get("aegis_session")
    if not token:
        return {"authenticated": False}
    
    from ..utils.security import decode_session_token
    data = decode_session_token(token)
    if not data:
        return {"authenticated": False}
    
    user_id = data.get("user_id")
    async for session in db.get_db():
        from sqlalchemy import select
        stmt = select(User).where(User.id == user_id)
        res = await session.execute(stmt)
        user = res.scalar()
        if user:
            return {
                "authenticated": True,
                "user": {
                    "id": user.id,
                    "login": user.login,
                    "name": user.name,
                    "email": user.email
                }
            }
    
    return {"authenticated": False}
