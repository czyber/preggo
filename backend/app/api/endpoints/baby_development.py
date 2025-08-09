from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, and_, or_
from app.db.session import get_session
from app.models.baby_development import BabyDevelopment, TrimesterType
from app.schemas.baby_development import (
    BabyDevelopmentCreate, BabyDevelopmentUpdate, BabyDevelopmentResponse,
    BabyDevelopmentSummary, BabyDevelopmentByWeek, BabyDevelopmentByTrimester,
    BabyDevelopmentStats, BabyDevelopmentSearch
)
from app.services.baby_development_service import BabyDevelopmentService

router = APIRouter()


def get_baby_development_service(db: Session = Depends(get_session)) -> BabyDevelopmentService:
    """Get baby development service with database session"""
    return BabyDevelopmentService(db)


@router.get("/", response_model=List[BabyDevelopmentSummary])
def list_baby_developments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return"),
    week_number: Optional[int] = Query(None, ge=1, le=45, description="Filter by week number"),
    trimester: Optional[TrimesterType] = Query(None, description="Filter by trimester"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: Session = Depends(get_session)
):
    """List baby development records with optional filtering"""
    query = select(BabyDevelopment).where(BabyDevelopment.is_active == is_active)
    
    if week_number is not None:
        query = query.where(BabyDevelopment.week_number == week_number)
    
    if trimester is not None:
        query = query.where(BabyDevelopment.trimester == trimester)
    
    query = query.order_by(BabyDevelopment.day_of_pregnancy).offset(skip).limit(limit)
    
    developments = db.exec(query).all()
    return developments


@router.get("/search", response_model=List[BabyDevelopmentSummary])
def search_baby_developments(
    search_params: BabyDevelopmentSearch = Depends(),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_session)
):
    """Advanced search for baby development records"""
    query = select(BabyDevelopment).where(BabyDevelopment.is_active == search_params.is_active)
    
    # Apply filters based on search parameters
    if search_params.week_number is not None:
        query = query.where(BabyDevelopment.week_number == search_params.week_number)
    
    if search_params.trimester is not None:
        query = query.where(BabyDevelopment.trimester == search_params.trimester)
    
    if search_params.day_range_start is not None:
        query = query.where(BabyDevelopment.day_of_pregnancy >= search_params.day_range_start)
    
    if search_params.day_range_end is not None:
        query = query.where(BabyDevelopment.day_of_pregnancy <= search_params.day_range_end)
    
    if search_params.search_text:
        search_term = f"%{search_params.search_text}%"
        query = query.where(
            or_(
                BabyDevelopment.title.ilike(search_term),
                BabyDevelopment.brief_description.ilike(search_term),
                BabyDevelopment.baby_size_comparison.ilike(search_term),
                BabyDevelopment.fun_fact.ilike(search_term)
            )
        )
    
    query = query.order_by(BabyDevelopment.day_of_pregnancy).offset(skip).limit(limit)
    
    developments = db.exec(query).all()
    return developments


@router.get("/by-day/{day}", response_model=BabyDevelopmentResponse)
def get_baby_development_by_day(day: int, db: Session = Depends(get_session)):
    """Get baby development information for a specific pregnancy day"""
    if not 1 <= day <= 310:
        raise HTTPException(status_code=400, detail="Day must be between 1 and 310")
    
    development = db.exec(
        select(BabyDevelopment).where(
            and_(
                BabyDevelopment.day_of_pregnancy == day,
                BabyDevelopment.is_active == True
            )
        )
    ).first()
    
    if not development:
        raise HTTPException(status_code=404, detail=f"No development data found for day {day}")
    
    return development


@router.get("/by-week/{week}", response_model=List[BabyDevelopmentSummary])
def get_baby_developments_by_week(week: int, db: Session = Depends(get_session)):
    """Get all baby development records for a specific week"""
    if not 1 <= week <= 45:
        raise HTTPException(status_code=400, detail="Week must be between 1 and 45")
    
    developments = db.exec(
        select(BabyDevelopment).where(
            and_(
                BabyDevelopment.week_number == week,
                BabyDevelopment.is_active == True
            )
        ).order_by(BabyDevelopment.day_of_pregnancy)
    ).all()
    
    if not developments:
        raise HTTPException(status_code=404, detail=f"No development data found for week {week}")
    
    return developments


@router.get("/by-trimester/{trimester}", response_model=List[BabyDevelopmentSummary])
def get_baby_developments_by_trimester(
    trimester: TrimesterType,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_session)
):
    """Get baby development records for a specific trimester"""
    developments = db.exec(
        select(BabyDevelopment).where(
            and_(
                BabyDevelopment.trimester == trimester,
                BabyDevelopment.is_active == True
            )
        ).order_by(BabyDevelopment.day_of_pregnancy).offset(skip).limit(limit)
    ).all()
    
    return developments


@router.get("/stats", response_model=BabyDevelopmentStats)
def get_baby_development_stats(
    service: BabyDevelopmentService = Depends(get_baby_development_service)
):
    """Get statistics about the baby development database"""
    return service.get_stats()


@router.get("/{development_id}", response_model=BabyDevelopmentResponse)
def get_baby_development(development_id: str, db: Session = Depends(get_session)):
    """Get a specific baby development record by ID"""
    development = db.exec(
        select(BabyDevelopment).where(BabyDevelopment.id == development_id)
    ).first()
    
    if not development:
        raise HTTPException(status_code=404, detail="Baby development record not found")
    
    return development


@router.post("/", response_model=BabyDevelopmentResponse)
def create_baby_development(
    development_data: BabyDevelopmentCreate,
    db: Session = Depends(get_session)
):
    """Create a new baby development record"""
    # Check if a record already exists for this day
    existing = db.exec(
        select(BabyDevelopment).where(
            BabyDevelopment.day_of_pregnancy == development_data.day_of_pregnancy
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Development record already exists for day {development_data.day_of_pregnancy}"
        )
    
    development = BabyDevelopment(**development_data.model_dump())
    db.add(development)
    db.commit()
    db.refresh(development)
    
    return development


@router.put("/{development_id}", response_model=BabyDevelopmentResponse)
def update_baby_development(
    development_id: str,
    development_data: BabyDevelopmentUpdate,
    db: Session = Depends(get_session)
):
    """Update an existing baby development record"""
    development = db.exec(
        select(BabyDevelopment).where(BabyDevelopment.id == development_id)
    ).first()
    
    if not development:
        raise HTTPException(status_code=404, detail="Baby development record not found")
    
    # Update fields that were provided
    update_data = development_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(development, field, value)
    
    db.add(development)
    db.commit()
    db.refresh(development)
    
    return development


@router.delete("/{development_id}")
def delete_baby_development(development_id: str, db: Session = Depends(get_session)):
    """Soft delete a baby development record (marks as inactive)"""
    development = db.exec(
        select(BabyDevelopment).where(BabyDevelopment.id == development_id)
    ).first()
    
    if not development:
        raise HTTPException(status_code=404, detail="Baby development record not found")
    
    development.is_active = False
    db.add(development)
    db.commit()
    
    return {"message": "Baby development record deactivated successfully"}