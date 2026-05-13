from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class AnalysisStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisOut(BaseModel):
    id: int
    repository_id: int
    status: AnalysisStatusEnum
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True
