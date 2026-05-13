from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    owner = Column(String, nullable=False)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Linked to the importer
    description = Column(String, nullable=True)
    html_url = Column(String, nullable=False)
    visibility = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
    analyses = relationship("Analysis", cascade="all, delete-orphan")
