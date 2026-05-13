from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    github_pr_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    state = Column(String, default="open") # open, closed, merged
    base_ref = Column(String, nullable=False) # e.g., main
    head_ref = Column(String, nullable=False) # e.g., feature-auth
    
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    repository = relationship("Repository", back_populates="pull_requests")
    analyses = relationship("Analysis", back_populates="pull_request")
