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
    FeedRequest, FeedResponse, PersonalTimelineResponse, FeedCursor, FamilyContext,
    ReactionRequest, ReactionResponse, OptimisticReactionRequest, OptimisticReactionResponse,
    FeedFiltersResponse, FeedFilterType, FeedSortType, PregnancyReactionType,
    CelebrationPost, FeedAnalytics
)
from app.models.content import ReactionType

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/family/{pregnancy_id}", response_model=FeedResponse)
async def get_family_feed(
    pregnancy_id: str,
    response: Response,
    limit: int = Query(20, ge=1, le=50, description="Number of posts to return"),
    cursor: Optional[str] = Query(None, description="Cursor for pagination (replaces offset)"),
    filter_type: FeedFilterType = Query(FeedFilterType.ALL, description="Type of content to show"),
    sort_by: FeedSortType = Query(FeedSortType.CHRONOLOGICAL, description="How to sort the feed"),
    include_reactions: bool = Query(True, description="Include reaction counts and types"),
    include_comments: bool = Query(True, description="Include comment previews"),
    include_media: bool = Query(True, description="Include media metadata"),
    include_content: bool = Query(False, description="Include integrated pregnancy content"),
    include_warmth: bool = Query(True, description="Include family warmth visualizations"),
    real_time: bool = Query(False, description="Enable real-time updates via WebSocket upgrade"),
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
        
        # Parse cursor if provided
        cursor_obj = None
        if cursor:
            try:
                cursor_obj = FeedCursor.decode(cursor)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid cursor: {str(e)}"
                )
        
        # Build enhanced feed request
        feed_request = FeedRequest(
            limit=limit,
            cursor=cursor,
            filter_type=filter_type,
            sort_by=sort_by,
            include_reactions=include_reactions,
            include_comments=include_comments,
            include_media=include_media,
            include_content=include_content,
            include_warmth=include_warmth,
            real_time=real_time,
            since=since_datetime
        )
        
        # Get the enhanced family feed with Instagram-like features
        feed_response = await feed_service.get_instagram_like_family_feed(
            session, user_id, pregnancy_id, feed_request
        )
        
        # Add family context for Instagram-like experience
        family_context = await _get_family_context(session, pregnancy_id)
        feed_response.family_context = family_context
        
        # Generate WebSocket token if real-time is requested
        if real_time:
            feed_response.real_time_token = f"wss://api.preggo.com/ws/feed/{pregnancy_id}?token={_generate_ws_token(user_id)}"
        
        # Add performance-optimized caching headers
        # Shorter cache for cursor-based pagination to ensure real-time feel
        cache_duration = 60 if not cursor else 120  # 1-2 minutes
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


