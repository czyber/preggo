"""
Posts endpoints for content sharing, reactions, and comments.

This module provides endpoints for:
- Creating and managing posts with various types (milestones, updates, photos)
- Comment management with threaded replies
- Reaction system for posts and comments
- Media upload and management
- Post visibility and privacy controls
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.core.supabase import get_current_active_user
from app.services.post_service import (
    post_service, comment_service, reaction_service, 
    media_item_service, post_view_service, post_share_service
)
from app.services.pregnancy_service import pregnancy_service
from app.db.session import get_session
from app.schemas.content import (
    PostCreate, PostUpdate, PostResponse,
    CommentCreate, CommentUpdate, CommentResponse,
    ReactionCreate, ReactionResponse,
    MediaItemCreate, MediaItemResponse,
    PostViewCreate, PostShareCreate
)
from app.models.content import PostStatus, ReactionType

router = APIRouter(prefix="/posts", tags=["posts"])


# Posts
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a new post."""
    try:
        user_id = current_user["sub"]
        
        # Verify user has access to the pregnancy
        if not await pregnancy_service.user_owns_pregnancy(session, user_id, post_data.pregnancy_id):
            # Also check if user is a family member
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, post_data.pregnancy_id
            )
            if not memberships:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have access to this pregnancy"
                )
        
        # Ensure author_id matches current user
        post_record = post_data.dict()
        post_record["author_id"] = user_id
        
        created_post = await post_service.create_post(session, post_record)
        
        if not created_post:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create post"
            )
        
        return PostResponse.from_orm(created_post)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create post: {str(e)}"
        )


@router.get("/pregnancy/{pregnancy_id}", response_model=List[PostResponse])
async def get_pregnancy_posts(
    pregnancy_id: str,
    status_filter: Optional[PostStatus] = Query(None, description="Filter by post status"),
    limit: Optional[int] = Query(20, description="Number of posts to return"),
    offset: Optional[int] = Query(0, description="Number of posts to skip"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get posts for a pregnancy with visibility filtering."""
    try:
        user_id = current_user["sub"]
        
        # Get posts that user can see based on their access level
        posts = await post_service.get_posts_by_visibility(
            session, user_id, pregnancy_id, limit, offset
        )
        
        # Filter by status if specified
        if status_filter:
            posts = [post for post in posts if post.status == status_filter]
        
        return [PostResponse.from_orm(post) for post in posts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pregnancy posts: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=List[PostResponse])
async def get_user_posts(
    user_id: str,
    pregnancy_id: Optional[str] = Query(None, description="Filter by pregnancy"),
    limit: Optional[int] = Query(20, description="Number of posts to return"),
    offset: Optional[int] = Query(0, description="Number of posts to skip"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get posts by a specific user."""
    try:
        current_user_id = current_user["sub"]
        
        # Users can only see their own posts or posts they have access to
        if user_id != current_user_id:
            # Check if current user has access to the posts via family membership
            if pregnancy_id:
                if not await pregnancy_service.user_owns_pregnancy(session, current_user_id, pregnancy_id):
                    from app.services.family_service import family_member_service
                    memberships = await family_member_service.get_user_memberships(
                        session, current_user_id, pregnancy_id
                    )
                    if not memberships:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="You don't have access to these posts"
                        )
        
        posts = await post_service.get_user_posts(session, user_id, pregnancy_id, limit, offset)
        return [PostResponse.from_orm(post) for post in posts]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user posts: {str(e)}"
        )


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get a specific post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access this post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        post = await post_service.get_by_id(session, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        return PostResponse.from_orm(post)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post: {str(e)}"
        )


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a post."""
    try:
        user_id = current_user["sub"]
        
        # Get post to check ownership
        post = await post_service.get_by_id(session, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Only author can update posts
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own posts"
            )
        
        # Update post
        update_data = post_update.dict(exclude_unset=True)
        updated_post = await post_service.update_post(session, post_id, update_data)
        
        if not updated_post:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update post"
            )
        
        return PostResponse.from_orm(updated_post)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update post: {str(e)}"
        )


@router.delete("/{post_id}")
async def delete_post(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete a post."""
    try:
        user_id = current_user["sub"]
        
        # Get post to check ownership
        post = await post_service.get_by_id(session, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Only author can delete posts
        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own posts"
            )
        
        await post_service.delete(session, post)
        return {"message": "Post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete post: {str(e)}"
        )


# Comments
@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a comment on a post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Create comment
        comment_record = comment_data.dict()
        comment_record["post_id"] = post_id
        comment_record["user_id"] = user_id
        
        created_comment = await comment_service.create_comment(session, comment_record)
        
        if not created_comment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
        
        return CommentResponse.from_orm(created_comment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create comment: {str(e)}"
        )


