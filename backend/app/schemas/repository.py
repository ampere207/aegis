from pydantic import BaseModel, HttpUrl
from typing import Optional


class RepositoryIn(BaseModel):
    owner: str
    name: str
    full_name: str
    html_url: HttpUrl
    clone_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    visibility: Optional[str] = None


class RepositoryOut(BaseModel):
    id: int
    owner: str
    name: str
    full_name: str
    html_url: HttpUrl
    description: Optional[str] = None
    visibility: Optional[str] = None

    class Config:
        from_attributes = True

