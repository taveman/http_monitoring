"""Models that reflects a domain"""
from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class State(Enum):
    WORKING = 'working'
    FAILED = 'failed'


class ServiceState(BaseModel):
    """Represents service condition"""
    path: str
    state: State
    status_code: int
    create_time: datetime = Field(default_factory=lambda: datetime.utcnow())
    update_time: datetime = Field(default_factory=lambda: datetime.utcnow())


class ServiceResponse(BaseModel):
    """Represents service response"""
    path: str
    status_code: int
    metric: Optional[int]