@router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: str,
    parent_id: Optional[str] = Query(None, description="Get replies to a specific comment"),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get comments for a post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        comments = await comment_service.get_post_comments(session, post_id, parent_id)
        return [CommentResponse.from_orm(comment) for comment in comments]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get comments: {str(e)}"
        )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Update a comment."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can modify this comment
        if not await comment_service.user_can_modify_comment(session, user_id, comment_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this comment"
            )
        
        # Update comment
        update_data = comment_update.dict(exclude_unset=True)
        updated_comment = await comment_service.update_comment(session, comment_id, update_data)
        
        if not updated_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return CommentResponse.from_orm(updated_comment)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update comment: {str(e)}"
        )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Delete a comment."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can modify this comment
        if not await comment_service.user_can_modify_comment(session, user_id, comment_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this comment"
            )
        
        comment = await comment_service.get_by_id(session, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        await comment_service.delete(session, comment)
        return {"message": "Comment deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete comment: {str(e)}"
        )


# Reactions
@router.post("/{post_id}/reactions", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
async def add_post_reaction(
    post_id: str,
    reaction_type: ReactionType,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Add or update a reaction to a post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Add or update reaction
        reaction_data = {
            "user_id": user_id,
            "post_id": post_id,
            "type": reaction_type
        }
        
        reaction = await reaction_service.add_or_update_reaction(session, reaction_data)
        
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction"
            )
        
        return ReactionResponse.from_orm(reaction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add reaction: {str(e)}"
        )


@router.delete("/{post_id}/reactions")
async def remove_post_reaction(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove a reaction from a post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        success = await reaction_service.remove_reaction(session, user_id, post_id=post_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reaction not found"
            )
        
        return {"message": "Reaction removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove reaction: {str(e)}"
        )


@router.get("/{post_id}/reactions", response_model=List[ReactionResponse])
async def get_post_reactions(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all reactions for a post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        reactions = await reaction_service.get_post_reactions(session, post_id)
        return [ReactionResponse.from_orm(reaction) for reaction in reactions]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get reactions: {str(e)}"
        )


# Comment Reactions
@router.post("/comments/{comment_id}/reactions", response_model=ReactionResponse, status_code=status.HTTP_201_CREATED)
async def add_comment_reaction(
    comment_id: str,
    reaction_type: ReactionType,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Add or update a reaction to a comment."""
    try:
        user_id = current_user["sub"]
        
        # Get comment to check post access
        comment = await comment_service.get_by_id(session, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, comment.post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Add or update reaction
        reaction_data = {
            "user_id": user_id,
            "comment_id": comment_id,
            "type": reaction_type
        }
        
        reaction = await reaction_service.add_or_update_reaction(session, reaction_data)
        
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add reaction"
            )
        
        return ReactionResponse.from_orm(reaction)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add comment reaction: {str(e)}"
        )


@router.delete("/comments/{comment_id}/reactions")
async def remove_comment_reaction(
    comment_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Remove a reaction from a comment."""
    try:
        user_id = current_user["sub"]
        
        # Get comment to check post access
        comment = await comment_service.get_by_id(session, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, comment.post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        success = await reaction_service.remove_reaction(session, user_id, comment_id=comment_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reaction not found"
            )
        
        return {"message": "Comment reaction removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove comment reaction: {str(e)}"
        )


# Media
@router.post("/media", response_model=MediaItemResponse, status_code=status.HTTP_201_CREATED)
async def create_media_item(
    media_data: MediaItemCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Create a media item (can be attached to post later)."""
    try:
        user_id = current_user["sub"]
        
        # Ensure uploaded_by matches current user
        media_record = media_data.dict()
        media_record["uploaded_by"] = user_id
        
        created_media = await media_item_service.create_media_item(session, media_record)
        
        if not created_media:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create media item"
            )
        
        return MediaItemResponse.from_orm(created_media)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create media item: {str(e)}"
        )


@router.get("/{post_id}/media", response_model=List[MediaItemResponse])
async def get_post_media(
    post_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Get all media items for a post."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        media_items = await media_item_service.get_post_media(session, post_id)
        return [MediaItemResponse.from_orm(media) for media in media_items]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post media: {str(e)}"
        )


# Views and Shares
@router.post("/{post_id}/view")
async def record_post_view(
    post_id: str,
    view_data: PostViewCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Record a post view for analytics."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Record view
        view_record = view_data.dict()
        view_record["post_id"] = post_id
        view_record["user_id"] = user_id
        
        await post_view_service.record_view(session, view_record)
        return {"message": "View recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record view: {str(e)}"
        )


@router.post("/{post_id}/share")
async def share_post(
    post_id: str,
    share_data: PostShareCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    session: Session = Depends(get_session)
):
    """Share a post with family members or groups."""
    try:
        user_id = current_user["sub"]
        
        # Check if user can access the post
        if not await post_service.user_can_access_post(session, user_id, post_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this post"
            )
        
        # Create share record
        share_record = share_data.dict()
        share_record["post_id"] = post_id
        share_record["shared_by"] = user_id
        
        created_share = await post_share_service.create_share(session, share_record)
        
        if not created_share:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to share post"
            )
        
        return {"message": "Post shared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share post: {str(e)}"
        )