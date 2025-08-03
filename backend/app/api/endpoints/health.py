"""
Health endpoints for health tracking, appointments, and measurements.

This module provides endpoints for:
- Health record management and snapshots
- Symptom tracking and trends
- Weight and mood tracking
- Health alerts and notifications
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from datetime import date

from app.core.supabase import get_current_active_user
from app.services.health_service import (
    pregnancy_health_service, health_alert_service,
    symptom_tracking_service, weight_entry_service, mood_entry_service
)
from app.services.pregnancy_service import pregnancy_service
from app.db.session import get_session
from app.schemas.health import (
    PregnancyHealthCreate, PregnancyHealthUpdate, PregnancyHealthResponse,
    HealthAlertCreate, HealthAlertUpdate, HealthAlertResponse,
    SymptomTrackingCreate, SymptomTrackingResponse,
    WeightEntryCreate, WeightEntryResponse,
    MoodEntryCreate, MoodEntryResponse
)

router = APIRouter(prefix="/health", tags=["health"])


# Health Records
@router.post("/", response_model=PregnancyHealthResponse, status_code=status.HTTP_201_CREATED)
async def create_health_record(
    health_data: PregnancyHealthCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new health record for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, health_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Check if health record already exists
        existing = await pregnancy_health_service.get_by_pregnancy_id(session, health_data.pregnancy_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Health record already exists for this pregnancy"
            )
        
        # Create health record
        health_record = health_data.dict()
        created_health = await pregnancy_health_service.create_health_record(
            session, health_data.pregnancy_id, health_record
        )
        
        if not created_health:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create health record"
            )
        
        return PregnancyHealthResponse.from_orm(created_health)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create health record: {str(e)}"
        )


@router.get("/pregnancy/{pregnancy_id}", response_model=PregnancyHealthResponse)
async def get_health_record(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get health record for a pregnancy."""
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
        
        # Get or create health record
        health_record = await pregnancy_health_service.get_or_create_health_record(
            session, pregnancy_id
        )
        
        if not health_record:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get health record"
            )
        
        return PregnancyHealthResponse.from_orm(health_record)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get health record: {str(e)}"
        )


@router.put("/pregnancy/{pregnancy_id}", response_model=PregnancyHealthResponse)
async def update_health_record(
    pregnancy_id: str,
    health_update: PregnancyHealthUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update health record for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Update health record
        update_data = health_update.dict(exclude_unset=True)
        updated_health = await pregnancy_health_service.update_health_record(
            session, pregnancy_id, update_data
        )
        
        if not updated_health:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        return PregnancyHealthResponse.from_orm(updated_health)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update health record: {str(e)}"
        )


# Health Alerts
@router.post("/alerts", response_model=HealthAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_health_alert(
    alert_data: HealthAlertCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new health alert."""
    try:
        user_id = current_user["sub"]
        
        # Get health record to check access
        health_record = await pregnancy_health_service.get_by_id(session, alert_data.pregnancy_health_id)
        if not health_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, health_record.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this health record"
            )
        
        # Create alert
        alert_record = alert_data.dict()
        created_alert = await health_alert_service.create_alert(session, alert_record)
        
        if not created_alert:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create health alert"
            )
        
        return HealthAlertResponse.from_orm(created_alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create health alert: {str(e)}"
        )


@router.get("/alerts/pregnancy/{pregnancy_id}", response_model=List[HealthAlertResponse])
async def get_health_alerts(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get health alerts for a pregnancy."""
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
        
        # Get health record
        health_record = await pregnancy_health_service.get_by_pregnancy_id(session, pregnancy_id)
        if not health_record:
            return []  # No health record means no alerts
        
        # Get active alerts
        alerts = await health_alert_service.get_active_alerts(session, health_record.id)
        return [HealthAlertResponse.from_orm(alert) for alert in alerts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get health alerts: {str(e)}"
        )


@router.put("/alerts/{alert_id}/acknowledge", response_model=HealthAlertResponse)
async def acknowledge_health_alert(
    alert_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Acknowledge a health alert."""
    try:
        user_id = current_user["sub"]
        
        # Get alert to check ownership
        alert = await health_alert_service.get_by_id(session, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health alert not found"
            )
        
        # Get health record to check access
        health_record = await pregnancy_health_service.get_by_id(session, alert.pregnancy_health_id)
        if not health_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, health_record.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this health alert"
            )
        
        # Acknowledge alert
        acknowledged_alert = await health_alert_service.acknowledge_alert(session, alert_id)
        
        if not acknowledged_alert:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to acknowledge health alert"
            )
        
        return HealthAlertResponse.from_orm(acknowledged_alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to acknowledge health alert: {str(e)}"
        )


@router.put("/alerts/{alert_id}/resolve", response_model=HealthAlertResponse)
async def resolve_health_alert(
    alert_id: str,
    alert_update: HealthAlertUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Resolve a health alert."""
    try:
        user_id = current_user["sub"]
        
        # Get alert to check ownership
        alert = await health_alert_service.get_by_id(session, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health alert not found"
            )
        
        # Get health record to check access
        health_record = await pregnancy_health_service.get_by_id(session, alert.pregnancy_health_id)
        if not health_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Health record not found"
            )
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, health_record.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this health alert"
            )
        
        # Resolve alert
        resolved_alert = await health_alert_service.resolve_alert(
            session, alert_id, alert_update.resolution_notes
        )
        
        if not resolved_alert:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resolve health alert"
            )
        
        return HealthAlertResponse.from_orm(resolved_alert)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve health alert: {str(e)}"
        )


