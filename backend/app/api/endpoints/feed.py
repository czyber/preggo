"""
Feed endpoints for family-specific content delivery and engagement.

This module provides endpoints for:
- Family feed with privacy-aware filtering and engagement scoring
- Personal timeline for pregnancy owners
- Real-time reactions with pregnancy-specific types
- Feed filters and analytics
- Celebration and milestone features
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Response
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime, timedelta
import hashlib
import json

from app.core.supabase import get_current_active_user
from app.services.feed_service import feed_service
from app.services.post_service import reaction_service
from app.services.pregnancy_service import pregnancy_service
from app.services.family_service import family_member_service
from app.db.session import get_session
from app.schemas.feed import (
    FeedRequest, FeedResponse, PersonalTimelineResponse,
    ReactionRequest, ReactionResponse, FeedFiltersResponse,
    FeedFilterType, FeedSortType, PregnancyReactionType,
    CelebrationPost, FeedAnalytics
)
from app.models.content import ReactionType

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/family/{pregnancy_id}", response_model=FeedResponse)
async def get_family_feed(
    pregnancy_id: str,
    response: Response,
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    filter_type: FeedFilterType = Query(FeedFilterType.ALL, description="Type of content to show"),
    sort_by: FeedSortType = Query(FeedSortType.CHRONOLOGICAL, description="How to sort the feed"),
    include_reactions: bool = Query(True, description="Include reaction counts and types"),
    include_comments: bool = Query(True, description="Include comment previews"),
    include_media: bool = Query(True, description="Include media metadata"),
    since: Optional[str] = Query(None, description="ISO timestamp - only show posts after this time"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get family feed for a pregnancy with privacy-aware filtering.
    
    Prioritizes:
    - Recent content from family members
    - Milestone posts with celebration features
    - Posts that need family support/responses
    - Pregnancy progression context
    """
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to this pregnancy
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
                detail="You don't have access to this pregnancy feed"
            )
        
        # Parse since timestamp if provided
        since_datetime = None
        if since:
            try:
                from datetime import datetime
                since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid since timestamp format. Use ISO 8601 format."
                )
        
        # Build feed request
        feed_request = FeedRequest(
            limit=limit,
            offset=offset,
            filter_type=filter_type,
            sort_by=sort_by,
            include_reactions=include_reactions,
            include_comments=include_comments,
            include_media=include_media,
            since=since_datetime
        )
        
        # Get the family feed
        feed_response = await feed_service.get_family_feed(
            session, user_id, pregnancy_id, feed_request
        )
        
        # Add caching headers for better performance
        # Cache for 2 minutes for first page, 5 minutes for subsequent pages
        cache_duration = 120 if offset == 0 else 300
        response.headers["Cache-Control"] = f"private, max-age={cache_duration}"
        response.headers["ETag"] = _generate_etag(feed_response, user_id)
        
        return feed_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get family feed: {str(e)}"
        )


@router.get("/personal/{pregnancy_id}", response_model=PersonalTimelineResponse)
async def get_personal_timeline(
    pregnancy_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    filter_type: FeedFilterType = Query(FeedFilterType.ALL, description="Type of content to show"),
    sort_by: FeedSortType = Query(FeedSortType.CHRONOLOGICAL, description="How to sort the timeline"),
    include_reactions: bool = Query(True, description="Include reaction counts and types"),
    include_comments: bool = Query(True, description="Include comment previews"),
    include_media: bool = Query(True, description="Include media metadata"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get personal timeline for pregnancy owner.
    
    Includes:
    - User's own posts with family engagement stats
    - Upcoming milestones and pregnancy progress
    - Personal analytics and insights
    """
    try:
        user_id = current_user["sub"]
        
        # Verify user owns this pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own personal timeline"
            )
        
        # Build feed request
        feed_request = FeedRequest(
            limit=limit,
            offset=offset,
            filter_type=filter_type,
            sort_by=sort_by,
            include_reactions=include_reactions,
            include_comments=include_comments,
            include_media=include_media
        )
        
        # Get personal timeline
        timeline_response = await feed_service.get_personal_timeline(
            session, user_id, pregnancy_id, feed_request
        )
        
        return timeline_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get personal timeline: {str(e)}"
        )


@router.post("/reactions", response_model=ReactionResponse)
async def add_reaction(
    reaction_request: ReactionRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Add or update a reaction to a post or comment.
    
    Supports pregnancy-specific reaction types like 'excited', 'care', 
    'support', 'beautiful', 'praying', 'proud', and 'grateful'.
    """
    try:
        user_id = current_user["sub"]
        
        # Validate that either post_id or comment_id is provided
        if not reaction_request.post_id and not reaction_request.comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or comment_id must be provided"
            )
        
        if reaction_request.post_id and reaction_request.comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot react to both post and comment simultaneously"
            )
        
        # Check access permissions
        if reaction_request.post_id:
            from app.services.post_service import post_service
            if not await post_service.user_can_access_post(session, user_id, reaction_request.post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this post"
                )
        
        if reaction_request.comment_id:
            from app.services.post_service import comment_service
            comment = await comment_service.get_by_id(session, reaction_request.comment_id)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            
            from app.services.post_service import post_service
            if not await post_service.user_can_access_post(session, user_id, comment.post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this comment's post"
                )
        
        # Map pregnancy reaction type to standard reaction type
        # For now, we'll use the existing ReactionType enum
        reaction_type_mapping = {
            PregnancyReactionType.LOVE: ReactionType.LOVE,
            PregnancyReactionType.EXCITED: ReactionType.EXCITED,
            PregnancyReactionType.CARE: ReactionType.CARE,
            PregnancyReactionType.SUPPORT: ReactionType.SUPPORT,
            PregnancyReactionType.BEAUTIFUL: ReactionType.BEAUTIFUL,
            PregnancyReactionType.FUNNY: ReactionType.FUNNY,
            PregnancyReactionType.PRAYING: ReactionType.PRAYING,
            # Map new types to existing ones for now
            PregnancyReactionType.PROUD: ReactionType.SUPPORT,
            PregnancyReactionType.GRATEFUL: ReactionType.PRAYING,
        }
        
        mapped_reaction_type = reaction_type_mapping.get(
            reaction_request.reaction_type, ReactionType.LOVE
        )
        
        # Create reaction data
        reaction_data = {
            "user_id": user_id,
            "type": mapped_reaction_type
        }
        
        if reaction_request.post_id:
            reaction_data["post_id"] = reaction_request.post_id
        if reaction_request.comment_id:
            reaction_data["comment_id"] = reaction_request.comment_id
        
        # Add or update the reaction
        reaction = await reaction_service.add_or_update_reaction(session, reaction_data)
        
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction"
            )
        
        # Get updated reaction counts
        if reaction_request.post_id:
            all_reactions = await reaction_service.get_post_reactions(session, reaction_request.post_id)
        else:
            all_reactions = await reaction_service.get_comment_reactions(session, reaction_request.comment_id)
        
        # Count reactions by type
        updated_counts = {}
        for r in all_reactions:
            updated_counts[r.type] = updated_counts.get(r.type, 0) + 1
        
        return ReactionResponse(
            success=True,
            reaction_id=reaction.id,
            updated_counts=updated_counts,
            message="Reaction added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add reaction: {str(e)}"
        )


