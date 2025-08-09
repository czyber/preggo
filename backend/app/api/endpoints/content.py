"""
Content API endpoints for the Preggo app overhaul.
Handles personalized content delivery, weekly tips, and baby development information.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_session
from app.services.content_service import content_service
from app.models.enhanced_content import (
    ContentType, ContentDeliveryMethod, UserContentPreferences,
    PersonalizationContext
)
from app.models.pregnancy import Pregnancy
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["content"])


# Request/Response Models
class ContentInteractionRequest(BaseModel):
    """Request model for recording content interactions"""
    interaction_type: str = Field(..., description="Type of interaction (view, helpful, not_helpful, saved, shared)")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent viewing content")
    save_to_memory: bool = Field(False, description="Whether to save to memory book")
    share_with_family: bool = Field(False, description="Whether content was shared with family")


class ContentPreferencesRequest(BaseModel):
    """Request model for updating content preferences"""
    content_frequency: str = Field("daily", description="Content delivery frequency")
    preferred_delivery_time: str = Field("09:00", description="Preferred delivery time (HH:MM)")
    delivery_methods: List[ContentDeliveryMethod] = Field(default_factory=lambda: [ContentDeliveryMethod.FEED_INTEGRATION])
    preferred_categories: List[str] = Field(default_factory=list)
    blocked_categories: List[str] = Field(default_factory=list)
    detail_level: str = Field("standard", description="Content detail level")
    emotional_tone: str = Field("warm", description="Preferred emotional tone")
    medical_info_level: str = Field("balanced", description="Medical information level")
    family_sharing_level: str = Field("moderate", description="Family sharing encouragement level")
    partner_involvement_level: str = Field("high", description="Partner-focused content level")
    cultural_preferences: Dict[str, Any] = Field(default_factory=dict)
    language_preference: str = Field("en", description="Language preference")


class PersonalizedContentResponse(BaseModel):
    """Response model for personalized content"""
    content: List[Dict[str, Any]]
    personalization_context: Dict[str, Any]
    delivery_timestamp: str
    total_count: int


class WeeklyContentResponse(BaseModel):
    """Response model for weekly content"""
    week_number: int
    trimester: int
    weekly_tips: List[Dict[str, Any]]
    baby_development: Optional[Dict[str, Any]]
    health_guidance: List[Dict[str, Any]]
    emotional_support: List[Dict[str, Any]]
    personalization_context: Dict[str, Any]


# API Endpoints

@router.get("/personalized", response_model=PersonalizedContentResponse)
async def get_personalized_content(
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(5, ge=1, le=20, description="Number of content items to return"),
    session: Session = Depends(get_session)
):
    """
    Get personalized content for the user's current pregnancy stage.
    This is the main endpoint for feed content integration.
    """
    try:
        # Verify pregnancy exists and user has access
        pregnancy = session.get(Pregnancy, pregnancy_id)
        if not pregnancy:
            raise HTTPException(status_code=404, detail="Pregnancy not found")
        
        # Get personalized content
        content = content_service.get_personalized_feed_content(
            session, user_id, pregnancy_id, limit
        )
        
        # Build personalization context for response
        current_week = pregnancy.pregnancy_details.current_week
        trimester = 1 if current_week <= 13 else (2 if current_week <= 27 else 3)
        
        personalization_context = {
            "pregnancy_week": current_week,
            "trimester": trimester,
            "is_high_risk": pregnancy.pregnancy_details.risk_level.value != "low",
            "is_multiple_pregnancy": pregnancy.pregnancy_details.is_multiple
        }
        
        return PersonalizedContentResponse(
            content=content,
            personalization_context=personalization_context,
            delivery_timestamp=datetime.utcnow().isoformat(),
            total_count=len(content)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting personalized content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get personalized content")


@router.get("/weekly/{week_number}", response_model=WeeklyContentResponse)
async def get_weekly_content(
    week_number: int = Field(..., ge=1, le=42, description="Pregnancy week number"),
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
    """
    Get comprehensive content for a specific pregnancy week.
    """
    try:
        # Verify pregnancy exists
        pregnancy = session.get(Pregnancy, pregnancy_id)
        if not pregnancy:
            raise HTTPException(status_code=404, detail="Pregnancy not found")
        
        # Get weekly content
        weekly_content = content_service.get_weekly_pregnancy_content(
            session, user_id, pregnancy_id, week_number
        )
        
        if not weekly_content:
            raise HTTPException(status_code=404, detail="Weekly content not found")
        
        return WeeklyContentResponse(**weekly_content)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting weekly content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weekly content")


@router.post("/{content_id}/interact")
async def record_content_interaction(
    content_id: str,
    interaction: ContentInteractionRequest,
    user_id: str = Query(..., description="User ID"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session)
):
    """
    Record user interaction with content for personalization learning.
    """
    try:
        # Prepare interaction data
        interaction_data = {
            "time_spent": interaction.time_spent_seconds,
            "save_to_memory": interaction.save_to_memory,
            "share_with_family": interaction.share_with_family
        }
        
        # Record interaction (async in background for performance)
        success = content_service.record_content_interaction(
            session, user_id, content_id, interaction.interaction_type, interaction_data
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to record interaction")
        
        # If user found content helpful and wants to save to memory book,
        # trigger memory book curation in the background
        if interaction.save_to_memory and interaction.interaction_type == "helpful":
            background_tasks.add_task(
                trigger_memory_book_curation,
                session, content_id, user_id
            )
        
        return {"success": True, "message": "Interaction recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording content interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.get("/preferences")
async def get_content_preferences(
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
    """
    Get user's content preferences for a specific pregnancy.
    """
    try:
        from sqlmodel import select, and_
        from app.models.enhanced_content import UserContentPreferences
        
        statement = select(UserContentPreferences).where(
            and_(
                UserContentPreferences.user_id == user_id,
                UserContentPreferences.pregnancy_id == pregnancy_id
            )
        )
        preferences = session.exec(statement).first()
        
        if not preferences:
            # Return default preferences
            return {
                "content_frequency": "daily",
                "preferred_delivery_time": "09:00",
                "delivery_methods": ["feed_integration"],
                "preferred_categories": [],
                "blocked_categories": [],
                "detail_level": "standard",
                "emotional_tone": "warm",
                "medical_info_level": "balanced",
                "family_sharing_level": "moderate",
                "partner_involvement_level": "high",
                "cultural_preferences": {},
                "language_preference": "en"
            }
        
        return {
            "content_frequency": preferences.content_frequency,
            "preferred_delivery_time": preferences.preferred_delivery_time,
            "delivery_methods": preferences.delivery_methods,
            "preferred_categories": preferences.preferred_categories,
            "blocked_categories": preferences.blocked_categories,
            "detail_level": preferences.detail_level,
            "emotional_tone": preferences.emotional_tone,
            "medical_info_level": preferences.medical_info_level,
            "family_sharing_level": preferences.family_sharing_level,
            "partner_involvement_level": preferences.partner_involvement_level,
            "cultural_preferences": preferences.cultural_preferences,
            "language_preference": preferences.language_preference
        }
        
    except Exception as e:
        logger.error(f"Error getting content preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")


@router.put("/preferences")
async def update_content_preferences(
    preferences_update: ContentPreferencesRequest,
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
    """
    Update user's content preferences for a specific pregnancy.
    """
    try:
        from sqlmodel import select, and_
        from app.models.enhanced_content import UserContentPreferences
        from datetime import datetime
        
        # Get existing preferences or create new
        statement = select(UserContentPreferences).where(
            and_(
                UserContentPreferences.user_id == user_id,
                UserContentPreferences.pregnancy_id == pregnancy_id
            )
        )
        preferences = session.exec(statement).first()
        
        if preferences:
            # Update existing preferences
            preferences.content_frequency = preferences_update.content_frequency
            preferences.preferred_delivery_time = preferences_update.preferred_delivery_time
            preferences.delivery_methods = preferences_update.delivery_methods
            preferences.preferred_categories = preferences_update.preferred_categories
            preferences.blocked_categories = preferences_update.blocked_categories
            preferences.detail_level = preferences_update.detail_level
            preferences.emotional_tone = preferences_update.emotional_tone
            preferences.medical_info_level = preferences_update.medical_info_level
            preferences.family_sharing_level = preferences_update.family_sharing_level
            preferences.partner_involvement_level = preferences_update.partner_involvement_level
            preferences.cultural_preferences = preferences_update.cultural_preferences
            preferences.language_preference = preferences_update.language_preference
            preferences.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            preferences = UserContentPreferences(
                user_id=user_id,
                pregnancy_id=pregnancy_id,
                **preferences_update.dict()
            )
            session.add(preferences)
        
        session.commit()
        
        return {"success": True, "message": "Preferences updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating content preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")


@router.get("/categories")
async def get_content_categories(
    session: Session = Depends(get_session)
):
    """
    Get all available content categories.
    """
    try:
        from sqlmodel import select
        from app.models.enhanced_content import ContentCategory
        
        statement = select(ContentCategory).where(
            ContentCategory.is_active == True
        ).order_by(ContentCategory.sort_order, ContentCategory.name)
        
        categories = session.exec(statement).all()
        
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "description": cat.description,
                "icon_name": cat.icon_name,
                "color_hex": cat.color_hex,
                "sort_order": cat.sort_order
            }
            for cat in categories
        ]
        
    except Exception as e:
        logger.error(f"Error getting content categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get categories")


@router.get("/baby-development/{week_number}")
async def get_baby_development_content(
    week_number: int = Field(..., ge=1, le=42, description="Pregnancy week number"),
    session: Session = Depends(get_session)
):
    """
    Get detailed baby development information for a specific week.
    """
    try:
        from sqlmodel import select
        from app.models.enhanced_content import BabyDevelopmentContent
        
        statement = select(BabyDevelopmentContent).where(
            BabyDevelopmentContent.week_number == week_number
        )
        development = session.exec(statement).first()
        
        if not development:
            raise HTTPException(status_code=404, detail="Baby development content not found for this week")
        
        return {
            "week_number": development.week_number,
            "size_comparison": development.size_comparison,
            "size_comparison_category": development.size_comparison_category,
            "alternative_comparisons": development.alternative_comparisons,
            "length_mm": development.length_mm,
            "weight_grams": development.weight_grams,
            "major_developments": development.major_developments,
            "sensory_developments": development.sensory_developments,
            "body_system_developments": development.body_system_developments,
            "amazing_fact": development.amazing_fact,
            "connection_moment": development.connection_moment,
            "what_baby_can_do": development.what_baby_can_do,
            "bonding_activities": development.bonding_activities,
            "conversation_starters": development.conversation_starters,
            "illustration_url": development.illustration_url,
            "size_comparison_image": development.size_comparison_image
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting baby development content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get baby development content")


@router.get("/search")
async def search_content(
    query: str = Query(..., min_length=2, description="Search query"),
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    user_id: str = Query(..., description="User ID"),
    content_types: Optional[List[ContentType]] = Query(None, description="Filter by content types"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    session: Session = Depends(get_session)
):
    """
    Search pregnancy content with personalization.
    """
    try:
        from sqlmodel import select, and_, or_, func
        from app.models.enhanced_content import PregnancyContent, MedicalReviewStatus
        
        # Build search query
        base_query = select(PregnancyContent).where(
            and_(
                PregnancyContent.is_active == True,
                PregnancyContent.medical_review_status == MedicalReviewStatus.APPROVED
            )
        )
        
        # Add text search
        search_conditions = [
            PregnancyContent.title.contains(query),
            PregnancyContent.subtitle.contains(query),
            PregnancyContent.content_body.contains(query),
            PregnancyContent.content_summary.contains(query)
        ]
        base_query = base_query.where(or_(*search_conditions))
        
        # Filter by content types if specified
        if content_types:
            base_query = base_query.where(PregnancyContent.content_type.in_(content_types))
        
        # Order by relevance (priority and match quality)
        base_query = base_query.order_by(
            PregnancyContent.priority.desc(),
            PregnancyContent.created_at.desc()
        )
        
        results = session.exec(base_query.limit(limit)).all()
        
        # Format results
        formatted_results = []
        for content in results:
            formatted_results.append({
                "id": content.id,
                "title": content.title,
                "subtitle": content.subtitle,
                "content_summary": content.content_summary,
                "content_type": content.content_type.value,
                "week_number": content.week_number,
                "trimester": content.trimester,
                "reading_time_minutes": content.reading_time_minutes,
                "featured_image": content.featured_image,
                "tags": content.tags,
                "priority": content.priority
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "total_count": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        raise HTTPException(status_code=500, detail="Failed to search content")


# Background task functions

async def trigger_memory_book_curation(session: Session, content_id: str, user_id: str):
    """
    Background task to trigger memory book curation when user saves helpful content.
    """
    try:
        from app.services.memory_book_service import memory_book_service
        
        # This would trigger memory book curation logic
        # For now, we'll just log the action
        logger.info(f"User {user_id} saved content {content_id} - triggering memory book curation")
        
    except Exception as e:
        logger.error(f"Error in memory book curation background task: {e}")