# Symptom Tracking
@router.post("/symptoms", response_model=SymptomTrackingResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom_entry(
    symptom_data: SymptomTrackingCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new symptom tracking entry."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, symptom_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create symptom entry
        symptom_record = symptom_data.dict()
        created_symptom = await symptom_tracking_service.create_symptom_entry(session, symptom_record)
        
        if not created_symptom:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create symptom entry"
            )
        
        return SymptomTrackingResponse.from_orm(created_symptom)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create symptom entry: {str(e)}"
        )


@router.get("/symptoms/pregnancy/{pregnancy_id}", response_model=List[SymptomTrackingResponse])
async def get_pregnancy_symptoms(
    pregnancy_id: str,
    days_back: Optional[int] = Query(30, description="Number of days to look back"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get symptom tracking entries for a pregnancy."""
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
        
        symptoms = await symptom_tracking_service.get_pregnancy_symptoms(
            session, pregnancy_id, days_back
        )
        return [SymptomTrackingResponse.from_orm(symptom) for symptom in symptoms]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get symptoms: {str(e)}"
        )


@router.get("/symptoms/pregnancy/{pregnancy_id}/trends/{symptom_name}", response_model=List[SymptomTrackingResponse])
async def get_symptom_trends(
    pregnancy_id: str,
    symptom_name: str,
    weeks_back: int = Query(4, description="Number of weeks to look back"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get trend data for a specific symptom."""
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
        
        trends = await symptom_tracking_service.get_symptom_trends(
            session, pregnancy_id, symptom_name, weeks_back
        )
        return [SymptomTrackingResponse.from_orm(trend) for trend in trends]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get symptom trends: {str(e)}"
        )


# Weight Tracking
@router.post("/weight", response_model=WeightEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_weight_entry(
    weight_data: WeightEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new weight tracking entry."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, weight_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Ensure recorded_by matches current user
        weight_record = weight_data.dict()
        weight_record["recorded_by"] = user_id
        
        created_weight = await weight_entry_service.create_weight_entry(session, weight_record)
        
        if not created_weight:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create weight entry"
            )
        
        return WeightEntryResponse.from_orm(created_weight)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create weight entry: {str(e)}"
        )


@router.get("/weight/pregnancy/{pregnancy_id}", response_model=List[WeightEntryResponse])
async def get_pregnancy_weights(
    pregnancy_id: str,
    limit: Optional[int] = Query(20, description="Number of entries to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get weight tracking entries for a pregnancy."""
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
        
        weights = await weight_entry_service.get_pregnancy_weights(session, pregnancy_id, limit)
        return [WeightEntryResponse.from_orm(weight) for weight in weights]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get weight entries: {str(e)}"
        )


# Mood Tracking
@router.post("/mood", response_model=MoodEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_mood_entry(
    mood_data: MoodEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new mood tracking entry."""
    try:
        user_id = current_user["sub"]
        
        # Verify user owns the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, mood_data.pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Create mood entry
        mood_record = mood_data.dict()
        created_mood = await mood_entry_service.create_mood_entry(session, mood_record)
        
        if not created_mood:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create mood entry"
            )
        
        return MoodEntryResponse.from_orm(created_mood)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create mood entry: {str(e)}"
        )


@router.get("/mood/pregnancy/{pregnancy_id}", response_model=List[MoodEntryResponse])
async def get_pregnancy_moods(
    pregnancy_id: str,
    days_back: Optional[int] = Query(30, description="Number of days to look back"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get mood tracking entries for a pregnancy."""
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
        
        moods = await mood_entry_service.get_pregnancy_moods(session, pregnancy_id, days_back)
        return [MoodEntryResponse.from_orm(mood) for mood in moods]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mood entries: {str(e)}"
        )