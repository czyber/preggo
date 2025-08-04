"""
Post service for database operations using SQLModel sessions.

This service handles all post-related database operations including posts,
comments, reactions, media items, views, and shares.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from app.models.content import (
    Post, Comment, Reaction, MediaItem, PostView, PostShare,
    PostStatus, ReactionType
)
from app.models.family import FamilyMember, MemberStatus
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class PostService(BaseService[Post]):
    """Service for post-related database operations."""
    
    def __init__(self):
        super().__init__(Post)
    
    async def get_pregnancy_posts(
        self, 
        session: Session, 
        pregnancy_id: str,
        status: Optional[PostStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Post]:
        """Get posts for a pregnancy."""
        try:
            statement = select(Post).where(
                Post.pregnancy_id == pregnancy_id
            )
            
            if status:
                statement = statement.where(Post.status == status)
            
            statement = statement.order_by(Post.created_at.desc())
            
            if offset:
                statement = statement.offset(offset)
            if limit:
                statement = statement.limit(limit)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting posts for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def get_user_posts(
        self, 
        session: Session, 
        user_id: str,
        pregnancy_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Post]:
        """Get posts by a specific user."""
        try:
            statement = select(Post).where(
                Post.author_id == user_id
            )
            
            if pregnancy_id:
                statement = statement.where(Post.pregnancy_id == pregnancy_id)
            
            statement = statement.order_by(Post.created_at.desc())
            
            if offset:
                statement = statement.offset(offset)
            if limit:
                statement = statement.limit(limit)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting posts for user {user_id}: {e}")
            return []
    
    async def create_post(
        self, 
        session: Session, 
        post_data: Dict[str, Any]
    ) -> Optional[Post]:
        """Create a new post."""
        try:
            if "status" not in post_data:
                post_data["status"] = PostStatus.PUBLISHED
            
            return await self.create(session, post_data)
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None
    
    async def update_post(
        self, 
        session: Session, 
        post_id: str, 
        post_data: Dict[str, Any]
    ) -> Optional[Post]:
        """Update an existing post."""
        try:
            db_post = await self.get_by_id(session, post_id)
            if not db_post:
                return None
            
            post_data["updated_at"] = datetime.utcnow()
            return await self.update(session, db_post, post_data)
        except Exception as e:
            logger.error(f"Error updating post {post_id}: {e}")
            return None
    
    async def user_can_access_post(
        self, 
        session: Session, 
        user_id: str, 
        post_id: str
    ) -> bool:
        """Check if user can access a post based on privacy settings."""
        try:
            post = await self.get_by_id(session, post_id)
            if not post:
                return False
            
            # Author can always access
            if post.author_id == user_id:
                return True
            
            # Check if user owns the pregnancy
            from app.services.pregnancy_service import pregnancy_service
            if await pregnancy_service.user_owns_pregnancy(session, user_id, post.pregnancy_id):
                return True
            
            # Check if user is family member with access to this post
            # This would require checking the post's privacy settings against
            # the user's family memberships - simplified for now
            statement = select(FamilyMember).where(
                FamilyMember.user_id == user_id,
                FamilyMember.pregnancy_id == post.pregnancy_id,
                FamilyMember.status == MemberStatus.ACTIVE
            )
            member = session.exec(statement).first()
            
            return member is not None
        except Exception as e:
            logger.error(f"Error checking post access: {e}")
            return False
    
    async def increment_view_count(
        self, 
        session: Session, 
        post_id: str
    ) -> Optional[Post]:
        """Increment view count for a post."""
        try:
            post = await self.get_by_id(session, post_id)
            if not post:
                return None
            
            post.view_count += 1
            session.add(post)
            session.commit()
            session.refresh(post)
            return post
        except Exception as e:
            logger.error(f"Error incrementing view count for post {post_id}: {e}")
            return None
    
    async def get_posts_by_visibility(
        self, 
        session: Session,
        user_id: str,
        pregnancy_id: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Post]:
        """Get posts that a user can see based on their family memberships."""
        try:
            # Get user's family memberships for this pregnancy
            from app.services.family_service import family_member_service
            memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            
            if not memberships:
                # User has no family access, only see their own posts
                return await self.get_user_posts(session, user_id, pregnancy_id, limit, offset)
            
            # For now, return all pregnancy posts if user is a family member
            # In a full implementation, this would check privacy.allowed_groups
            return await self.get_pregnancy_posts(
                session, pregnancy_id, PostStatus.PUBLISHED, limit, offset
            )
        except Exception as e:
            logger.error(f"Error getting posts by visibility: {e}")
            return []


class CommentService(BaseService[Comment]):
    """Service for comment-related database operations."""
    
    def __init__(self):
        super().__init__(Comment)
    
    async def get_post_comments(
        self, 
        session: Session, 
        post_id: str,
        parent_id: Optional[str] = None
    ) -> List[Comment]:
        """Get comments for a post with author information."""
        try:
            from app.models.user import User
            
            statement = select(Comment).join(User).where(
                Comment.post_id == post_id
            )
            
            if parent_id:
                statement = statement.where(Comment.parent_id == parent_id)
            else:
                statement = statement.where(Comment.parent_id.is_(None))
            
            statement = statement.order_by(Comment.created_at.asc())
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting comments for post {post_id}: {e}")
            return []
    
    async def create_comment(
        self, 
        session: Session, 
        comment_data: Dict[str, Any]
    ) -> Optional[Comment]:
        """Create a new comment and return it with author information."""
        try:
            comment = await self.create(session, comment_data)
            
            if comment:
                # Increment comment count on post
                post_statement = select(Post).where(Post.id == comment_data["post_id"])
                post = session.exec(post_statement).first()
                if post:
                    post.comment_count += 1
                    session.add(post)
                    session.commit()
                
                # Fetch the comment with author information
                from app.models.user import User
                comment_with_author = session.exec(
                    select(Comment).join(User).where(Comment.id == comment.id)
                ).first()
                return comment_with_author
            
            return comment
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            return None
    
    async def update_comment(
        self, 
        session: Session, 
        comment_id: str, 
        comment_data: Dict[str, Any]
    ) -> Optional[Comment]:
        """Update a comment."""
        try:
            db_comment = await self.get_by_id(session, comment_id)
            if not db_comment:
                return None
            
            comment_data["updated_at"] = datetime.utcnow()
            comment_data["edited"] = True
            
            return await self.update(session, db_comment, comment_data)
        except Exception as e:
            logger.error(f"Error updating comment {comment_id}: {e}")
            return None
    
    async def user_can_modify_comment(
        self, 
        session: Session, 
        user_id: str, 
        comment_id: str
    ) -> bool:
        """Check if user can modify a comment."""
        try:
            comment = await self.get_by_id(session, comment_id)
            if not comment:
                return False
            
            # User can modify their own comments
            if comment.user_id == user_id:
                return True
            
            # Post author can moderate comments on their posts
            post_statement = select(Post).where(Post.id == comment.post_id)
            post = session.exec(post_statement).first()
            if post and post.author_id == user_id:
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking comment modification rights: {e}")
            return False


class ReactionService(BaseService[Reaction]):
    """Service for reaction-related database operations."""
    
    def __init__(self):
        super().__init__(Reaction)
    
    async def get_post_reactions(
        self, 
        session: Session, 
        post_id: str
    ) -> List[Reaction]:
        """Get all reactions for a post."""
        try:
            statement = select(Reaction).where(
                Reaction.post_id == post_id
            )
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting reactions for post {post_id}: {e}")
            return []
    
    async def get_comment_reactions(
        self, 
        session: Session, 
        comment_id: str
    ) -> List[Reaction]:
        """Get all reactions for a comment."""
        try:
            statement = select(Reaction).where(
                Reaction.comment_id == comment_id
            )
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting reactions for comment {comment_id}: {e}")
            return []
    
    async def add_or_update_reaction(
        self, 
        session: Session, 
        reaction_data: Dict[str, Any]
    ) -> Optional[Reaction]:
        """Add a new reaction or update existing one."""
        try:
            # Check if user already reacted
            statement = select(Reaction).where(
                Reaction.user_id == reaction_data["user_id"]
            )
            
            if reaction_data.get("post_id"):
                statement = statement.where(Reaction.post_id == reaction_data["post_id"])
            elif reaction_data.get("comment_id"):
                statement = statement.where(Reaction.comment_id == reaction_data["comment_id"])
            
            existing_reaction = session.exec(statement).first()
            
            if existing_reaction:
                # Update existing reaction
                existing_reaction.type = reaction_data["type"]
                session.add(existing_reaction)
                session.commit()
                session.refresh(existing_reaction)
                return existing_reaction
            else:
                # Create new reaction
                reaction = await self.create(session, reaction_data)
                
                if reaction:
                    # Increment reaction count
                    if reaction_data.get("post_id"):
                        post_statement = select(Post).where(Post.id == reaction_data["post_id"])
                        post = session.exec(post_statement).first()
                        if post:
                            post.reaction_count += 1
                            session.add(post)
                            session.commit()
                    elif reaction_data.get("comment_id"):
                        comment_statement = select(Comment).where(Comment.id == reaction_data["comment_id"])
                        comment = session.exec(comment_statement).first()
                        if comment:
                            comment.reaction_count += 1
                            session.add(comment)
                            session.commit()
                
                return reaction
        except Exception as e:
            logger.error(f"Error adding/updating reaction: {e}")
            return None
    
    async def remove_reaction(
        self, 
        session: Session, 
        user_id: str,
        post_id: Optional[str] = None,
        comment_id: Optional[str] = None
    ) -> bool:
        """Remove a user's reaction."""
        try:
            statement = select(Reaction).where(
                Reaction.user_id == user_id
            )
            
            if post_id:
                statement = statement.where(Reaction.post_id == post_id)
            elif comment_id:
                statement = statement.where(Reaction.comment_id == comment_id)
            else:
                return False
            
            reaction = session.exec(statement).first()
            if not reaction:
                return False
            
            # Decrement reaction count
            if post_id:
                post_statement = select(Post).where(Post.id == post_id)
                post = session.exec(post_statement).first()
                if post:
                    post.reaction_count = max(0, post.reaction_count - 1)
                    session.add(post)
            elif comment_id:
                comment_statement = select(Comment).where(Comment.id == comment_id)
                comment = session.exec(comment_statement).first()
                if comment:
                    comment.reaction_count = max(0, comment.reaction_count - 1)
                    session.add(comment)
            
            await self.delete(session, reaction)
            return True
        except Exception as e:
            logger.error(f"Error removing reaction: {e}")
            return False