@router.get("/integrated/{pregnancy_id}")
async def get_integrated_feed(
    pregnancy_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of feed items to return"),
    include_content: bool = Query(True, description="Include pregnancy content cards"),
    include_warmth: bool = Query(True, description="Include family warmth data"),
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
    """
    Get integrated feed combining posts with pregnancy content for StoryCard format.
    This endpoint is optimized for the new feed redesign with content integration.
    """
    try:
        from app.services.content_service import content_service
        from app.services.family_warmth_service import family_warmth_service
        from app.services.memory_book_service import memory_book_service
        from app.models.content import Post, PostType
        from app.models.pregnancy import Pregnancy
        from sqlmodel import select, desc
        
        # Verify pregnancy exists and user has access (simplified for now)
        pregnancy = session.get(Pregnancy, pregnancy_id)
        if not pregnancy:
            raise HTTPException(status_code=404, detail="Pregnancy not found")
        
        # Get recent posts
        posts_query = select(Post).where(
            Post.pregnancy_id == pregnancy_id
        ).order_by(desc(Post.created_at)).limit(limit // 2)
        
        posts = list(session.exec(posts_query).all())
        
        # Get personalized content if requested
        personalized_content = []
        if include_content:
            personalized_content = content_service.get_personalized_feed_content(
                session, user_id, pregnancy_id, limit // 2
            )
        
        # Build integrated feed items
        feed_items = []
        
        # Add posts as StoryCard items
        for post in posts:
            # Get family warmth data if requested
            warmth_data = None
            if include_warmth and post.family_warmth_score > 0:
                warmth_data = {
                    "overall_score": post.family_warmth_score,
                    "visualization_type": "hearts_growing" if post.family_warmth_score > 0.6 else "hearts_emerging"
                }
            
            # Check if post is memory-eligible
            memory_eligible = post.memory_book_eligible
            memory_priority = post.memory_book_priority
            
            # Build pregnancy context
            current_week = pregnancy.pregnancy_details.current_week if pregnancy.pregnancy_details else None
            pregnancy_context = None
            if current_week:
                pregnancy_context = {
                    "week_number": current_week,
                    "trimester": 1 if current_week <= 13 else (2 if current_week <= 27 else 3),
                    "is_milestone_week": current_week in [12, 20, 28, 37],  # Example milestone weeks
                    "development_highlight": None,  # Would get from baby development content
                    "size_comparison": None  # Would get from baby development content
                }
            
            feed_item = {
                "id": post.id,
                "type": "user_post",
                "story_card_type": "pregnancy_moment",
                "content": {
                    "title": post.content.title,
                    "text": post.content.text,
                    "post_type": post.type.value,
                    "mood": post.content.mood.value if post.content.mood else None,
                    "week": post.content.week,
                    "tags": post.content.tags
                },
                "pregnancy_context": pregnancy_context,
                "family_warmth": warmth_data,
                "memory_book": {
                    "eligible": memory_eligible,
                    "priority": memory_priority,
                    "auto_curate": memory_priority > 0.7
                } if memory_eligible else None,
                "emotional_context": post.emotional_context,
                "celebration_data": post.celebration_trigger_data,
                "engagement": {
                    "reaction_count": post.reaction_count,
                    "comment_count": post.comment_count,
                    "view_count": post.view_count
                },
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat()
            }
            
            feed_items.append(feed_item)
        
        # Add personalized content as StoryCard items
        for content_item in personalized_content:
            feed_item = {
                "id": content_item.get("id"),
                "type": "pregnancy_content",
                "story_card_type": "educational_tip" if content_item.get("content_type") == "weekly_tip" else "development_info",
                "content": {
                    "title": content_item.get("title"),
                    "subtitle": content_item.get("subtitle"),
                    "text": content_item.get("content"),
                    "content_summary": content_item.get("content_summary"),
                    "content_type": content_item.get("content_type"),
                    "reading_time_minutes": content_item.get("reading_time_minutes"),
                    "featured_image": content_item.get("featured_image"),
                    "tags": content_item.get("tags", [])
                },
                "pregnancy_context": {
                    "week_number": content_item.get("week_number"),
                    "trimester": content_item.get("trimester"),
                    "personalization_score": content_item.get("personalization_score", 0.0)
                },
                "interaction_prompts": {
                    "can_save_to_memory": True,
                    "can_share_with_family": True,
                    "feedback_options": ["helpful", "not_helpful", "saved"]
                },
                "created_at": datetime.utcnow().isoformat()
            }
            
            feed_items.append(feed_item)
        
        # Sort integrated feed by relevance and recency
        feed_items.sort(key=lambda x: (
            x.get("pregnancy_context", {}).get("personalization_score", 0.0) if x["type"] == "pregnancy_content" else 0.5,
            x["created_at"]
        ), reverse=True)
        
        return {
            "pregnancy_id": pregnancy_id,
            "feed_items": feed_items[:limit],
            "total_count": len(feed_items[:limit]),
            "has_more": len(posts) + len(personalized_content) > limit,
            "integration_features": {
                "content_included": include_content,
                "warmth_included": include_warmth,
                "memory_prompts_enabled": True
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting integrated feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get integrated feed")


@router.get("/story-cards/{pregnancy_id}")
async def get_story_card_feed(
    pregnancy_id: str,
    limit: int = Query(15, ge=5, le=30, description="Number of story cards to return"),
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
    """
    Get feed optimized specifically for StoryCard UI components.
    Returns a mix of user posts and pregnancy content formatted for story card display.
    """
    try:
        from app.services.content_service import content_service
        from app.services.family_warmth_service import family_warmth_service
        from app.models.pregnancy import Pregnancy
        
        # Verify pregnancy exists
        pregnancy = session.get(Pregnancy, pregnancy_id)
        if not pregnancy:
            raise HTTPException(status_code=404, detail="Pregnancy not found")
        
        current_week = pregnancy.pregnancy_details.current_week if pregnancy.pregnancy_details else 1
        
        # Get story cards from multiple sources
        story_cards = []
        
        # 1. Weekly pregnancy content card (always first if available)
        weekly_content = content_service.get_weekly_pregnancy_content(
            session, user_id, pregnancy_id, current_week
        )
        
        if weekly_content and weekly_content.get("baby_development"):
            development = weekly_content["baby_development"]
            story_cards.append({
                "id": f"weekly_development_{current_week}",
                "type": "baby_development",
                "priority": 10,  # High priority
                "content": {
                    "title": f"Week {current_week}: Your Baby This Week",
                    "subtitle": development.get("size_comparison", ""),
                    "amazing_fact": development.get("amazing_fact", ""),
                    "connection_moment": development.get("connection_moment", ""),
                    "size_comparison": development.get("size_comparison"),
                    "size_comparison_image": development.get("size_comparison_image"),
                    "major_developments": development.get("major_developments", []),
                    "what_baby_can_do": development.get("what_baby_can_do", "")
                },
                "pregnancy_context": {
                    "week_number": current_week,
                    "trimester": weekly_content.get("trimester"),
                    "is_development_highlight": True
                },
                "interaction_prompts": {
                    "share_with_family": True,
                    "save_to_memory": True,
                    "start_conversation": True
                }
            })
        
        # 2. Recent posts as story cards
        from sqlmodel import select, desc
        from app.models.content import Post
        
        recent_posts_query = select(Post).where(
            Post.pregnancy_id == pregnancy_id
        ).order_by(desc(Post.created_at)).limit(8)
        
        recent_posts = list(session.exec(recent_posts_query).all())
        
        for post in recent_posts:
            story_card = {
                "id": post.id,
                "type": "user_moment",
                "priority": 5 + post.family_warmth_score * 5,  # Priority based on family warmth
                "content": {
                    "title": post.content.title or f"{post.type.value.title()} Moment",
                    "text": post.content.text,
                    "mood": post.content.mood.value if post.content.mood else None,
                    "post_type": post.type.value,
                    "tags": post.content.tags
                },
                "family_warmth": {
                    "score": post.family_warmth_score,
                    "visualization": "hearts_growing" if post.family_warmth_score > 0.6 else "hearts_emerging"
                } if post.family_warmth_score > 0 else None,
                "memory_book": {
                    "eligible": post.memory_book_eligible,
                    "priority": post.memory_book_priority
                } if post.memory_book_eligible else None,
                "created_at": post.created_at.isoformat()
            }
            story_cards.append(story_card)
        
        # 3. Personalized tips as story cards
        personalized_tips = content_service.get_personalized_feed_content(
            session, user_id, pregnancy_id, 5
        )
        
        for tip in personalized_tips:
            if tip.get("content_type") in ["weekly_tip", "emotional_support", "health_wellness"]:
                story_cards.append({
                    "id": tip["id"],
                    "type": "pregnancy_tip",
                    "priority": tip.get("personalization_score", 0.5) * 10,
                    "content": {
                        "title": tip["title"],
                        "subtitle": tip.get("subtitle"),
                        "text": tip["content"],
                        "tip_type": tip["content_type"],
                        "reading_time": tip.get("reading_time_minutes"),
                        "featured_image": tip.get("featured_image")
                    },
                    "interaction_prompts": {
                        "mark_helpful": True,
                        "save_to_memory": True,
                        "share_with_family": True
                    }
                })
        
        # 4. Family warmth summary card (if there's recent activity)
        warmth_summary = family_warmth_service.get_family_warmth_summary(
            session, pregnancy_id, 7
        )
        
        if warmth_summary and warmth_summary.get("overall_warmth_score", 0) > 0.3:
            story_cards.append({
                "id": f"warmth_summary_{pregnancy_id}",
                "type": "family_warmth_summary",
                "priority": 8,
                "content": {
                    "title": "Your Family's Love",
                    "subtitle": f"Family warmth score: {warmth_summary['overall_warmth_score']:.1%}",
                    "insights": warmth_summary.get("insights", [])[:2],
                    "active_family_members": warmth_summary.get("active_family_members", 0),
                    "recent_highlights": warmth_summary.get("family_activity", {}).get("most_supportive_interactions", [])[:1]
                },
                "visualization_data": {
                    "warmth_score": warmth_summary["overall_warmth_score"],
                    "warmth_breakdown": warmth_summary.get("warmth_breakdown", {}),
                    "trend": warmth_summary.get("warmth_trend", "stable")
                }
            })
        
        # Sort by priority and limit results
        story_cards.sort(key=lambda x: x["priority"], reverse=True)
        final_story_cards = story_cards[:limit]
        
        return {
            "pregnancy_id": pregnancy_id,
            "story_cards": final_story_cards,
            "total_count": len(final_story_cards),
            "current_week": current_week,
            "card_types_included": list(set(card["type"] for card in final_story_cards)),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting story card feed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get story card feed")


def _generate_etag(data: Any, user_id: str) -> str:
    """Generate ETag for caching based on data and user."""
    content = json.dumps({
        "user_id": user_id,
        "data_hash": hash(str(data)),
        "timestamp": datetime.utcnow().replace(second=0, microsecond=0).isoformat()
    }, sort_keys=True)
    return hashlib.md5(content.encode()).hexdigest()


async def _get_family_context(session: Session, pregnancy_id: str) -> FamilyContext:
    """Get family context information for Instagram-like feed."""
    try:
        from app.services.family_warmth_service import family_warmth_service
        
        # Get family warmth summary for the past 7 days
        warmth_summary = family_warmth_service.get_family_warmth_summary(
            session, pregnancy_id, 7
        )
        
        # Count active family members (simplified)
        active_members = warmth_summary.get("active_family_members", 0) if warmth_summary else 3
        
        # Count recent interactions (simplified)
        recent_interactions = warmth_summary.get("total_interactions", 0) if warmth_summary else 15
        
        # Get overall warmth score
        warmth_score = warmth_summary.get("overall_warmth_score", 0.5) if warmth_summary else 0.5
        
        return FamilyContext(
            active_members=active_members,
            recent_interactions=recent_interactions,
            warmth_score=warmth_score,
            celebration_count=2  # Placeholder
        )
    except Exception as e:
        # Fallback values if warmth service fails
        return FamilyContext(
            active_members=3,
            recent_interactions=10,
            warmth_score=0.6,
            celebration_count=1
        )


def _generate_ws_token(user_id: str) -> str:
    """Generate WebSocket token for real-time features."""
    # In production, this would be a proper JWT or session token
    import secrets
    import base64
    token_data = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "nonce": secrets.token_hex(16)
    }
    token_json = json.dumps(token_data, sort_keys=True)
    return base64.b64encode(token_json.encode()).decode()


@router.post("/reactions/optimistic", response_model=OptimisticReactionResponse)
async def add_optimistic_reaction(
    reaction_request: OptimisticReactionRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Add reaction with optimistic updates and sub-50ms response target.
    
    Optimized for Instagram-like immediate feedback with:
    - Client-side deduplication via client_id
    - Minimal validation for speed
    - Background processing for family warmth calculations
    - Real-time activity broadcasting
    """
    start_time = datetime.utcnow()
    
    try:
        user_id = current_user["sub"]
        
        # Fast validation - minimal checks for sub-50ms response
        if not reaction_request.post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="post_id is required for optimistic reactions"
            )
        
        # Check for duplicate client_id to prevent double reactions
        from sqlmodel import select
        from app.models.content import Reaction
        
        existing_reaction_query = select(Reaction).where(
            Reaction.client_id == reaction_request.client_id,
            Reaction.created_at >= start_time - timedelta(minutes=5)  # 5-minute dedup window
        )
        existing_reaction = session.exec(existing_reaction_query).first()
        
        if existing_reaction:
            # Return existing reaction to prevent duplicates
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            return OptimisticReactionResponse(
                success=True,
                reaction_id=existing_reaction.id,
                optimistic=False,  # Already processed
                updated_counts={reaction_request.reaction_type: 1},
                family_warmth_delta=0.0,
                latency_ms=latency_ms,
                client_dedup_id=reaction_request.client_id,
                broadcast_queued=False
            )
        
        # Map pregnancy reaction type to standard reaction type
        reaction_type_mapping = {
            PregnancyReactionType.LOVE: ReactionType.LOVE,
            PregnancyReactionType.EXCITED: ReactionType.EXCITED,
            PregnancyReactionType.CARE: ReactionType.CARE,
            PregnancyReactionType.SUPPORT: ReactionType.SUPPORT,
            PregnancyReactionType.BEAUTIFUL: ReactionType.BEAUTIFUL,
            PregnancyReactionType.FUNNY: ReactionType.FUNNY,
            PregnancyReactionType.PRAYING: ReactionType.PRAYING,
            PregnancyReactionType.PROUD: ReactionType.SUPPORT,  # Map to existing
            PregnancyReactionType.GRATEFUL: ReactionType.PRAYING,  # Map to existing
        }
        
        mapped_reaction_type = reaction_type_mapping.get(
            reaction_request.reaction_type, ReactionType.LOVE
        )
        
        # Calculate family warmth contribution based on intensity and reaction type
        base_warmth_values = {
            ReactionType.LOVE: 0.1,
            ReactionType.EXCITED: 0.08,
            ReactionType.CARE: 0.12,
            ReactionType.SUPPORT: 0.15,
            ReactionType.BEAUTIFUL: 0.08,
            ReactionType.FUNNY: 0.05,
            ReactionType.PRAYING: 0.12,
        }
        
        base_warmth = base_warmth_values.get(mapped_reaction_type, 0.05)
        family_warmth_contribution = base_warmth * (reaction_request.intensity / 2.0)
        
        # Create reaction with enhanced fields
        import uuid
        reaction_id = str(uuid.uuid4())
        
        new_reaction = Reaction(
            id=reaction_id,
            user_id=user_id,
            post_id=reaction_request.post_id,
            type=mapped_reaction_type,
            intensity=reaction_request.intensity,
            custom_message=reaction_request.custom_message,
            is_milestone_reaction=reaction_request.is_milestone_reaction,
            family_warmth_contribution=family_warmth_contribution,
            client_id=reaction_request.client_id,
            created_at=datetime.utcnow()
        )
        
        # Fast database insert
        session.add(new_reaction)
        session.commit()
        
        # Queue background tasks for performance (don't wait for them)
        from app.models.content import FeedActivity
        activity = FeedActivity(
            pregnancy_id="",  # Will be populated by background job
            user_id=user_id,
            activity_type="reaction",
            target_id=reaction_request.post_id,
            target_type="post",
            activity_data={
                "reaction_type": reaction_request.reaction_type,
                "intensity": reaction_request.intensity,
                "is_milestone": reaction_request.is_milestone_reaction
            },
            client_timestamp=reaction_request.timestamp,
            broadcast_priority=3 if reaction_request.is_milestone_reaction else 2
        )
        session.add(activity)
        session.commit()
        
        # Calculate response time
        end_time = datetime.utcnow()
        latency_ms = (end_time - start_time).total_seconds() * 1000
        
        # Build optimistic response with minimal data for speed
        updated_counts = {reaction_request.reaction_type: 1}  # Simplified for speed
        
        return OptimisticReactionResponse(
            success=True,
            reaction_id=reaction_id,
            optimistic=True,
            updated_counts=updated_counts,
            family_warmth_delta=family_warmth_contribution,
            latency_ms=latency_ms,
            client_dedup_id=reaction_request.client_id,
            broadcast_queued=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Fast error response
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add optimistic reaction (latency: {latency_ms:.1f}ms): {str(e)}"
        )