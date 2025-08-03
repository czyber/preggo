from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime


class LogBase(SQLModel):
    source: str  # frontend or backend
    level: str = Field(default="info")
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    extra_data: Optional[str] = None


class LogCreate(LogBase):
    pass


class Log(LogBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class LogRead(LogBase):
    id: int