"""
Pregnancy management endpoints for CRUD operations and week tracking - CORRECTED VERSION.

This module provides endpoints for:
- Creating and managing pregnancies using SQLModel sessions
- Week-by-week pregnancy tracking
- Pregnancy details and updates
- Partner management and sharing

NOTE: This is the corrected version that uses SQLModel sessions instead of direct Supabase operations.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlmodel import Session

from app.core.supabase import get_current_active_user
from app.services import pregnancy_service, weekly_update_service
from app.db.session import get_session
from app.core.config import settings
from app.schemas.pregnancy import (
    PregnancyCreate, 
    PregnancyUpdate, 
    PregnancyResponse,
    WeeklyUpdateResponse
)
from app.models.pregnancy import (
    PregnancyStatus, 
    RiskLevel,
    BabyInfo,
    PregnancyDetails,
    PregnancyPreferences
)

router = APIRouter(prefix="/pregnancies", tags=["pregnancies"])


class PregnancyWeekCalculation(BaseModel):
    """Model for pregnancy week calculation response"""
    current_week: int
    current_day: int
    trimester: int
    days_pregnant: int
    weeks_remaining: int
    due_date: date
    progress_percentage: float


class WeeklyJourneyResponse(BaseModel):
    """Response model for weekly pregnancy journey"""
    pregnancy_id: str
    current_week: int
    baby_development: Dict[str, Any]
    maternal_changes: Dict[str, Any]
    tips: List[str]
    checklist: List[Dict[str, Any]]
    size_comparison: Optional[str]
    estimated_size: Optional[Dict[str, Any]]


@router.post("/", response_model=PregnancyResponse, status_code=status.HTTP_201_CREATED)
async def create_pregnancy(
    pregnancy_data: PregnancyCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Create a new pregnancy record using SQLModel session.
    """
    try:
        user_id = current_user["sub"]  # Use 'sub' from JWT token as user_id
        
        # Check if user already has active pregnancies (business rule)
        existing_pregnancies = await pregnancy_service.get_active_pregnancies(session, user_id)
        
        # For now, allow only one active pregnancy per user
        if len(existing_pregnancies) >= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active pregnancy. Complete or archive the existing one first."
            )
        
        # Calculate pregnancy details
        due_date = pregnancy_data.pregnancy_details.due_date
        today = date.today()
        
        # Calculate weeks and days pregnant
        if pregnancy_data.pregnancy_details.conception_date:
            conception_date = pregnancy_data.pregnancy_details.conception_date
        else:
            # Estimate conception date (due date - 280 days)
            conception_date = due_date - timedelta(days=280)
        
        days_pregnant = (today - conception_date).days
        current_week = max(0, min(days_pregnant // 7, settings.MAX_PREGNANCY_WEEK))
        current_day = max(0, days_pregnant % 7)
        
        # Determine trimester
        if current_week <= 12:
            trimester = 1
        elif current_week <= 26:
            trimester = 2
        else:
            trimester = 3
        
        # Prepare pregnancy data
        pregnancy_record = {
            "user_id": user_id,
            "partner_ids": pregnancy_data.partner_ids or [],
            "pregnancy_details": {
                "due_date": due_date,
                "conception_date": conception_date,
                "current_week": current_week,
                "current_day": current_day,
                "trimester": trimester,
                "is_multiple": pregnancy_data.pregnancy_details.is_multiple,
                "expected_babies": [baby.dict() for baby in pregnancy_data.pregnancy_details.expected_babies],
                "risk_level": pregnancy_data.pregnancy_details.risk_level
            },
            "preferences": pregnancy_data.preferences.dict() if pregnancy_data.preferences else {},
            "status": PregnancyStatus.ACTIVE
        }
        
        # Create pregnancy record using service
        created_pregnancy = await pregnancy_service.create_pregnancy(session, pregnancy_record)
        if not created_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create pregnancy record"
            )
        
        return PregnancyResponse.from_orm(created_pregnancy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pregnancy: {str(e)}"
        )


@router.get("/", response_model=List[PregnancyResponse])
async def get_user_pregnancies(
    active_only: bool = Query(True, description="Return only active pregnancies"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get all pregnancies for the current user using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        if active_only:
            pregnancies = await pregnancy_service.get_active_pregnancies(session, user_id)
        else:
            pregnancies = await pregnancy_service.get_user_pregnancies(session, user_id)
        
        return [PregnancyResponse.from_orm(pregnancy) for pregnancy in pregnancies]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pregnancies: {str(e)}"
        )


@router.get("/{pregnancy_id}", response_model=PregnancyResponse)
async def get_pregnancy(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get a specific pregnancy by ID using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get pregnancy data
        pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
        
        if not pregnancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        return PregnancyResponse.from_orm(pregnancy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pregnancy: {str(e)}"
        )


@router.put("/{pregnancy_id}", response_model=PregnancyResponse)
async def update_pregnancy(
    pregnancy_id: str,
    pregnancy_update: PregnancyUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Update a pregnancy record using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        update_dict = pregnancy_update.dict(exclude_unset=True)
        
        for key, value in update_dict.items():
            if value is not None:
                update_data[key] = value
        
        if not update_data:
            # No updates provided, fetch and return current data
            pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
            return PregnancyResponse.from_orm(pregnancy)
        
        # Update pregnancy record
        updated_pregnancy = await pregnancy_service.update_pregnancy(session, pregnancy_id, update_data)
        
        if not updated_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pregnancy"
            )
        
        return PregnancyResponse.from_orm(updated_pregnancy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pregnancy: {str(e)}"
        )


@router.get("/{pregnancy_id}/week-calculation", response_model=PregnancyWeekCalculation)
async def calculate_pregnancy_week(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Calculate current pregnancy week and related information.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get pregnancy data
        pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
        
        if not pregnancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        pregnancy_details = pregnancy.pregnancy_details
        due_date = pregnancy_details["due_date"]
        conception_date = pregnancy_details.get("conception_date")
        
        if not conception_date:
            conception_date = due_date - timedelta(days=280)
        
        today = date.today()
        days_pregnant = (today - conception_date).days
        current_week = max(0, min(days_pregnant // 7, settings.MAX_PREGNANCY_WEEK))
        current_day = max(0, days_pregnant % 7)
        
        # Determine trimester
        if current_week <= 12:
            trimester = 1
        elif current_week <= 26:
            trimester = 2
        else:
            trimester = 3
        
        # Calculate remaining weeks
        total_days = (due_date - conception_date).days
        weeks_remaining = max(0, (total_days - days_pregnant) // 7)
        
        # Calculate progress percentage
        progress_percentage = min(100.0, (days_pregnant / total_days) * 100 if total_days > 0 else 0)
        
        return PregnancyWeekCalculation(
            current_week=current_week,
            current_day=current_day,
            trimester=trimester,
            days_pregnant=days_pregnant,
            weeks_remaining=weeks_remaining,
            due_date=due_date,
            progress_percentage=round(progress_percentage, 1)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate pregnancy week: {str(e)}"
        )


@router.get("/{pregnancy_id}/weekly-journey", response_model=WeeklyJourneyResponse)
async def get_weekly_journey(
    pregnancy_id: str,
    week: Optional[int] = Query(None, description="Specific week to get info for (defaults to current week)"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get week-by-week pregnancy journey information using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # If no week specified, calculate current week
        if week is None:
            calc_response = await calculate_pregnancy_week(pregnancy_id, current_user, session)
            week = calc_response.current_week
        
        # Validate week range
        if week < 0 or week > settings.MAX_PREGNANCY_WEEK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Week must be between 0 and {settings.MAX_PREGNANCY_WEEK}"
            )
        
        # Get weekly update data using service
        weekly_data = await weekly_update_service.get_weekly_update_by_week(session, pregnancy_id, week)
        
        if weekly_data:
            return WeeklyJourneyResponse(
                pregnancy_id=pregnancy_id,
                current_week=week,
                baby_development={
                    "development": weekly_data.baby_development,
                    "size": {
                        "length": weekly_data.baby_size_length,
                        "weight": weekly_data.baby_size_weight,
                        "comparison": weekly_data.baby_size_comparison
                    }
                },
                maternal_changes={
                    "changes": weekly_data.maternal_changes,
                    "symptoms": weekly_data.common_symptoms
                },
                tips=weekly_data.tips,
                checklist=[],  # This would come from a separate checklist table
                size_comparison=weekly_data.baby_size_comparison,
                estimated_size={
                    "length_cm": weekly_data.baby_size_length,
                    "weight_grams": weekly_data.baby_size_weight
                }
            )
        else:
            # Return default/template data if no specific weekly update exists
            return WeeklyJourneyResponse(
                pregnancy_id=pregnancy_id,
                current_week=week,
                baby_development={
                    "development": f"Your baby is developing rapidly at week {week}.",
                    "size": {}
                },
                maternal_changes={
                    "changes": f"Your body continues to change during week {week}.",
                    "symptoms": []
                },
                tips=[],
                checklist=[],
                size_comparison=None,
                estimated_size={}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weekly journey: {str(e)}"
        )


@router.post("/{pregnancy_id}/partners/{partner_id}")
async def add_partner(
    pregnancy_id: str,
    partner_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Add a partner to the pregnancy using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Add partner using service
        updated_pregnancy = await pregnancy_service.add_partner(session, pregnancy_id, partner_id)
        
        if not updated_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        return {"message": "Partner added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add partner: {str(e)}"
        )


@router.delete("/{pregnancy_id}/partners/{partner_id}")
async def remove_partner(
    pregnancy_id: str,
    partner_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Remove a partner from the pregnancy using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Remove partner using service
        updated_pregnancy = await pregnancy_service.remove_partner(session, pregnancy_id, partner_id)
        
        if not updated_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        return {"message": "Partner removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove partner: {str(e)}"
        )


@router.put("/{pregnancy_id}/status")
async def update_pregnancy_status(
    pregnancy_id: str,
    new_status: PregnancyStatus,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Update pregnancy status (active, completed, archived) using SQLModel session.
    """
    try:
        user_id = current_user["sub"]
        
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Update pregnancy status using service
        if new_status == PregnancyStatus.ARCHIVED:
            updated_pregnancy = await pregnancy_service.archive_pregnancy(session, pregnancy_id)
        elif new_status == PregnancyStatus.COMPLETED:
            updated_pregnancy = await pregnancy_service.complete_pregnancy(session, pregnancy_id)
        else:
            updated_pregnancy = await pregnancy_service.update_pregnancy(
                session, pregnancy_id, {"status": new_status}
            )
        
        if not updated_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pregnancy status"
            )
        
        return PregnancyResponse.from_orm(updated_pregnancy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pregnancy status: {str(e)}"
        )