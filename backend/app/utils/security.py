import time
import jwt
from typing import Any
from ..core.config import settings

_SECRET = (settings.GITHUB_CLIENT_SECRET or "dev-secret")
_ALGORITHM = "HS256"
_EXP_SECONDS = 60 * 60 * 24 * 7


def create_session_token(payload: dict, exp: int | None = None) -> str:
    now = int(time.time())
    to_encode = payload.copy()
    to_encode.update({"iat": now, "exp": now + (exp or _EXP_SECONDS)})
    return jwt.encode(to_encode, _SECRET, algorithm=_ALGORITHM)


def decode_session_token(token: str) -> dict | None:
    try:
        data = jwt.decode(token, _SECRET, algorithms=[_ALGORITHM])
        return data
    except Exception:
        return None
