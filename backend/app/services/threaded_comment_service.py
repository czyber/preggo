"""
Threaded Comment Service for enhanced comment functionality.

This service provides:
- Threading up to 5 levels deep with proper path management
- @mention system with auto-complete and notifications
- Real-time typing indicators via WebSocket
- Comment reactions (subset of main reactions)
- Threaded reply endpoints with performance optimization
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, func, and_, or_
from datetime import datetime, timedelta
from app.models.content import Comment, Post, FeedActivity
from app.models.family import FamilyMember, MemberStatus
from app.models.user import User
from app.services.base import BaseService
import logging
import re
import asyncio
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class ThreadedCommentService(BaseService[Comment]):
    """Enhanced service for threaded comment operations with real-time features."""
    
    def __init__(self):
        super().__init__(Comment)
        
        # Mention pattern for detecting @mentions in comment content
        self.mention_pattern = re.compile(r'@([a-zA-Z0-9_]+)', re.IGNORECASE)
        
        # Typing indicator cleanup interval (seconds)
        self.typing_cleanup_interval = 30
    
    async def create_threaded_comment(
        self,
        session: Session,
        post_id: str,
        user_id: str,
        content: str,
        parent_id: Optional[str] = None,
        mentions: Optional[List[str]] = None
    ) -> Tuple[Optional[Comment], Dict[str, Any]]:
        """
        Create a new comment with proper threading support.
        
        Returns:
            Tuple of (comment, metadata including thread_info)
        """
        try:
            # Validate post exists
            post = session.get(Post, post_id)
            if not post:
                return None, {"error": "Post not found"}
            
            # Validate parent comment if provided
            parent_comment = None
            thread_depth = 0
            thread_path = ""
            root_comment_id = None
            
            if parent_id:
                parent_comment = session.get(Comment, parent_id)
                if not parent_comment:
                    return None, {"error": "Parent comment not found"}
                
                if not parent_comment.can_accept_replies():
                    return None, {"error": "Maximum thread depth reached"}
                
                thread_depth = parent_comment.thread_depth + 1
                root_comment_id = parent_comment.root_comment_id or parent_comment.id
                
                # Generate thread path
                current_reply_count = await self._get_reply_count(session, parent_id)
                thread_path = parent_comment.get_next_thread_path(current_reply_count)
            else:
                # Root comment - generate path based on post's root comment count
                root_comment_count = await self._get_root_comment_count(session, post_id)
                thread_path = str(root_comment_count + 1)
            
            # Process mentions in content
            processed_mentions = []
            mention_names = []
            
            if mentions:
                processed_mentions, mention_names = await self._process_mentions(
                    session, mentions, post.pregnancy_id
                )
            else:
                # Auto-detect mentions from content
                detected_mentions = self._detect_mentions_in_content(content)
                if detected_mentions:
                    processed_mentions, mention_names = await self._process_mentions(
                        session, detected_mentions, post.pregnancy_id
                    )
            
            # Calculate family warmth contribution
            family_warmth = await self._calculate_comment_family_warmth(
                session, user_id, post.pregnancy_id, content, len(processed_mentions)
            )
            
            # Create comment data
            comment_data = {
                "post_id": post_id,
                "user_id": user_id,
                "parent_id": parent_id,
                "content": content,
                "thread_depth": thread_depth,
                "thread_path": thread_path,
                "root_comment_id": root_comment_id,
                "mentions": processed_mentions,
                "mention_names": mention_names,
                "family_warmth_contribution": family_warmth,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create the comment
            comment = await self.create(session, comment_data)
            if not comment:
                return None, {"error": "Failed to create comment"}
            
            # Update parent comment reply count
            if parent_comment:
                await self._update_parent_reply_counts(session, parent_comment.id)
            
            # Update post comment count
            await self._update_post_comment_count(session, post_id)
            
            # Queue background tasks for notifications and real-time updates
            asyncio.create_task(self._queue_comment_background_tasks(
                session, comment, post, processed_mentions
            ))
            
            # Prepare metadata response
            metadata = {
                "thread_depth": thread_depth,
                "thread_path": thread_path,
                "mentions_processed": len(processed_mentions),
                "family_warmth_contribution": family_warmth,
                "is_reply": parent_id is not None,
                "created_at": comment.created_at.isoformat()
            }
            
            return comment, metadata
            
        except Exception as e:
            logger.error(f"Error creating threaded comment: {e}")
            return None, {"error": str(e)}
    
    async def get_threaded_comments(
        self,
        session: Session,
        post_id: str,
        user_id: Optional[str] = None,
        include_reactions: bool = True,
        max_depth: int = 5,
        limit_per_level: int = 50
    ) -> Dict[str, Any]:
        """
        Get comments for a post with full threading structure.
        
        Returns nested comment structure with performance optimization.
        """
        try:
            # Get all comments for the post ordered by thread path
            comments_query = select(Comment).where(
                Comment.post_id == post_id
            ).order_by(Comment.thread_path)
            
            all_comments = session.exec(comments_query).all()
            
            if not all_comments:
                return {"comments": [], "total_count": 0, "thread_structure": {}}
            
            # Build threaded structure
            comment_tree = {}
            comment_lookup = {}
            root_comments = []
            
            for comment in all_comments:
                comment_data = await self._format_comment_for_response(
                    session, comment, user_id, include_reactions
                )
                comment_lookup[comment.id] = comment_data
                
                if comment.thread_depth == 0:
                    # Root comment
                    comment_data["replies"] = []
                    root_comments.append(comment_data)
                    comment_tree[comment.id] = comment_data
                else:
                    # Reply comment - find parent and add to its replies
                    parent_comment = comment_lookup.get(comment.parent_id)
                    if parent_comment:
                        if "replies" not in parent_comment:
                            parent_comment["replies"] = []
                        comment_data["replies"] = []
                        parent_comment["replies"].append(comment_data)
            
            # Calculate thread statistics
            thread_stats = {
                "total_comments": len(all_comments),
                "root_comments": len(root_comments),
                "max_depth_used": max(comment.thread_depth for comment in all_comments) if all_comments else 0,
                "threads_with_replies": len([c for c in all_comments if c.reply_count > 0]),
                "total_mentions": sum(len(c.mentions) for c in all_comments)
            }
            
            return {
                "comments": root_comments,
                "total_count": len(all_comments),
                "thread_structure": comment_tree,
                "thread_statistics": thread_stats,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting threaded comments: {e}")
            return {"error": str(e)}
    
    async def update_comment_with_threading(
        self,
        session: Session,
        comment_id: str,
        user_id: str,
        new_content: str,
        preserve_mentions: bool = True
    ) -> Tuple[Optional[Comment], Dict[str, Any]]:
        """Update comment content while preserving threading structure."""
        try:
            comment = session.get(Comment, comment_id)
            if not comment:
                return None, {"error": "Comment not found"}
            
            # Check permissions
            if comment.user_id != user_id:
                # Check if user is post author (can moderate)
                post = session.get(Post, comment.post_id)
                if not post or post.author_id != user_id:
                    return None, {"error": "Permission denied"}
            
            # Store original content for edit history
            edit_entry = {
                "previous_content": comment.content,
                "edited_at": datetime.utcnow().isoformat(),
                "edited_by": user_id
            }
            
            if not comment.edit_history:
                comment.edit_history = []
            comment.edit_history.append(edit_entry)
            
            # Process mentions in new content
            if not preserve_mentions:
                post = session.get(Post, comment.post_id)
                detected_mentions = self._detect_mentions_in_content(new_content)
                if detected_mentions:
                    processed_mentions, mention_names = await self._process_mentions(
                        session, detected_mentions, post.pregnancy_id
                    )
                    comment.mentions = processed_mentions
                    comment.mention_names = mention_names
            
            # Update comment
            comment.content = new_content
            comment.edited = True
            comment.updated_at = datetime.utcnow()
            
            session.add(comment)
            session.commit()
            session.refresh(comment)
            
            # Queue real-time update
            asyncio.create_task(self._broadcast_comment_update(comment))
            
            metadata = {
                "edit_count": len(comment.edit_history),
                "mentions_updated": not preserve_mentions,
                "updated_at": comment.updated_at.isoformat()
            }
            
            return comment, metadata
            
        except Exception as e:
            logger.error(f"Error updating comment: {e}")
            return None, {"error": str(e)}
    
    async def set_typing_indicator(
        self,
        session: Session,
        user_id: str,
        post_id: Optional[str] = None,
        parent_comment_id: Optional[str] = None,
        is_typing: bool = True
    ) -> bool:
        """Set typing indicator for real-time display."""
        try:
            # Determine what the user is typing on
            target_comment = None
            
            if parent_comment_id:
                # Typing reply to a comment
                target_comment = session.get(Comment, parent_comment_id)
                if not target_comment:
                    return False
            elif post_id:
                # Typing new root comment on post
                post = session.get(Post, post_id)
                if not post:
                    return False
            else:
                return False
            
            if is_typing:
                # Set typing indicator
                if target_comment:
                    target_comment.is_typing_reply = True
                    target_comment.last_typing_user = user_id
                    target_comment.last_typing_at = datetime.utcnow()
                    session.add(target_comment)
                    session.commit()
                
                # Broadcast typing indicator
                asyncio.create_task(self._broadcast_typing_indicator(
                    user_id, post_id, parent_comment_id, True
                ))
            else:
                # Clear typing indicator
                if target_comment:
                    target_comment.is_typing_reply = False
                    target_comment.last_typing_user = None
                    target_comment.last_typing_at = None
                    session.add(target_comment)
                    session.commit()
                
                # Broadcast typing stopped
                asyncio.create_task(self._broadcast_typing_indicator(
                    user_id, post_id, parent_comment_id, False
                ))
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting typing indicator: {e}")
            return False
    
    async def get_mention_suggestions(
        self,
        session: Session,
        pregnancy_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get mention suggestions for auto-complete."""
        try:
            if not query or len(query) < 1:
                return []
            
            # Get family members for this pregnancy
            family_query = select(FamilyMember, User).join(User).where(
                FamilyMember.pregnancy_id == pregnancy_id,
                FamilyMember.status == MemberStatus.ACTIVE
            )
            
            family_members = session.exec(family_query).all()
            
            suggestions = []
            for member, user in family_members:
                # Match against username, display name, or email
                user_data = {
                    "user_id": user.id,
                    "username": user.email.split("@")[0],  # Use email prefix as username
                    "display_name": f"{user.first_name} {user.last_name}".strip() if user.first_name else user.email,
                    "avatar_url": getattr(user, 'avatar_url', None),
                    "relationship": member.relationship_type.value if member.relationship_type else "Family"
                }
                
                # Calculate match score
                username_similarity = SequenceMatcher(None, query.lower(), user_data["username"].lower()).ratio()
                name_similarity = SequenceMatcher(None, query.lower(), user_data["display_name"].lower()).ratio()
                
                match_score = max(username_similarity, name_similarity)
                
                if match_score > 0.3:  # Threshold for relevance
                    user_data["match_score"] = match_score
                    suggestions.append(user_data)
            
            # Sort by match score and limit results
            suggestions.sort(key=lambda x: x["match_score"], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error getting mention suggestions: {e}")
            return []
    
    async def cleanup_old_typing_indicators(self, session: Session):
        """Clean up old typing indicators (run periodically)."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=self.typing_cleanup_interval)
            
            # Find comments with stale typing indicators
            stale_typing_query = select(Comment).where(
                Comment.is_typing_reply == True,
                Comment.last_typing_at < cutoff_time
            )
            
            stale_comments = session.exec(stale_typing_query).all()
            
            for comment in stale_comments:
                comment.is_typing_reply = False
                comment.last_typing_user = None
                comment.last_typing_at = None
                session.add(comment)
            
            if stale_comments:
                session.commit()
                logger.info(f"Cleaned up {len(stale_comments)} stale typing indicators")
            
        except Exception as e:
            logger.error(f"Error cleaning up typing indicators: {e}")
    
    # Private helper methods
    
    async def _get_reply_count(self, session: Session, parent_id: str) -> int:
        """Get direct reply count for a comment."""
        count_query = select(func.count(Comment.id)).where(Comment.parent_id == parent_id)
        return session.exec(count_query).first() or 0
    
    async def _get_root_comment_count(self, session: Session, post_id: str) -> int:
        """Get root comment count for a post."""
        count_query = select(func.count(Comment.id)).where(
            Comment.post_id == post_id,
            Comment.thread_depth == 0
        )
        return session.exec(count_query).first() or 0
    
    def _detect_mentions_in_content(self, content: str) -> List[str]:
        """Detect @mentions in comment content."""
        matches = self.mention_pattern.findall(content)
        return list(set(matches))  # Remove duplicates
    
    async def _process_mentions(
        self,
        session: Session,
        mentions: List[str],
        pregnancy_id: str
    ) -> Tuple[List[str], List[str]]:
        """Process mention strings to user IDs and display names."""
        processed_user_ids = []
        processed_names = []
        
        try:
            # Get family members for validation
            family_query = select(FamilyMember, User).join(User).where(
                FamilyMember.pregnancy_id == pregnancy_id,
                FamilyMember.status == MemberStatus.ACTIVE
            )
            
            family_members = session.exec(family_query).all()
            
            # Create lookup maps
            username_to_user = {}
            for member, user in family_members:
                username = user.email.split("@")[0]
                username_to_user[username.lower()] = user
            
            # Process each mention
            for mention in mentions:
                mention_lower = mention.lower()
                if mention_lower in username_to_user:
                    user = username_to_user[mention_lower]
                    processed_user_ids.append(user.id)
                    display_name = f"{user.first_name} {user.last_name}".strip() if user.first_name else user.email
                    processed_names.append(display_name)
            
        except Exception as e:
            logger.error(f"Error processing mentions: {e}")
        
        return processed_user_ids, processed_names
    
    async def _calculate_comment_family_warmth(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        content: str,
        mention_count: int
    ) -> float:
        """Calculate family warmth contribution for a comment."""
        base_warmth = 0.03  # Base warmth for any comment
        
        # Length bonus (longer, more thoughtful comments)
        length_bonus = min(len(content) / 500, 0.02)
        
        # Mention bonus (engaging with specific family members)
        mention_bonus = mention_count * 0.01
        
        # Check if user is family member (not pregnancy owner)
        family_member_query = select(FamilyMember).where(
            FamilyMember.user_id == user_id,
            FamilyMember.pregnancy_id == pregnancy_id,
            FamilyMember.status == MemberStatus.ACTIVE
        )
        is_family_member = session.exec(family_member_query).first() is not None
        
        family_bonus = 0.02 if is_family_member else 0.0
        
        total_warmth = base_warmth + length_bonus + mention_bonus + family_bonus
        return min(total_warmth, 0.1)  # Cap at 0.1 per comment
    
    async def _format_comment_for_response(
        self,
        session: Session,
        comment: Comment,
        user_id: Optional[str] = None,
        include_reactions: bool = True
    ) -> Dict[str, Any]:
        """Format comment for API response with all enhanced data."""
        # Get author information
        author = session.get(User, comment.user_id)
        author_data = {
            "id": comment.user_id,
            "display_name": f"{author.first_name} {author.last_name}".strip() if author and author.first_name else "Unknown",
            "avatar_url": getattr(author, 'avatar_url', None) if author else None
        }
        
        # Build base comment data
        comment_data = {
            "id": comment.id,
            "content": comment.content,
            "author": author_data,
            "thread_depth": comment.thread_depth,
            "thread_path": comment.thread_path,
            "reply_count": comment.reply_count,
            "total_descendant_count": comment.total_descendant_count,
            "mentions": [
                {"user_id": uid, "display_name": name}
                for uid, name in zip(comment.mentions, comment.mention_names)
            ],
            "edited": comment.edited,
            "family_warmth": comment.family_warmth_contribution,
            "can_accept_replies": comment.can_accept_replies(),
            "created_at": comment.created_at.isoformat(),
            "updated_at": comment.updated_at.isoformat()
        }
        
        # Add edit history if edited
        if comment.edited and comment.edit_history:
            comment_data["edit_history"] = comment.edit_history
        
        # Add reaction data if requested
        if include_reactions and comment.reaction_summary:
            comment_data["reactions"] = {
                "total_count": comment.reaction_count,
                "reaction_counts": comment.reaction_summary,
                "user_reaction": None  # Would need to query user's reaction
            }
        
        # Add typing indicator info
        if comment.is_typing_reply:
            typing_author = session.get(User, comment.last_typing_user) if comment.last_typing_user else None
            comment_data["typing_indicator"] = {
                "is_someone_typing": True,
                "typing_user": {
                    "id": comment.last_typing_user,
                    "display_name": f"{typing_author.first_name} {typing_author.last_name}".strip() if typing_author and typing_author.first_name else "Someone"
                } if typing_author else None,
                "typing_since": comment.last_typing_at.isoformat() if comment.last_typing_at else None
            }
        
        return comment_data
    
    async def _update_parent_reply_counts(self, session: Session, comment_id: str):
        """Update reply counts for parent comments up the thread."""
        try:
            comment = session.get(Comment, comment_id)
            if not comment or not comment.parent_id:
                return
            
            # Update direct parent reply count
            parent = session.get(Comment, comment.parent_id)
            if parent:
                direct_replies_query = select(func.count(Comment.id)).where(Comment.parent_id == parent.id)
                parent.reply_count = session.exec(direct_replies_query).first() or 0
                
                # Update total descendant count for all ancestors
                if parent.root_comment_id:
                    root_comment = session.get(Comment, parent.root_comment_id)
                    if root_comment:
                        descendant_query = select(func.count(Comment.id)).where(Comment.root_comment_id == root_comment.id)
                        root_comment.total_descendant_count = session.exec(descendant_query).first() or 0
                        session.add(root_comment)
                
                session.add(parent)
                session.commit()
        
        except Exception as e:
            logger.error(f"Error updating parent reply counts: {e}")
    
    async def _update_post_comment_count(self, session: Session, post_id: str):
        """Update total comment count on post."""
        try:
            post = session.get(Post, post_id)
            if post:
                comment_count_query = select(func.count(Comment.id)).where(Comment.post_id == post_id)
                post.comment_count = session.exec(comment_count_query).first() or 0
                session.add(post)
                session.commit()
        
        except Exception as e:
            logger.error(f"Error updating post comment count: {e}")
    
    async def _queue_comment_background_tasks(
        self,
        session: Session,
        comment: Comment,
        post: Post,
        mentioned_user_ids: List[str]
    ):
        """Queue background tasks for comment processing."""
        try:
            # Create feed activity
            activity_data = {
                "content_preview": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                "thread_depth": comment.thread_depth,
                "mentions_count": len(mentioned_user_ids),
                "is_reply": comment.parent_id is not None
            }
            
            activity = FeedActivity(
                pregnancy_id=post.pregnancy_id,
                user_id=comment.user_id,
                activity_type="comment",
                target_id=comment.id,
                target_type="comment",
                activity_data=activity_data,
                broadcast_priority=3 if mentioned_user_ids else 1
            )
            
            session.add(activity)
            session.commit()
            
            # Queue mention notifications
            if mentioned_user_ids:
                asyncio.create_task(self._send_mention_notifications(
                    comment, post, mentioned_user_ids
                ))
            
        except Exception as e:
            logger.error(f"Error in comment background tasks: {e}")
    
    async def _send_mention_notifications(
        self,
        comment: Comment,
        post: Post,
        mentioned_user_ids: List[str]
    ):
        """Send notifications to mentioned users."""
        try:
            # This would integrate with notification service
            logger.info(f"Sending mention notifications for comment {comment.id} to users: {mentioned_user_ids}")
            
        except Exception as e:
            logger.error(f"Error sending mention notifications: {e}")
    
    async def _broadcast_comment_update(self, comment: Comment):
        """Broadcast comment update via WebSocket."""
        try:
            # This would integrate with WebSocket service
            logger.info(f"Broadcasting comment update for comment {comment.id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting comment update: {e}")
    
    async def _broadcast_typing_indicator(
        self,
        user_id: str,
        post_id: Optional[str],
        parent_comment_id: Optional[str],
        is_typing: bool
    ):
        """Broadcast typing indicator via WebSocket."""
        try:
            # This would integrate with WebSocket service
            logger.info(f"Broadcasting typing indicator: user={user_id}, post={post_id}, parent={parent_comment_id}, typing={is_typing}")
            
        except Exception as e:
            logger.error(f"Error broadcasting typing indicator: {e}")


# Global service instance
threaded_comment_service = ThreadedCommentService()