@router.delete("/reactions")
async def remove_reaction(
    post_id: Optional[str] = Query(None, description="Post ID to remove reaction from"),
    comment_id: Optional[str] = Query(None, description="Comment ID to remove reaction from"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove user's reaction from a post or comment."""
    try:
        user_id = current_user["sub"]
        
        # Validate parameters
        if not post_id and not comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or comment_id must be provided"
            )
        
        if post_id and comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both post_id and comment_id"
            )
        
        # Check access permissions
        if post_id:
            from app.services.post_service import post_service
            if not await post_service.user_can_access_post(session, user_id, post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this post"
                )
        
        if comment_id:
            from app.services.post_service import comment_service
            comment = await comment_service.get_by_id(session, comment_id)
            if not comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Comment not found"
                )
            
            from app.services.post_service import post_service
            if not await post_service.user_can_access_post(session, user_id, comment.post_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this comment's post"
                )
        
        # Remove the reaction
        success = await reaction_service.remove_reaction(
            session, user_id, post_id=post_id, comment_id=comment_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reaction found to remove"
            )
        
        return {"message": "Reaction removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove reaction: {str(e)}"
        )


@router.get("/filters", response_model=FeedFiltersResponse)
async def get_feed_filters(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get available feed filters and their counts.
    
    Returns filter options based on user's accessible pregnancies
    and family memberships.
    """
    try:
        user_id = current_user["sub"]
        
        # Get user's accessible pregnancies
        user_pregnancies = await pregnancy_service.get_user_pregnancies(session, user_id)
        if not user_pregnancies:
            user_pregnancies = []
        
        # Get user's family memberships
        all_memberships = []
        for pregnancy in user_pregnancies:
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy.id
            )
            if memberships:
                all_memberships.extend(memberships)
        
        # Build available filters with counts
        available_filters = []
        
        # Add basic filter types
        filter_types = [
            {"type": "all", "name": "All Posts", "count": 0, "description": "All accessible posts"},
            {"type": "milestones", "name": "Milestones", "count": 0, "description": "Important pregnancy milestones"},
            {"type": "photos", "name": "Photos", "count": 0, "description": "Belly photos and ultrasounds"},
            {"type": "updates", "name": "Updates", "count": 0, "description": "Weekly updates and appointments"},
            {"type": "celebrations", "name": "Celebrations", "count": 0, "description": "Happy moments and announcements"},
            {"type": "questions", "name": "Questions", "count": 0, "description": "Questions needing family input"},
        ]
        
        # In a full implementation, you would query for actual counts
        # For now, using placeholder counts
        for filter_type in filter_types:
            filter_type["count"] = 10  # Placeholder
            available_filters.append(filter_type)
        
        # Build active pregnancies info
        active_pregnancies = []
        for pregnancy in user_pregnancies:
            try:
                pregnancy_id = getattr(pregnancy, 'id', None)
                if not pregnancy_id:
                    continue
                    
                pregnancy_info = {
                    "id": pregnancy_id,
                    "name": getattr(pregnancy, 'name', f"Pregnancy {pregnancy_id[:8]}"),
                    "current_week": None,  # Would calculate from pregnancy data
                    "due_date": getattr(pregnancy, 'due_date', None).isoformat() if getattr(pregnancy, 'due_date', None) else None,
                    "is_owner": await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id)
                }
                active_pregnancies.append(pregnancy_info)
            except Exception as e:
                # Skip this pregnancy if there's an error
                continue
        
        # Build family groups info
        family_groups = []
        unique_groups = {}
        
        for membership in all_memberships:
            try:
                group_id = getattr(membership, 'group_id', None)
                if group_id and group_id not in unique_groups:
                    # Get family group details
                    from app.services.family_service import family_group_service
                    group = await family_group_service.get_by_id(session, group_id)
                    if group:
                        unique_groups[group_id] = {
                            "id": getattr(group, 'id', group_id),
                            "name": getattr(group, 'name', 'Family Group'),
                            "type": getattr(group, 'type', {}).value if hasattr(getattr(group, 'type', None), 'value') else 'family',
                            "pregnancy_id": getattr(group, 'pregnancy_id', None),
                            "member_count": 0  # Would count actual members
                        }
            except Exception as e:
                # Skip this membership if there's an error
                continue
        
        family_groups = list(unique_groups.values())
        
        # Generate suggested filters based on recent activity
        suggested_filters = ["milestones", "photos"]  # Placeholder
        
        return FeedFiltersResponse(
            available_filters=available_filters,
            active_pregnancies=active_pregnancies,
            family_groups=family_groups,
            suggested_filters=suggested_filters
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feed filters: {str(e)}"
        )


@router.get("/trending/{pregnancy_id}")
async def get_trending_posts(
    pregnancy_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of trending posts to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get trending posts in the family for a pregnancy."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to this pregnancy
        has_access = False
        
        if await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            has_access = True
        else:
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            has_access = len(memberships) > 0
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get trending posts
        trending_post_ids = await feed_service.get_trending_posts(session, pregnancy_id, limit)
        
        return {
            "trending_posts": trending_post_ids,
            "count": len(trending_post_ids),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trending posts: {str(e)}"
        )


@router.get("/celebrations/{pregnancy_id}")
async def get_celebrations(
    pregnancy_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of celebrations to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get recent celebrations for family posts."""
    try:
        user_id = current_user["sub"]
        
        # Verify access
        has_access = False
        
        if await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            has_access = True
        else:
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            has_access = len(memberships) > 0
        
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this pregnancy"
            )
        
        # Get recent celebration-worthy posts
        from app.models.content import PostType
        from app.services.post_service import post_service
        
        celebration_posts = await post_service.get_pregnancy_posts(
            session, pregnancy_id, limit=limit
        )
        
        # Filter for celebration-worthy posts
        celebration_types = [
            PostType.MILESTONE, PostType.ANNOUNCEMENT, 
            PostType.CELEBRATION, PostType.ULTRASOUND
        ]
        
        celebrations = []
        for post in celebration_posts:
            if post.type in celebration_types:
                celebration = CelebrationPost(
                    post_id=post.id,
                    celebration_type=post.type.value,
                    family_reactions=[],  # Would populate with actual reactions
                    celebration_message=f"Celebrating this {post.type.value}!",
                    is_new=(datetime.utcnow() - post.created_at).days < 1
                )
                celebrations.append(celebration)
        
        return {
            "celebrations": celebrations[:limit],
            "count": len(celebrations[:limit])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get celebrations: {str(e)}"
        )