class MediaItemService(BaseService[MediaItem]):
    """Service for media item-related database operations."""
    
    def __init__(self):
        super().__init__(MediaItem)
    
    async def get_post_media(
        self, 
        session: Session, 
        post_id: str
    ) -> List[MediaItem]:
        """Get all media items for a post."""
        try:
            statement = select(MediaItem).where(
                MediaItem.post_id == post_id
            ).order_by(MediaItem.order)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting media for post {post_id}: {e}")
            return []
    
    async def create_media_item(
        self, 
        session: Session, 
        media_data: Dict[str, Any]
    ) -> Optional[MediaItem]:
        """Create a new media item."""
        try:
            return await self.create(session, media_data)
        except Exception as e:
            logger.error(f"Error creating media item: {e}")
            return None


class PostViewService(BaseService[PostView]):
    """Service for post view tracking."""
    
    def __init__(self):
        super().__init__(PostView)
    
    async def record_view(
        self, 
        session: Session, 
        view_data: Dict[str, Any]
    ) -> Optional[PostView]:
        """Record a post view."""
        try:
            # Check if user already viewed this post recently (within 1 hour)
            statement = select(PostView).where(
                PostView.post_id == view_data["post_id"],
                PostView.user_id == view_data["user_id"],
                PostView.viewed_at >= datetime.utcnow() - timedelta(hours=1)
            )
            
            existing_view = session.exec(statement).first()
            if existing_view:
                # Update existing view
                existing_view.time_spent = view_data.get("time_spent")
                existing_view.viewed_at = datetime.utcnow()
                session.add(existing_view)
                session.commit()
                session.refresh(existing_view)
                return existing_view
            else:
                # Create new view and increment post view count
                view = await self.create(session, view_data)
                if view:
                    await post_service.increment_view_count(session, view_data["post_id"])
                return view
        except Exception as e:
            logger.error(f"Error recording post view: {e}")
            return None


class PostShareService(BaseService[PostShare]):
    """Service for post sharing operations."""
    
    def __init__(self):
        super().__init__(PostShare)
    
    async def create_share(
        self, 
        session: Session, 
        share_data: Dict[str, Any]
    ) -> Optional[PostShare]:
        """Create a new post share."""
        try:
            return await self.create(session, share_data)
        except Exception as e:
            logger.error(f"Error creating post share: {e}")
            return None


# Global service instances
post_service = PostService()
comment_service = CommentService()
reaction_service = ReactionService()
media_item_service = MediaItemService()
post_view_service = PostViewService()
post_share_service = PostShareService()