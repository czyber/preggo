"""
Family warmth API endpoints for the Preggo app overhaul.
Handles family support visualization and warmth calculation.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_session
from app.services.family_warmth_service import family_warmth_service
from app.models.enhanced_content import FamilyWarmthType, FamilyInteraction
from app.models.content import Post, Comment
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/family-warmth", tags=["family_warmth"])


# Request/Response Models
class FamilyInteractionRequest(BaseModel):
    """Request model for recording family interactions"""
    pregnancy_id: str
    post_id: Optional[str] = None
    interaction_content: str = Field(..., min_length=1, description="Content of the interaction")
    relationship_to_pregnant_person: str = Field(..., description="Relationship (partner, mother, sister, etc.)")
    family_group_level: str = Field(default="immediate", description="Family group level")


class WarmthCalculationRequest(BaseModel):
    """Request model for triggering warmth calculation"""
    pregnancy_id: str
    post_id: Optional[str] = None
    force_recalculate: bool = False


class WarmthVisualizationResponse(BaseModel):
    """Response model for warmth visualization data"""
    overall_warmth_score: float
    warmth_breakdown: Dict[str, float]
    warmth_trend: str
    total_interactions: int
    active_family_members: int
    calculation_period_days: int
    insights: List[str]
    interaction_patterns: Dict[str, Any]
    family_activity: Dict[str, Any]
    calculated_at: str


class FamilyActivityResponse(BaseModel):
    """Response model for family activity summary"""
    recent_interactions: List[Dict[str, Any]]
    most_active_family_members: List[Dict[str, Any]]
    interaction_timeline: List[Dict[str, Any]]
    support_highlights: List[Dict[str, Any]]


# API Endpoints

@router.post("/interactions")
async def record_family_interaction(
    interaction: FamilyInteractionRequest,
    user_id: str = Query(..., description="User ID of family member"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session)
):
    """
    Record a family interaction (comment, reaction, support) for warmth calculation.
    This is called when family members interact with posts.
    """
    try:
        # Record the family interaction
        family_interaction = family_warmth_service.record_family_interaction(
            session=session,
            post_id=interaction.post_id,
            pregnancy_id=interaction.pregnancy_id,
            user_id=user_id,
            interaction_content=interaction.interaction_content,
            relationship=interaction.relationship_to_pregnant_person,
            family_group_level=interaction.family_group_level
        )
        
        if not family_interaction:
            raise HTTPException(status_code=400, detail="Failed to record family interaction")
        
        # Schedule warmth recalculation in background for performance
        background_tasks.add_task(
            recalculate_warmth_background,
            session, interaction.pregnancy_id, interaction.post_id
        )
        
        return {
            "success": True,
            "interaction_id": family_interaction.id,
            "warmth_type": family_interaction.interaction_type.value,
            "warmth_intensity": family_interaction.warmth_intensity,
            "message": "Family interaction recorded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording family interaction: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.get("/summary/{pregnancy_id}", response_model=WarmthVisualizationResponse)
async def get_family_warmth_summary(
    pregnancy_id: str,
    days_back: int = Query(7, ge=1, le=30, description="Days to analyze"),
    session: Session = Depends(get_session)
):
    """
    Get comprehensive family warmth summary for a pregnancy.
    This provides the data needed for family support visualization.
    """
    try:
        warmth_summary = family_warmth_service.get_family_warmth_summary(
            session, pregnancy_id, days_back
        )
        
        if not warmth_summary:
            # Return empty state if no warmth data yet
            return WarmthVisualizationResponse(
                overall_warmth_score=0.0,
                warmth_breakdown={
                    "immediate_family": 0.0,
                    "extended_family": 0.0,
                    "recent_engagement": 0.0,
                    "emotional_support": 0.0
                },
                warmth_trend="stable",
                total_interactions=0,
                active_family_members=0,
                calculation_period_days=days_back,
                insights=["Start sharing updates to build family warmth!"],
                interaction_patterns={},
                family_activity={},
                calculated_at=datetime.utcnow().isoformat()
            )
        
        return WarmthVisualizationResponse(**warmth_summary)
        
    except Exception as e:
        logger.error(f"Error getting family warmth summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get warmth summary")


@router.get("/activity/{pregnancy_id}", response_model=FamilyActivityResponse)
async def get_family_activity(
    pregnancy_id: str,
    days_back: int = Query(7, ge=1, le=30, description="Days to analyze"),
    limit: int = Query(20, ge=5, le=100, description="Number of interactions to return"),
    session: Session = Depends(get_session)
):
    """
    Get detailed family activity information for a pregnancy.
    Shows recent interactions, most active members, and support highlights.
    """
    try:
        from sqlmodel import select, and_, func, desc
        from datetime import timedelta
        from app.models.enhanced_content import FamilyInteraction
        from app.models.user import User
        
        # Get recent interactions
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Query recent interactions with user details
        interaction_query = select(FamilyInteraction, User).join(
            User, FamilyInteraction.user_id == User.id
        ).where(
            and_(
                FamilyInteraction.pregnancy_id == pregnancy_id,
                FamilyInteraction.interaction_at >= cutoff_date
            )
        ).order_by(desc(FamilyInteraction.interaction_at)).limit(limit)
        
        interaction_results = session.exec(interaction_query).all()
        
        # Format recent interactions
        recent_interactions = []
        for interaction, user in interaction_results:
            recent_interactions.append({
                "id": interaction.id,
                "user_name": f"{user.first_name} {user.last_name}",
                "user_id": interaction.user_id,
                "relationship": interaction.relationship_to_pregnant_person,
                "interaction_type": interaction.interaction_type.value,
                "content_preview": interaction.interaction_content[:100] + "..." if len(interaction.interaction_content) > 100 else interaction.interaction_content,
                "warmth_intensity": interaction.warmth_intensity,
                "emotional_sentiment": interaction.emotional_sentiment,
                "interaction_at": interaction.interaction_at.isoformat(),
                "post_id": interaction.post_id
            })
        
        # Get most active family members
        activity_query = select(
            FamilyInteraction.user_id,
            FamilyInteraction.relationship_to_pregnant_person,
            func.count(FamilyInteraction.id).label("interaction_count"),
            func.avg(FamilyInteraction.warmth_intensity).label("avg_warmth")
        ).where(
            and_(
                FamilyInteraction.pregnancy_id == pregnancy_id,
                FamilyInteraction.interaction_at >= cutoff_date
            )
        ).group_by(
            FamilyInteraction.user_id,
            FamilyInteraction.relationship_to_pregnant_person
        ).order_by(desc("interaction_count")).limit(10)
        
        activity_results = session.exec(activity_query).all()
        
        # Get user details for most active members
        most_active_family_members = []
        for result in activity_results:
            user = session.get(User, result.user_id)
            if user:
                most_active_family_members.append({
                    "user_id": result.user_id,
                    "user_name": f"{user.first_name} {user.last_name}",
                    "relationship": result.relationship_to_pregnant_person,
                    "interaction_count": result.interaction_count,
                    "average_warmth": float(result.avg_warmth) if result.avg_warmth else 0.0
                })
        
        # Create interaction timeline (daily activity)
        timeline_query = select(
            func.date(FamilyInteraction.interaction_at).label("interaction_date"),
            func.count(FamilyInteraction.id).label("daily_count"),
            func.avg(FamilyInteraction.warmth_intensity).label("avg_daily_warmth")
        ).where(
            and_(
                FamilyInteraction.pregnancy_id == pregnancy_id,
                FamilyInteraction.interaction_at >= cutoff_date
            )
        ).group_by(func.date(FamilyInteraction.interaction_at)).order_by("interaction_date")
        
        timeline_results = session.exec(timeline_query).all()
        
        interaction_timeline = []
        for result in timeline_results:
            interaction_timeline.append({
                "date": result.interaction_date.isoformat(),
                "interaction_count": result.daily_count,
                "average_warmth": float(result.avg_daily_warmth) if result.avg_daily_warmth else 0.0
            })
        
        # Get support highlights (highest warmth interactions)
        highlight_interactions = [
            interaction for interaction in recent_interactions
            if interaction["warmth_intensity"] >= 0.7
        ]
        
        # Sort by warmth and take top 5
        support_highlights = sorted(
            highlight_interactions,
            key=lambda x: x["warmth_intensity"],
            reverse=True
        )[:5]
        
        return FamilyActivityResponse(
            recent_interactions=recent_interactions,
            most_active_family_members=most_active_family_members,
            interaction_timeline=interaction_timeline,
            support_highlights=support_highlights
        )
        
    except Exception as e:
        logger.error(f"Error getting family activity: {e}")
        raise HTTPException(status_code=500, detail="Failed to get family activity")


@router.post("/calculate")
async def trigger_warmth_calculation(
    calculation_request: WarmthCalculationRequest,
    session: Session = Depends(get_session)
):
    """
    Manually trigger warmth calculation for a pregnancy or specific post.
    Useful for updating warmth scores after significant interactions.
    """
    try:
        warmth_calculation = family_warmth_service.calculate_and_store_warmth(
            session=session,
            pregnancy_id=calculation_request.pregnancy_id,
            post_id=calculation_request.post_id,
            force_recalculate=calculation_request.force_recalculate
        )
        
        if not warmth_calculation:
            raise HTTPException(status_code=400, detail="Failed to calculate warmth")
        
        return {
            "success": True,
            "calculation_id": warmth_calculation.id,
            "overall_warmth_score": warmth_calculation.warmth_scores.overall_warmth_score,
            "warmth_trend": warmth_calculation.warmth_scores.warmth_trend,
            "total_interactions": warmth_calculation.total_interactions,
            "calculated_at": warmth_calculation.calculation_date.isoformat(),
            "insights": warmth_calculation.warmth_insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering warmth calculation: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate warmth")


@router.get("/insights/{pregnancy_id}")
async def get_warmth_insights(
    pregnancy_id: str,
    session: Session = Depends(get_session)
):
    """
    Get actionable insights about family warmth and suggestions for improvement.
    """
    try:
        warmth_summary = family_warmth_service.get_family_warmth_summary(
            session, pregnancy_id, 7
        )
        
        if not warmth_summary:
            return {
                "insights": ["Start sharing updates to build family warmth!"],
                "suggestions": [
                    "Share a belly photo to get family excited",
                    "Post about how you're feeling",
                    "Ask family members questions to encourage interaction"
                ],
                "warmth_level": "getting_started"
            }
        
        overall_warmth = warmth_summary.get("overall_warmth_score", 0.0)
        insights = warmth_summary.get("insights", [])
        
        # Generate suggestions based on warmth level
        suggestions = []
        if overall_warmth >= 0.8:
            warmth_level = "amazing"
            suggestions = [
                "Your family love is incredible! Keep sharing these special moments",
                "Consider creating a weekly family update tradition",
                "Your warmth score inspires other families!"
            ]
        elif overall_warmth >= 0.6:
            warmth_level = "strong"
            suggestions = [
                "Great family engagement! Try asking questions to spark more conversation",
                "Share more about your daily experiences",
                "Encourage family members to share their excitement too"
            ]
        elif overall_warmth >= 0.4:
            warmth_level = "growing"
            suggestions = [
                "Your family cares! Share more updates to keep them engaged",
                "Try posting photos - they generate great family responses",
                "Ask specific questions to encourage family participation"
            ]
        else:
            warmth_level = "building"
            suggestions = [
                "Start with simple updates about how you're feeling",
                "Share milestone moments - family loves to celebrate with you",
                "Reach out to family members directly to encourage participation"
            ]
        
        return {
            "insights": insights,
            "suggestions": suggestions,
            "warmth_level": warmth_level,
            "overall_warmth_score": overall_warmth
        }
        
    except Exception as e:
        logger.error(f"Error getting warmth insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")


@router.get("/visualization/{pregnancy_id}")
async def get_warmth_visualization_data(
    pregnancy_id: str,
    session: Session = Depends(get_session)
):
    """
    Get data specifically formatted for warmth visualization components.
    Returns data optimized for frontend visualization needs.
    """
    try:
        warmth_summary = family_warmth_service.get_family_warmth_summary(
            session, pregnancy_id, 7
        )
        
        if not warmth_summary:
            return {
                "visualization_type": "empty_state",
                "message": "Share updates with your family to see warmth visualization",
                "suggested_actions": [
                    "Share how you're feeling today",
                    "Post a belly photo",
                    "Share an exciting milestone"
                ]
            }
        
        overall_warmth = warmth_summary.get("overall_warmth_score", 0.0)
        warmth_breakdown = warmth_summary.get("warmth_breakdown", {})
        
        # Determine visualization type based on warmth level
        if overall_warmth >= 0.8:
            visualization_type = "hearts_flourishing"
            color_scheme = "warm_gold"
        elif overall_warmth >= 0.6:
            visualization_type = "hearts_growing"
            color_scheme = "warm_pink"
        elif overall_warmth >= 0.4:
            visualization_type = "hearts_emerging"
            color_scheme = "soft_pink"
        else:
            visualization_type = "hearts_beginning"
            color_scheme = "gentle_blue"
        
        return {
            "visualization_type": visualization_type,
            "color_scheme": color_scheme,
            "overall_warmth_score": overall_warmth,
            "warmth_segments": [
                {
                    "name": "Immediate Family",
                    "score": warmth_breakdown.get("immediate_family", 0.0),
                    "color": "#FF6B8A",
                    "description": "Partner, parents, siblings"
                },
                {
                    "name": "Extended Family",
                    "score": warmth_breakdown.get("extended_family", 0.0),
                    "color": "#FF8FA3",
                    "description": "Grandparents, aunts, uncles, cousins"
                },
                {
                    "name": "Recent Support",
                    "score": warmth_breakdown.get("recent_engagement", 0.0),
                    "color": "#FFB3C1",
                    "description": "Latest family interactions"
                },
                {
                    "name": "Emotional Support",
                    "score": warmth_breakdown.get("emotional_support", 0.0),
                    "color": "#FFC6D2",
                    "description": "Quality of family emotional support"
                }
            ],
            "trend": warmth_summary.get("warmth_trend", "stable"),
            "active_family_members": warmth_summary.get("active_family_members", 0),
            "recent_highlights": warmth_summary.get("family_activity", {}).get("most_supportive_interactions", [])[:3]
        }
        
    except Exception as e:
        logger.error(f"Error getting warmth visualization data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get visualization data")


# Background task functions

async def recalculate_warmth_background(session: Session, pregnancy_id: str, post_id: Optional[str] = None):
    """
    Background task to recalculate warmth after new interactions.
    """
    try:
        family_warmth_service.calculate_and_store_warmth(
            session, pregnancy_id, post_id, force_recalculate=True
        )
        logger.info(f"Recalculated warmth for pregnancy {pregnancy_id}, post {post_id}")
        
    except Exception as e:
        logger.error(f"Error in warmth recalculation background task: {e}")