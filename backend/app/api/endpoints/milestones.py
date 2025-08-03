"""
Milestone endpoints for tracking pregnancy milestones and celebrations.

This module provides endpoints for:
- Managing pregnancy milestones and celebrations
- Medical appointment tracking and results
- Important date management
- Weekly checklist management
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.core.supabase import get_current_active_user
from app.services.milestone_service import (
    milestone_service, appointment_service, 
    important_date_service, weekly_checklist_service
)
from app.services.pregnancy_service import pregnancy_service
from app.db.session import get_session
from app.schemas.milestone import (
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    AppointmentCreate, AppointmentUpdate, AppointmentResponse,
    ImportantDateCreate, ImportantDateResponse,
    WeeklyChecklistCreate, WeeklyChecklistUpdate, WeeklyChecklistResponse
)

router = APIRouter(prefix="/milestones", tags=["milestones"])


# Milestones
@router.post("/", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    milestone_data: MilestoneCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new milestone."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, milestone_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create milestone
        milestone_record = milestone_data.dict()
        created_milestone = await milestone_service.create_milestone(session, milestone_record)
        
        if not created_milestone:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create milestone"
            )
        
        return MilestoneResponse.from_orm(created_milestone)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create milestone: {str(e)}"
        )


@router.get("/pregnancy/{pregnancy_id}", response_model=List[MilestoneResponse])
async def get_pregnancy_milestones(
    pregnancy_id: str,
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all milestones for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            # Check if user is a family member
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        milestones = await milestone_service.get_pregnancy_milestones(session, pregnancy_id, completed)
        return [MilestoneResponse.from_orm(milestone) for milestone in milestones]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get milestones: {str(e)}"
        )


@router.get("/pregnancy/{pregnancy_id}/week/{week}", response_model=List[MilestoneResponse])
async def get_week_milestones(
    pregnancy_id: str,
    week: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get milestones for a specific pregnancy week."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        milestones = await milestone_service.get_milestones_by_week(session, pregnancy_id, week)
        return [MilestoneResponse.from_orm(milestone) for milestone in milestones]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get week milestones: {str(e)}"
        )


@router.get("/pregnancy/{pregnancy_id}/upcoming", response_model=List[MilestoneResponse])
async def get_upcoming_milestones(
    pregnancy_id: str,
    current_week: int = Query(..., description="Current pregnancy week"),
    weeks_ahead: int = Query(4, description="Number of weeks to look ahead"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get upcoming milestones for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        milestones = await milestone_service.get_upcoming_milestones(
            session, pregnancy_id, current_week, weeks_ahead
        )
        return [MilestoneResponse.from_orm(milestone) for milestone in milestones]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming milestones: {str(e)}"
        )


@router.get("/{milestone_id}", response_model=MilestoneResponse)
async def get_milestone(
    milestone_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get a specific milestone."""
    try:
        user_id = current_user["sub"]
        
        milestone = await milestone_service.get_by_id(session, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, milestone.pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, milestone.pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this milestone"
                )
        
        return MilestoneResponse.from_orm(milestone)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get milestone: {str(e)}"
        )


@router.put("/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: str,
    milestone_update: MilestoneUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a milestone."""
    try:
        user_id = current_user["sub"]
        
        # Get milestone to check ownership
        milestone = await milestone_service.get_by_id(session, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, milestone.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this milestone"
            )
        
        # Update milestone
        update_data = milestone_update.dict(exclude_unset=True)
        updated_milestone = await milestone_service.update_milestone(session, milestone_id, update_data)
        
        if not updated_milestone:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update milestone"
            )
        
        return MilestoneResponse.from_orm(updated_milestone)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update milestone: {str(e)}"
        )


@router.put("/{milestone_id}/complete", response_model=MilestoneResponse)
async def complete_milestone(
    milestone_id: str,
    celebration_post_id: Optional[str] = Query(None, description="ID of celebration post"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Mark a milestone as completed."""
    try:
        user_id = current_user["sub"]
        
        # Get milestone to check ownership
        milestone = await milestone_service.get_by_id(session, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, milestone.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this milestone"
            )
        
        # Complete milestone
        completed_milestone = await milestone_service.complete_milestone(
            session, milestone_id, celebration_post_id
        )
        
        if not completed_milestone:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to complete milestone"
            )
        
        return MilestoneResponse.from_orm(completed_milestone)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete milestone: {str(e)}"
        )