@router.get("/analytics/{pregnancy_id}", response_model=FeedAnalytics)
async def get_feed_analytics(
    pregnancy_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get feed analytics and engagement insights for pregnancy owner."""
    try:
        user_id = current_user["sub"]
        
        # Only pregnancy owner can access analytics
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only pregnancy owner can access feed analytics"
            )
        
        # Get trending posts
        trending_posts = await feed_service.get_trending_posts(session, pregnancy_id)
        
        # Calculate engagement metrics
        # This would involve complex queries in a full implementation
        total_engagement = 42  # Placeholder
        engagement_by_type = {
            "milestone": 15,
            "photo": 12,
            "update": 8,
            "question": 5,
            "celebration": 2
        }
        
        family_activity_score = 85.5  # Placeholder
        
        suggestions = [
            "Share more milestone moments to increase family engagement",
            "Ask questions to encourage family participation",
            "Upload photos from appointments for family to see"
        ]
        
        return FeedAnalytics(
            total_family_engagement=total_engagement,
            trending_posts=trending_posts,
            engagement_by_type=engagement_by_type,
            family_activity_score=family_activity_score,
            suggestions=suggestions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get feed analytics: {str(e)}"
        )


def _generate_etag(data: Any, user_id: str) -> str:
    """Generate ETag for caching based on data and user."""
    content = json.dumps({
        "user_id": user_id,
        "data_hash": hash(str(data)),
        "timestamp": datetime.utcnow().replace(second=0, microsecond=0).isoformat()
    }, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()