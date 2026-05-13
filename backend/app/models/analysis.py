import enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
from .base import Base

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    pull_request_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("analyses.id"), nullable=True) # For history tracking
    
    status = Column(Enum(AnalysisStatus), nullable=False, default=AnalysisStatus.PENDING)
    analysis_type = Column(String, default="FULL") # FULL, INCREMENTAL, PR
    
    created_at = Column(DateTime, server_default=func.now())

    findings = relationship("Finding", back_populates="analysis", cascade="all, delete-orphan")
    pull_request = relationship("PullRequest", back_populates="analyses")
    parent = relationship("Analysis", remote_side=[id], backref="children")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="queued")
    worker = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
