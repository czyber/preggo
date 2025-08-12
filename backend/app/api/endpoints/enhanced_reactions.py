"""
Enhanced Reactions API endpoints with optimized performance.

This module provides endpoints for:
- Enhanced pregnancy-specific reactions with intensity levels 1-3
- Sub-50ms optimistic reaction processing
- Family warmth calculation and integration
- Milestone-specific reactions with special triggers
- Real-time reaction broadcasting
- Client-side deduplication support
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime, timedelta
import uuid

from app.core.supabase import get_current_active_user
from app.services.enhanced_reaction_service import enhanced_reaction_service
from app.services.realtime_websocket_service import realtime_websocket_service
from app.services.post_service import post_service
from app.services.threaded_comment_service import threaded_comment_service
from app.db.session import get_session
from app.models.content import ReactionType, Post, Comment
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reactions", tags=["enhanced_reactions"])


@router.post("/optimistic", response_model=Dict[str, Any])
async def add_optimistic_reaction(
    reaction_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session),
    response: Response = Response()
):
    """
    Add reaction with optimistic updates for sub-50ms response.
    
    Optimized for Instagram-like immediate feedback with:
    - Client-side deduplication via client_id
    - Minimal validation for speed
    - Background processing for family warmth calculations
    - Real-time activity broadcasting
    """
    start_time = datetime.utcnow()
    
    try:
        user_id = current_user["sub"]
        
        # Extract and validate request data
        post_id = reaction_data.get("post_id")
        comment_id = reaction_data.get("comment_id")
        reaction_type_str = reaction_data.get("reaction_type", "love")
        intensity = reaction_data.get("intensity", 2)
        custom_message = reaction_data.get("custom_message")
        is_milestone_reaction = reaction_data.get("is_milestone_reaction", False)
        client_id = reaction_data.get("client_id", str(uuid.uuid4()))
        client_timestamp_str = reaction_data.get("client_timestamp")
        
        # Parse client timestamp
        client_timestamp = None
        if client_timestamp_str:
            try:
                client_timestamp = datetime.fromisoformat(client_timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                client_timestamp = datetime.utcnow()
        
        # Validate required fields
        if not post_id and not comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or comment_id must be provided"
            )
        
        if post_id and comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot react to both post and comment simultaneously"
            )
        
        # Validate and convert reaction type
        try:
            reaction_type = ReactionType(reaction_type_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reaction type: {reaction_type_str}. Must be one of: {[r.value for r in ReactionType]}"
            )
        
        # Validate intensity
        if intensity < 1 or intensity > 3:
            intensity = 2  # Default to medium intensity
        
        # Quick access validation (simplified for speed)
        if post_id:
            # Basic post existence check
            post = session.get(Post, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="Post not found")
            pregnancy_id = post.pregnancy_id
        else:
            # Basic comment existence check
            comment = session.get(Comment, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            post = session.get(Post, comment.post_id)
            pregnancy_id = post.pregnancy_id if post else None
        
        # Add optimistic reaction
        reaction, performance_metrics = await enhanced_reaction_service.add_optimistic_reaction(
            session=session,
            user_id=user_id,
            post_id=post_id,
            comment_id=comment_id,
            reaction_type=reaction_type,
            intensity=intensity,
            custom_message=custom_message,
            is_milestone_reaction=is_milestone_reaction,
            client_id=client_id,
            client_timestamp=client_timestamp
        )
        
        if not reaction:
            error_msg = performance_metrics.get("error", "Failed to add reaction")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Get updated reaction summary
        reaction_summary = await enhanced_reaction_service.get_enhanced_reaction_summary(
            session=session,
            post_id=post_id,
            comment_id=comment_id,
            user_id=user_id
        )
        
        # Broadcast real-time update if pregnancy_id is available
        if pregnancy_id and performance_metrics.get("background_queued", False):
            await realtime_websocket_service.broadcast_reaction_update(
                pregnancy_id=pregnancy_id,
                reaction_data={
                    "action": "add",
                    "reaction_id": reaction.id,
                    "user_id": user_id,
                    "post_id": post_id,
                    "comment_id": comment_id,
                    "reaction_type": reaction_type.value,
                    "intensity": intensity,
                    "is_milestone": is_milestone_reaction,
                    "family_warmth_delta": reaction.family_warmth_contribution,
                    "updated_summary": reaction_summary,
                    "timestamp": reaction.created_at.isoformat()
                },
                exclude_user=user_id
            )
        
        # Set performance headers
        response.headers["X-Reaction-Latency"] = f"{performance_metrics.get('latency_ms', 0):.1f}ms"
        response.headers["X-Optimistic"] = str(performance_metrics.get('optimistic', True)).lower()
        
        # Build response
        response_data = {
            "success": True,
            "reaction_id": reaction.id,
            "reaction_type": reaction_type.value,
            "intensity": intensity,
            "family_warmth_delta": reaction.family_warmth_contribution,
            "updated_counts": reaction_summary.get("reaction_counts", {}),
            "total_family_warmth": reaction_summary.get("total_family_warmth", 0.0),
            "client_dedup_id": client_id,
            "performance": {
                "latency_ms": performance_metrics.get("latency_ms", 0),
                "optimistic": performance_metrics.get("optimistic", True),
                "background_queued": performance_metrics.get("background_queued", False)
            },
            "server_timestamp": datetime.utcnow().isoformat()
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        # Fast error response with performance tracking
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.error(f"Error in optimistic reaction (latency: {latency_ms:.1f}ms): {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add optimistic reaction: {str(e)}"
        )


@router.post("/", response_model=Dict[str, Any])
async def add_standard_reaction(
    reaction_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Add reaction with full validation (fallback for non-optimistic clients).
    """
    try:
        user_id = current_user["sub"]
        
        # Extract request data
        post_id = reaction_data.get("post_id")
        comment_id = reaction_data.get("comment_id")
        reaction_type_str = reaction_data.get("reaction_type", "love")
        intensity = reaction_data.get("intensity", 2)
        custom_message = reaction_data.get("custom_message")
        is_milestone_reaction = reaction_data.get("is_milestone_reaction", False)
        
        # Full validation
        if not post_id and not comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or comment_id must be provided"
            )
        
        # Validate reaction type
        try:
            reaction_type = ReactionType(reaction_type_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reaction type: {reaction_type_str}"
            )
        
        # Validate access permissions
        if post_id:
            if not await post_service.user_can_access_post(session, user_id, post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this post"
                )
        
        if comment_id:
            comment = session.get(Comment, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            
            if not await post_service.user_can_access_post(session, user_id, comment.post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this comment's post"
                )
        
        # Add reaction with full processing
        reaction, performance_metrics = await enhanced_reaction_service.add_optimistic_reaction(
            session=session,
            user_id=user_id,
            post_id=post_id,
            comment_id=comment_id,
            reaction_type=reaction_type,
            intensity=intensity,
            custom_message=custom_message,
            is_milestone_reaction=is_milestone_reaction,
            client_id=f"standard_{uuid.uuid4()}"  # Generate client_id for deduplication
        )
        
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction"
            )
        
        # Get complete reaction summary
        reaction_summary = await enhanced_reaction_service.get_enhanced_reaction_summary(
            session=session,
            post_id=post_id,
            comment_id=comment_id,
            user_id=user_id
        )
        
        return {
            "success": True,
            "reaction_id": reaction.id,
            "reaction_summary": reaction_summary,
            "message": "Reaction added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding standard reaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add reaction: {str(e)}"
        )


