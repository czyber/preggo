"""
Threaded Comments API endpoints with real-time support.

This module provides endpoints for:
- Threaded comments up to 5 levels deep
- Real-time typing indicators via WebSocket
- @mention system with auto-complete
- Comment reactions (subset of main reactions)
- Thread management and navigation
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session
from datetime import datetime
import uuid

from app.core.supabase import get_current_active_user
from app.services.threaded_comment_service import threaded_comment_service
from app.services.enhanced_reaction_service import enhanced_reaction_service
from app.services.realtime_websocket_service import realtime_websocket_service
from app.services.post_service import post_service
from app.db.session import get_session
from app.models.content import Comment, Post
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comments", tags=["threaded_comments"])


@router.post("/", response_model=Dict[str, Any])
async def create_comment(
    comment_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Create a new comment with threading support and @mentions.
    """
    try:
        user_id = current_user["sub"]
        
        # Extract request data
        post_id = comment_data.get("post_id")
        parent_id = comment_data.get("parent_id")  # For threaded replies
        content = comment_data.get("content", "").strip()
        mentions = comment_data.get("mentions", [])
        
        # Validate required fields
        if not post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="post_id is required"
            )
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="content cannot be empty"
            )
        
        if len(content) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment content cannot exceed 2000 characters"
            )
        
        # Validate access to post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Get post for pregnancy_id (needed for real-time broadcasting)
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Create threaded comment
        comment, metadata = await threaded_comment_service.create_threaded_comment(
            session=session,
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id,
            mentions=mentions
        )
        
        if not comment:
            error_msg = metadata.get("error", "Failed to create comment")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
        
        # Get author information for response
        from app.models.user import User
        author = session.get(User, user_id)
        author_info = {
            "id": user_id,
            "display_name": f"{author.first_name} {author.last_name}".strip() if author and author.first_name else "Unknown",
            "avatar_url": getattr(author, 'avatar_url', None) if author else None
        }
        
        # Build response data for real-time broadcasting
        comment_response = {
            "id": comment.id,
            "content": comment.content,
            "author": author_info,
            "post_id": post_id,
            "parent_id": parent_id,
            "thread_depth": comment.thread_depth,
            "thread_path": comment.thread_path,
            "mentions": [
                {"user_id": uid, "display_name": name}
                for uid, name in zip(comment.mentions, comment.mention_names)
            ],
            "family_warmth": comment.family_warmth_contribution,
            "can_accept_replies": comment.can_accept_replies(),
            "created_at": comment.created_at.isoformat(),
            "metadata": metadata
        }
        
        # Broadcast real-time comment update
        await realtime_websocket_service.broadcast_comment_update(
            pregnancy_id=post.pregnancy_id,
            comment_data={
                "action": "add",
                "comment": comment_response,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        # If comment has mentions, send mention notifications
        if comment.mentions:
            # This would typically send push notifications or email alerts
            logger.info(f"Comment {comment.id} mentions: {comment.mention_names}")
        
        return {
            "success": True,
            "comment": comment_response,
            "message": "Comment created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )


@router.get("/{post_id}", response_model=Dict[str, Any])
async def get_threaded_comments(
    post_id: str,
    include_reactions: bool = Query(True, description="Include reaction data for comments"),
    max_depth: int = Query(5, ge=1, le=5, description="Maximum thread depth to return"),
    limit_per_level: int = Query(50, ge=1, le=100, description="Maximum comments per thread level"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get all threaded comments for a post with full tree structure.
    """
    try:
        user_id = current_user["sub"]
        
        # Validate access to post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Get threaded comments
        comments_data = await threaded_comment_service.get_threaded_comments(
            session=session,
            post_id=post_id,
            user_id=user_id,
            include_reactions=include_reactions,
            max_depth=max_depth,
            limit_per_level=limit_per_level
        )
        
        if "error" in comments_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=comments_data["error"]
            )
        
        return comments_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting threaded comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get threaded comments: {str(e)}"
        )


@router.put("/{comment_id}", response_model=Dict[str, Any])
async def update_comment(
    comment_id: str,
    update_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Update a comment's content while preserving threading structure.
    """
    try:
        user_id = current_user["sub"]
        
        # Extract update data
        new_content = update_data.get("content", "").strip()
        preserve_mentions = update_data.get("preserve_mentions", True)
        
        # Validate content
        if not new_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content cannot be empty"
            )
        
        if len(new_content) > 2000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Comment content cannot exceed 2000 characters"
            )
        
        # Update comment
        updated_comment, metadata = await threaded_comment_service.update_comment_with_threading(
            session=session,
            comment_id=comment_id,
            user_id=user_id,
            new_content=new_content,
            preserve_mentions=preserve_mentions
        )
        
        if not updated_comment:
            error_msg = metadata.get("error", "Failed to update comment")
            if "not found" in error_msg.lower():
                raise HTTPException(status_code=404, detail=error_msg)
            elif "permission" in error_msg.lower():
                raise HTTPException(status_code=403, detail=error_msg)
            else:
                raise HTTPException(status_code=500, detail=error_msg)
        
        # Get post for real-time broadcasting
        post = session.get(Post, updated_comment.post_id)
        
        # Get author information
        from app.models.user import User
        author = session.get(User, user_id)
        author_info = {
            "id": user_id,
            "display_name": f"{author.first_name} {author.last_name}".strip() if author and author.first_name else "Unknown",
            "avatar_url": getattr(author, 'avatar_url', None) if author else None
        }
        
        # Build updated comment response
        comment_response = {
            "id": updated_comment.id,
            "content": updated_comment.content,
            "author": author_info,
            "edited": updated_comment.edited,
            "edit_history": updated_comment.edit_history,
            "updated_at": updated_comment.updated_at.isoformat(),
            "metadata": metadata
        }
        
        # Broadcast real-time update
        if post:
            await realtime_websocket_service.broadcast_comment_update(
                pregnancy_id=post.pregnancy_id,
                comment_data={
                    "action": "update",
                    "comment": comment_response,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )
        
        return {
            "success": True,
            "comment": comment_response,
            "message": "Comment updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}"
        )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Delete a comment and handle thread reorganization.
    """
    try:
        user_id = current_user["sub"]
        
        # Get comment
        comment = session.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # Check permissions
        if comment.user_id != user_id:
            # Check if user is post author (can moderate)
            post = session.get(Post, comment.post_id)
            if not post or post.author_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own comments"
                )
        
        # Store info for real-time broadcast
        post = session.get(Post, comment.post_id)
        pregnancy_id = post.pregnancy_id if post else None
        
        # Check if comment has replies
        if comment.reply_count > 0:
            # For comments with replies, we typically replace content with "[deleted]"
            # rather than actually deleting to preserve thread structure
            comment.content = "[This comment has been deleted]"
            comment.edited = True
            comment.updated_at = datetime.utcnow()
            session.add(comment)
            session.commit()
            
            # Broadcast soft delete
            if pregnancy_id:
                await realtime_websocket_service.broadcast_comment_update(
                    pregnancy_id=pregnancy_id,
                    comment_data={
                        "action": "soft_delete",
                        "comment_id": comment_id,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            
            return {"success": True, "message": "Comment marked as deleted"}
        else:
            # Actually delete comment if it has no replies
            await threaded_comment_service.delete(session, comment_id)
            
            # Broadcast hard delete
            if pregnancy_id:
                await realtime_websocket_service.broadcast_comment_update(
                    pregnancy_id=pregnancy_id,
                    comment_data={
                        "action": "delete",
                        "comment_id": comment_id,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            
            return {"success": True, "message": "Comment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}"
        )


@router.post("/typing", response_model=Dict[str, Any])
async def set_typing_indicator(
    typing_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Set typing indicator for real-time display.
    """
    try:
        user_id = current_user["sub"]
        
        # Extract typing data
        post_id = typing_data.get("post_id")
        parent_comment_id = typing_data.get("parent_comment_id")
        is_typing = typing_data.get("is_typing", True)
        
        # Validate that either post_id or parent_comment_id is provided
        if not post_id and not parent_comment_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either post_id or parent_comment_id must be provided"
            )
        
        # Set typing indicator
        success = await threaded_comment_service.set_typing_indicator(
            session=session,
            user_id=user_id,
            post_id=post_id,
            parent_comment_id=parent_comment_id,
            is_typing=is_typing
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target post or comment not found"
            )
        
        # Get user name for broadcasting
        from app.models.user import User
        author = session.get(User, user_id)
        user_name = f"{author.first_name} {author.last_name}".strip() if author and author.first_name else "Someone"
        
        # Determine pregnancy_id for broadcasting
        pregnancy_id = None
        if post_id:
            post = session.get(Post, post_id)
            pregnancy_id = post.pregnancy_id if post else None
        elif parent_comment_id:
            comment = session.get(Comment, parent_comment_id)
            if comment:
                post = session.get(Post, comment.post_id)
                pregnancy_id = post.pregnancy_id if post else None
        
        # Broadcast typing indicator
        if pregnancy_id:
            await realtime_websocket_service.broadcast_typing_indicator(
                pregnancy_id=pregnancy_id,
                user_id=user_id,
                post_id=post_id,
                comment_id=parent_comment_id,
                is_typing=is_typing,
                user_name=user_name
            )
        
        return {
            "success": True,
            "is_typing": is_typing,
            "message": f"Typing indicator {'set' if is_typing else 'cleared'}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting typing indicator: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set typing indicator: {str(e)}"
        )


@router.get("/mentions/suggestions/{pregnancy_id}")
async def get_mention_suggestions(
    pregnancy_id: str,
    query: str = Query(..., min_length=1, max_length=50, description="Search query for mentions"),
    limit: int = Query(10, ge=1, le=20, description="Maximum number of suggestions"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Get mention suggestions for auto-complete in comments.
    """
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
        
        # Get mention suggestions
        suggestions = await threaded_comment_service.get_mention_suggestions(
            session=session,
            pregnancy_id=pregnancy_id,
            query=query.strip(),
            limit=limit
        )
        
        return {
            "suggestions": suggestions,
            "query": query,
            "total_count": len(suggestions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mention suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get mention suggestions: {str(e)}"
        )


@router.post("/{comment_id}/reactions", response_model=Dict[str, Any])
async def add_comment_reaction(
    comment_id: str,
    reaction_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Add reaction to a comment using the enhanced reaction system.
    """
    try:
        user_id = current_user["sub"]
        
        # Validate comment exists and user has access
        comment = session.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if not await post_service.user_can_access_post(session, user_id, comment.post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this comment's post"
            )
        
        # Use enhanced reaction service for comment reactions
        # Comment reactions typically use a subset of main reactions
        reaction_type_str = reaction_data.get("reaction_type", "love")
        intensity = reaction_data.get("intensity", 2)
        custom_message = reaction_data.get("custom_message")
        
        # Validate reaction type
        from app.models.content import ReactionType
        try:
            reaction_type = ReactionType(reaction_type_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid reaction type: {reaction_type_str}"
            )
        
        # Add reaction to comment
        reaction, performance_metrics = await enhanced_reaction_service.add_optimistic_reaction(
            session=session,
            user_id=user_id,
            comment_id=comment_id,
            reaction_type=reaction_type,
            intensity=intensity,
            custom_message=custom_message,
            is_milestone_reaction=False,  # Comments don't typically have milestone reactions
            client_id=f"comment_reaction_{uuid.uuid4()}"
        )
        
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction to comment"
            )
        
        # Get updated reaction summary for the comment
        reaction_summary = await enhanced_reaction_service.get_enhanced_reaction_summary(
            session=session,
            comment_id=comment_id,
            user_id=user_id
        )
        
        # Broadcast real-time update
        post = session.get(Post, comment.post_id)
        if post:
            await realtime_websocket_service.broadcast_reaction_update(
                pregnancy_id=post.pregnancy_id,
                reaction_data={
                    "action": "add",
                    "target_type": "comment",
                    "comment_id": comment_id,
                    "reaction_id": reaction.id,
                    "user_id": user_id,
                    "reaction_type": reaction_type.value,
                    "intensity": intensity,
                    "updated_summary": reaction_summary,
                    "timestamp": reaction.created_at.isoformat()
                },
                exclude_user=user_id
            )
        
        return {
            "success": True,
            "reaction_id": reaction.id,
            "reaction_summary": reaction_summary,
            "message": "Comment reaction added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment reaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment reaction: {str(e)}"
        )


@router.delete("/{comment_id}/reactions")
async def remove_comment_reaction(
    comment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """
    Remove user's reaction from a comment.
    """
    try:
        user_id = current_user["sub"]
        
        # Validate comment exists and user has access
        comment = session.get(Comment, comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        if not await post_service.user_can_access_post(session, user_id, comment.post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this comment's post"
            )
        
        # Remove reaction
        success = await enhanced_reaction_service.remove_user_reaction(
            session=session,
            user_id=user_id,
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
            comment_id=comment_id,
            user_id=user_id
        )
        
        # Broadcast real-time update
        post = session.get(Post, comment.post_id)
        if post:
            await realtime_websocket_service.broadcast_reaction_update(
                pregnancy_id=post.pregnancy_id,
                reaction_data={
                    "action": "remove",
                    "target_type": "comment",
                    "comment_id": comment_id,
                    "user_id": user_id,
                    "updated_summary": reaction_summary,
                    "timestamp": datetime.utcnow().isoformat()
                },
                exclude_user=user_id
            )
        
        return {
            "success": True,
            "updated_summary": reaction_summary,
            "message": "Comment reaction removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing comment reaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove comment reaction: {str(e)}"
        )