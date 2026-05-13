from pydantic import BaseModel


class GitHubTokenIn(BaseModel):
    access_token: str
    scope: str | None
    token_type: str | None
