from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, desc
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_session
from app.models.log import Log, LogCreate, LogRead
from app.core.logging import write_to_dev_log

router = APIRouter()


class FrontendLogRequest(BaseModel):
    level: str = "info"
    message: str
    timestamp: datetime
    metadata: Optional[str] = None


@router.post("/frontend")
def create_frontend_log(*, log_data: FrontendLogRequest):
    """Receive logs from frontend and write to dev.log"""
    write_to_dev_log(
        source="frontend",
        level=log_data.level,
        message=log_data.message,
        metadata=log_data.metadata
    )
    return {"status": "logged"}


@router.get("/", response_model=List[LogRead])
def get_logs(
    *,
    session: Session = Depends(get_session),
    limit: int = 50,
    source: Optional[str] = None
):
    """Get logs, optionally filtered by source"""
    query = select(Log)
    if source:
        query = query.where(Log.source == source)
    query = query.order_by(desc(Log.timestamp)).limit(limit)
    logs = session.exec(query).all()
    # Return in chronological order
    return list(reversed(logs))


@router.delete("/")
def clear_logs(*, session: Session = Depends(get_session)):
    """Clear all logs"""
    session.exec(select(Log)).all()
    for log in session.exec(select(Log)).all():
        session.delete(log)
    session.commit()
    return {"message": "All logs cleared"}