@router.delete("/{milestone_id}")
async def delete_milestone(
    milestone_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete a milestone."""
    try:
        user_id = current_user["sub"]
        
        # Get milestone to check ownership
        milestone = await milestone_service.get_by_id(session, milestone_id)
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Milestone not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, milestone.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this milestone"
            )
        
        await milestone_service.delete(session, milestone)
        return {"message": "Milestone deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete milestone: {str(e)}"
        )


@router.post("/pregnancy/{pregnancy_id}/defaults", response_model=List[MilestoneResponse])
async def create_default_milestones(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create default milestones for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        milestones = await milestone_service.create_default_milestones(session, pregnancy_id)
        return [MilestoneResponse.from_orm(milestone) for milestone in milestones]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create default milestones: {str(e)}"
        )


# Appointments
@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new appointment."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, appointment_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create appointment
        appointment_record = appointment_data.dict()
        created_appointment = await appointment_service.create_appointment(session, appointment_record)
        
        if not created_appointment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create appointment"
            )
        
        return AppointmentResponse.from_orm(created_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment: {str(e)}"
        )


@router.get("/appointments/pregnancy/{pregnancy_id}", response_model=List[AppointmentResponse])
async def get_pregnancy_appointments(
    pregnancy_id: str,
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    future_only: bool = Query(False, description="Only return future appointments"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get appointments for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        appointments = await appointment_service.get_pregnancy_appointments(
            session, pregnancy_id, completed, future_only
        )
        return [AppointmentResponse.from_orm(appointment) for appointment in appointments]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get appointments: {str(e)}"
        )


@router.get("/appointments/pregnancy/{pregnancy_id}/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    pregnancy_id: str,
    days_ahead: int = Query(30, description="Number of days to look ahead"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get upcoming appointments for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        appointments = await appointment_service.get_upcoming_appointments(
            session, pregnancy_id, days_ahead
        )
        return [AppointmentResponse.from_orm(appointment) for appointment in appointments]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get upcoming appointments: {str(e)}"
        )


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    appointment_update: AppointmentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update an appointment."""
    try:
        user_id = current_user["sub"]
        
        # Get appointment to check ownership
        appointment = await appointment_service.get_by_id(session, appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, appointment.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this appointment"
            )
        
        # Update appointment
        update_data = appointment_update.dict(exclude_unset=True)
        updated_appointment = await appointment_service.update_appointment(session, appointment_id, update_data)
        
        if not updated_appointment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update appointment"
            )
        
        return AppointmentResponse.from_orm(updated_appointment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update appointment: {str(e)}"
        )


@router.delete("/appointments/{appointment_id}")    
async def delete_appointment(
    appointment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete an appointment."""
    try:
        user_id = current_user["sub"]
        
        # Get appointment to check ownership
        appointment = await appointment_service.get_by_id(session, appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, appointment.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this appointment"
            )
        
        await appointment_service.delete(session, appointment)
        return {"message": "Appointment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete appointment: {str(e)}"
        )


# Important Dates
@router.post("/important-dates", response_model=ImportantDateResponse, status_code=status.HTTP_201_CREATED)
async def create_important_date(
    date_data: ImportantDateCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new important date."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, date_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create important date
        date_record = date_data.dict()
        created_date = await important_date_service.create_important_date(session, date_record)
        
        if not created_date:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create important date"
            )
        
        return ImportantDateResponse.from_orm(created_date)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create important date: {str(e)}"
        )


@router.get("/important-dates/pregnancy/{pregnancy_id}", response_model=List[ImportantDateResponse])
async def get_pregnancy_important_dates(
    pregnancy_id: str,
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get important dates for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        dates = await important_date_service.get_pregnancy_dates(session, pregnancy_id, category)
        return [ImportantDateResponse.from_orm(date) for date in dates]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get important dates: {str(e)}"
        )


# Weekly Checklists
@router.post("/checklists", response_model=WeeklyChecklistResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist_item(
    checklist_data: WeeklyChecklistCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new checklist item."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, checklist_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create checklist item
        checklist_record = checklist_data.dict()
        created_item = await weekly_checklist_service.create_checklist_item(session, checklist_record)
        
        if not created_item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create checklist item"
            )
        
        return WeeklyChecklistResponse.from_orm(created_item)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checklist item: {str(e)}"
        )


@router.get("/checklists/pregnancy/{pregnancy_id}", response_model=List[WeeklyChecklistResponse])
async def get_pregnancy_checklists(
    pregnancy_id: str,
    week: Optional[int] = Query(None, description="Filter by week"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get checklist items for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        checklists = await weekly_checklist_service.get_pregnancy_checklists(
            session, pregnancy_id, week, completed
        )
        return [WeeklyChecklistResponse.from_orm(checklist) for checklist in checklists]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get checklist items: {str(e)}"
        )


@router.put("/checklists/{checklist_id}", response_model=WeeklyChecklistResponse)
async def update_checklist_item(
    checklist_id: str,
    checklist_update: WeeklyChecklistUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a checklist item."""
    try:
        user_id = current_user["sub"]
        
        # Get checklist item to check ownership
        checklist = await weekly_checklist_service.get_by_id(session, checklist_id)
        if not checklist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Checklist item not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, checklist.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this checklist item"
            )
        
        # Update checklist item
        update_data = checklist_update.dict(exclude_unset=True)
        updated_checklist = await weekly_checklist_service.update_checklist_item(
            session, checklist_id, update_data
        )
        
        if not updated_checklist:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update checklist item"
            )
        
        return WeeklyChecklistResponse.from_orm(updated_checklist)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update checklist item: {str(e)}"
        )


@router.post("/checklists/pregnancy/{pregnancy_id}/defaults", response_model=List[WeeklyChecklistResponse])
async def create_default_checklists(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create default weekly checklists for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        checklists = await weekly_checklist_service.create_default_checklists(session, pregnancy_id)
        return [WeeklyChecklistResponse.from_orm(checklist) for checklist in checklists]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create default checklists: {str(e)}"
        )