from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    severity = Column(String, default="info") # info, low, medium, high, critical
    type = Column(String) # architectural, trust_boundary, privilege_escalation
    extra_data = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="findings")
