from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    github_id: str
    login: str
    name: str | None
    email: str | None

    class Config:
        from_attributes = True
