"""
Pregnancy management endpoints for CRUD operations and week tracking.

This module provides endpoints for:
- Creating and managing pregnancies
- Week-by-week pregnancy tracking
- Pregnancy details and updates
- Partner management and sharing
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.core.supabase import get_current_active_user
from app.services import pregnancy_service, get_session_dependency
from app.db.session import get_session
from sqlmodel import Session
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
    
    Args:
        pregnancy_data: Pregnancy creation data including due date and details
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        PregnancyResponse with created pregnancy details
        
    Raises:
        HTTPException: If creation fails or user has too many active pregnancies
    """
    try:
        # Check if user already has active pregnancies (business rule)
        existing_pregnancies = await pregnancy_service.get_active_pregnancies(
            session, 
            current_user["sub"]  # Use 'sub' from JWT token as user_id
        )
        
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
            "user_id": current_user["sub"],  # Use 'sub' from JWT token as user_id
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
    
    Args:
        active_only: Whether to return only active pregnancies
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        List of PregnancyResponse objects
    """
    try:
        if active_only:
            pregnancies = await pregnancy_service.get_active_pregnancies(
                session, 
                current_user["sub"]
            )
        else:
            pregnancies = await pregnancy_service.get_user_pregnancies(
                session, 
                current_user["sub"]
            )
        
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
    
    Args:
        pregnancy_id: UUID of the pregnancy
        current_user: Current authenticated user
        session: Database session
        
    Returns:
        PregnancyResponse with pregnancy details
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, current_user["sub"], pregnancy_id):
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update a pregnancy record.
    
    Args:
        pregnancy_id: UUID of the pregnancy
        pregnancy_update: Fields to update
        current_user: Current authenticated user
        
    Returns:
        PregnancyResponse with updated pregnancy details
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await user_owns_pregnancy(current_user["id"], pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Prepare update data (only include non-None fields)
        update_data = {}
        update_dict = pregnancy_update.dict(exclude_unset=True)
        
        for key, value in update_dict.items():
            if value is not None:
                if key == "pregnancy_details":
                    update_data["pregnancy_details"] = value
                elif key == "preferences":
                    update_data["preferences"] = value
                else:
                    update_data[key] = value
        
        if not update_data:
            # No updates provided, fetch and return current data
            response = supabase_service.client.table('pregnancies').select('*').eq('id', pregnancy_id).execute()
            return PregnancyResponse(**response.data[0])
        
        # Update pregnancy record
        updated_pregnancy = await supabase_service.update_record(
            "pregnancies",
            pregnancy_id,
            update_data
        )
        
        if not updated_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pregnancy"
            )
        
        return PregnancyResponse(**updated_pregnancy)
        
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Calculate current pregnancy week and related information.
    
    Args:
        pregnancy_id: UUID of the pregnancy
        current_user: Current authenticated user
        
    Returns:
        PregnancyWeekCalculation with current week details
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await user_owns_pregnancy(current_user["id"], pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get pregnancy data
        response = supabase_service.client.table('pregnancies').select('pregnancy_details').eq('id', pregnancy_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        pregnancy_details = response.data[0]["pregnancy_details"]
        due_date = datetime.fromisoformat(pregnancy_details["due_date"]).date()
        conception_date = datetime.fromisoformat(pregnancy_details.get("conception_date", 
                                                                      (due_date - timedelta(days=280)).isoformat())).date()
        
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get week-by-week pregnancy journey information.
    
    Args:
        pregnancy_id: UUID of the pregnancy
        week: Specific week to get information for (optional)
        current_user: Current authenticated user
        
    Returns:
        WeeklyJourneyResponse with week-specific pregnancy information
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await user_owns_pregnancy(current_user["id"], pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # If no week specified, calculate current week
        if week is None:
            calc_response = await calculate_pregnancy_week(pregnancy_id, current_user)
            week = calc_response.current_week
        
        # Validate week range
        if week < 0 or week > settings.MAX_PREGNANCY_WEEK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Week must be between 0 and {settings.MAX_PREGNANCY_WEEK}"
            )
        
        # Get weekly update data
        response = supabase_service.client.table('weekly_updates').select('*').eq('pregnancy_id', pregnancy_id).eq('week', week).execute()
        
        if response.data:
            weekly_data = response.data[0]
            
            return WeeklyJourneyResponse(
                pregnancy_id=pregnancy_id,
                current_week=week,
                baby_development={
                    "development": weekly_data.get("baby_development", ""),
                    "size": {
                        "length": weekly_data.get("baby_size_length"),
                        "weight": weekly_data.get("baby_size_weight"),
                        "comparison": weekly_data.get("baby_size_comparison")
                    }
                },
                maternal_changes={
                    "changes": weekly_data.get("maternal_changes", ""),
                    "symptoms": weekly_data.get("common_symptoms", [])
                },
                tips=weekly_data.get("tips", []),
                checklist=[],  # This would come from a separate checklist table
                size_comparison=weekly_data.get("baby_size_comparison"),
                estimated_size={
                    "length_cm": weekly_data.get("baby_size_length"),
                    "weight_grams": weekly_data.get("baby_size_weight")
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Add a partner to the pregnancy.
    
    Args:
        pregnancy_id: UUID of the pregnancy
        partner_id: UUID of the partner to add
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await user_owns_pregnancy(current_user["id"], pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get current pregnancy data
        response = supabase_service.client.table('pregnancies').select('partner_ids').eq('id', pregnancy_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        current_partners = response.data[0].get("partner_ids", [])
        
        # Add partner if not already in the list
        if partner_id not in current_partners:
            current_partners.append(partner_id)
            
            # Update pregnancy record
            await supabase_service.update_record(
                "pregnancies",
                pregnancy_id,
                {"partner_ids": current_partners}
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Remove a partner from the pregnancy.
    
    Args:
        pregnancy_id: UUID of the pregnancy
        partner_id: UUID of the partner to remove
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await user_owns_pregnancy(current_user["id"], pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get current pregnancy data
        response = supabase_service.client.table('pregnancies').select('partner_ids').eq('id', pregnancy_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pregnancy not found"
            )
        
        current_partners = response.data[0].get("partner_ids", [])
        
        # Remove partner if in the list
        if partner_id in current_partners:
            current_partners.remove(partner_id)
            
            # Update pregnancy record
            await supabase_service.update_record(
                "pregnancies",
                pregnancy_id,
                {"partner_ids": current_partners}
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
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update pregnancy status (active, completed, archived).
    
    Args:
        pregnancy_id: UUID of the pregnancy
        new_status: New status for the pregnancy
        current_user: Current authenticated user
        
    Returns:
        Updated pregnancy response
        
    Raises:
        HTTPException: If pregnancy not found or user doesn't have access
    """
    try:
        # Check if user owns this pregnancy
        if not await user_owns_pregnancy(current_user["id"], pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Update pregnancy status
        updated_pregnancy = await supabase_service.update_record(
            "pregnancies",
            pregnancy_id,
            {"status": new_status}
        )
        
        if not updated_pregnancy:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pregnancy status"
            )
        
        return PregnancyResponse(**updated_pregnancy)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update pregnancy status: {str(e)}"
        )