@router.delete("/{post_or_comment_id}")
async def remove_reaction(
    post_or_comment_id: str,
    target_type: str = "post",  # "post" or "comment"
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove user's reaction from a post or comment."""
    try:
        user_id = current_user["sub"]
        
        # Determine post_id and comment_id
        post_id = post_or_comment_id if target_type == "post" else None
        comment_id = post_or_comment_id if target_type == "comment" else None
        
        # Validate target exists and user has access
        pregnancy_id = None
        if post_id:
            if not await post_service.user_can_access_post(session, user_id, post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this post"
                )
            post = session.get(Post, post_id)
            pregnancy_id = post.pregnancy_id if post else None
            
        elif comment_id:
            comment = session.get(Comment, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            
            if not await post_service.user_can_access_post(session, user_id, comment.post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this comment's post"
                )
            
            post = session.get(Post, comment.post_id)
            pregnancy_id = post.pregnancy_id if post else None
        
        # Remove the reaction
        success = await enhanced_reaction_service.remove_user_reaction(
            session=session,
            user_id=user_id,
            post_id=post_id,
            comment_id=comment_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reaction found to remove"
            )
        
        # Get updated reaction summary
        reaction_summary = await enhanced_reaction_service.get_enhanced_reaction_summary(
            session=session,
            post_id=post_id,
            comment_id=comment_id,
            user_id=user_id
        )
        
        # Broadcast real-time update
        if pregnancy_id:
            await realtime_websocket_service.broadcast_reaction_update(
                pregnancy_id=pregnancy_id,
                reaction_data={
                    "action": "remove",
                    "user_id": user_id,
                    "post_id": post_id,
                    "comment_id": comment_id,
                    "updated_summary": reaction_summary,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )
        
        return {
            "success": True,
            "updated_summary": reaction_summary,
            "message": "Reaction removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing reaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove reaction: {str(e)}"
        )


@router.get("/{post_or_comment_id}/summary")
async def get_reaction_summary(
    post_or_comment_id: str,
    target_type: str = "post",  # "post" or "comment"
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get comprehensive reaction summary for a post or comment."""
    try:
        user_id = current_user["sub"]
        
        # Determine post_id and comment_id
        post_id = post_or_comment_id if target_type == "post" else None
        comment_id = post_or_comment_id if target_type == "comment" else None
        
        # Validate access
        if post_id:
            if not await post_service.user_can_access_post(session, user_id, post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this post"
                )
        elif comment_id:
            comment = session.get(Comment, comment_id)
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")
            
            if not await post_service.user_can_access_post(session, user_id, comment.post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this comment's post"
                )
        
        # Get enhanced reaction summary
        reaction_summary = await enhanced_reaction_service.get_enhanced_reaction_summary(
            session=session,
            post_id=post_id,
            comment_id=comment_id,
            user_id=user_id
        )
        
        return reaction_summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting reaction summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reaction summary: {str(e)}"
        )


@router.get("/family-insights/{pregnancy_id}")
async def get_family_reaction_insights(
    pregnancy_id: str,
    days: int = 7,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get family-wide reaction insights for analytics."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to this pregnancy
        from app.services.pregnancy_service import pregnancy_service
        from app.services.family_service import family_member_service
        
        has_access = False
        
        # Check if user owns the pregnancy
        if await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            has_access = True
        else:
            # Check if user is a family member
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            has_access = len(memberships) > 0
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get family reaction insights
        insights = await enhanced_reaction_service.get_family_reaction_insights(
            session=session,
            pregnancy_id=pregnancy_id,
            days=days
        )
        
        return insights
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting family reaction insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family reaction insights: {str(e)}"
        )


@router.get("/types/available")
async def get_available_reaction_types():
    """Get all available reaction types with their descriptions."""
    reaction_types = [
        {
            "value": "love",
            "display_name": "Love",
            "emoji": "❤️",
            "description": "General love and support",
            "category": "primary",
            "family_warmth_base": 0.12
        },
        {
            "value": "excited",
            "display_name": "Excited",
            "emoji": "😍",
            "description": "Excitement for milestones/moments",
            "category": "primary",
            "family_warmth_base": 0.10
        },
        {
            "value": "supportive",
            "display_name": "Supportive",
            "emoji": "🤗",
            "description": "Caring, nurturing, being there",
            "category": "primary",
            "family_warmth_base": 0.15
        },
        {
            "value": "strong",
            "display_name": "Strong",
            "emoji": "💪",
            "description": "Strength, encouragement, you got this",
            "category": "primary",
            "family_warmth_base": 0.13
        },
        {
            "value": "blessed",
            "display_name": "Blessed",
            "emoji": "✨",
            "description": "Beautiful moments, feeling blessed",
            "category": "primary",
            "family_warmth_base": 0.11
        },
        {
            "value": "happy",
            "display_name": "Happy",
            "emoji": "😂",
            "description": "Joy, laughter, funny moments",
            "category": "additional",
            "family_warmth_base": 0.08
        },
        {
            "value": "grateful",
            "display_name": "Grateful",
            "emoji": "🙏",
            "description": "Gratitude, prayers, thankfulness",
            "category": "additional",
            "family_warmth_base": 0.12
        },
        {
            "value": "celebrating",
            "display_name": "Celebrating",
            "emoji": "🎉",
            "description": "Celebrating achievements/milestones",
            "category": "additional",
            "family_warmth_base": 0.14
        },
        {
            "value": "amazed",
            "display_name": "Amazed",
            "emoji": "🌟",
            "description": "Wonder, awe, amazement at development",
            "category": "additional",
            "family_warmth_base": 0.09
        }
    ]
    
    return {
        "reaction_types": reaction_types,
        "intensity_levels": [
            {"level": 1, "display_name": "Light", "multiplier": 0.5, "description": "Gentle reaction"},
            {"level": 2, "display_name": "Medium", "multiplier": 1.0, "description": "Standard reaction"},
            {"level": 3, "display_name": "Strong", "multiplier": 1.5, "description": "Emphatic reaction"}
        ],
        "milestone_bonus": {
            "celebrating": 1.5,
            "excited": 1.3,
            "supportive": 1.2,
            "amazed": 1.4
        }
    }