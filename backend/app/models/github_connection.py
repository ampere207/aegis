from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base


class GitHubConnection(Base):
    __tablename__ = "github_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    access_token = Column(String, nullable=False)
    scope = Column(String, nullable=True)
    token_type = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
