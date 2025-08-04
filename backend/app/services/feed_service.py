"""
Feed service for family-specific content delivery and engagement.

This service handles the feed algorithm for pregnancy tracking, providing
family-aware content filtering, engagement scoring, and real-time capabilities
for celebrations and interactions.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, func, and_, or_
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from app.services.base import BaseService
from app.services.post_service import post_service, reaction_service, comment_service
from app.services.family_service import family_member_service
from app.services.pregnancy_service import pregnancy_service
from app.models.content import (
    Post, Reaction, Comment, PostType, PostStatus, ReactionType, VisibilityLevel
)
from app.models.family import FamilyMember, MemberStatus, RelationshipType
from app.models.pregnancy import Pregnancy
from app.schemas.feed import (
    FeedRequest, FeedResponse, EnrichedPost, PersonalTimelineResponse,
    ReactionSummary, CommentPreview, PregnancyContext, FamilyEngagementStats,
    FeedFilterType, FeedSortType, PregnancyReactionType
)

logger = logging.getLogger(__name__)


class FeedService(BaseService[Post]):
    """Service for family feed algorithm and content delivery."""
    
    def __init__(self):
        super().__init__(Post)
    
    async def get_family_feed(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest
    ) -> FeedResponse:
        """
        Get family feed with privacy-aware filtering and engagement scoring.
        
        Prioritizes:
        - Recent content from family members
        - Milestone posts with celebration features
        - Posts that need family support/responses
        - Pregnancy progression context
        """
        try:
            # Verify user has access to this pregnancy
            if not await self._user_has_access(session, user_id, pregnancy_id):
                return FeedResponse(posts=[], total_count=0, has_more=False)
            
            # Get user's family memberships for context
            family_memberships = await family_member_service.get_user_memberships(
                session, user_id, pregnancy_id
            )
            
            # Build optimized query with joins
            posts_query = await self._build_family_feed_query(
                session, user_id, pregnancy_id, feed_request, family_memberships
            )
            
            # Apply sorting
            posts_query = self._apply_feed_sorting(posts_query, feed_request.sort_by)
            
            # Get total count efficiently
            count_query = select(func.count(Post.id)).where(
                and_(
                    Post.pregnancy_id == pregnancy_id,
                    Post.status == PostStatus.PUBLISHED,
                    Post.deleted_at.is_(None)
                )
            )
            if feed_request.since:
                count_query = count_query.where(Post.created_at >= feed_request.since)
            if feed_request.filter_type != FeedFilterType.ALL:
                post_types = self._get_post_types_for_filter(feed_request.filter_type)
                if post_types:
                    count_query = count_query.where(Post.type.in_(post_types))
            
            total_count = session.exec(count_query).first() or 0
            
            # Apply pagination at DB level
            posts_query = posts_query.offset(feed_request.offset).limit(feed_request.limit)
            posts_with_metadata = session.exec(posts_query).all()
            
            # Enrich posts with additional context using batch operations
            enriched_posts = await self._batch_enrich_posts_for_feed(
                session, posts_with_metadata, user_id, pregnancy_id, feed_request
            )
            
            # Get pregnancy summary for context
            pregnancy_summary = await self._get_pregnancy_summary(session, pregnancy_id)
            
            # Calculate pagination info
            has_more = (feed_request.offset + len(posts)) < total_count
            next_offset = feed_request.offset + len(posts) if has_more else None
            
            # Generate feed metadata
            feed_metadata = await self._generate_feed_metadata(
                session, user_id, pregnancy_id, enriched_posts
            )
            
            return FeedResponse(
                posts=enriched_posts,
                total_count=total_count,
                has_more=has_more,
                next_offset=next_offset,
                feed_metadata=feed_metadata,
                pregnancy_summary=pregnancy_summary
            )
            
        except Exception as e:
            logger.error(f"Error getting family feed for pregnancy {pregnancy_id}: {e}")
            return FeedResponse(posts=[], total_count=0, has_more=False)
    
    async def get_personal_timeline(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest
    ) -> PersonalTimelineResponse:
        """Get personal timeline for pregnancy owner."""
        try:
            # Verify user owns this pregnancy
            if not await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
                return PersonalTimelineResponse(
                    posts=[], milestones_coming_up=[], total_count=0, has_more=False
                )
            
            # Get user's posts for this pregnancy
            posts = await post_service.get_user_posts(
                session, user_id, pregnancy_id, feed_request.limit, feed_request.offset
            )
            
            # Enrich posts with personal context
            enriched_posts = []
            for post in posts:
                enriched_post = await self._enrich_post_for_personal_timeline(
                    session, post, user_id, pregnancy_id, feed_request
                )
                enriched_posts.append(enriched_post)
            
            # Get upcoming milestones
            milestones_coming_up = await self._get_upcoming_milestones(session, pregnancy_id)
            
            # Get weekly progress
            weekly_progress = await self._get_weekly_progress(session, pregnancy_id)
            
            # Get total count
            all_user_posts = await post_service.get_user_posts(session, user_id, pregnancy_id)
            total_count = len(all_user_posts)
            
            has_more = (feed_request.offset + len(posts)) < total_count
            
            return PersonalTimelineResponse(
                posts=enriched_posts,
                milestones_coming_up=milestones_coming_up,
                weekly_progress=weekly_progress,
                total_count=total_count,
                has_more=has_more
            )
            
        except Exception as e:
            logger.error(f"Error getting personal timeline for pregnancy {pregnancy_id}: {e}")
            return PersonalTimelineResponse(
                posts=[], milestones_coming_up=[], total_count=0, has_more=False
            )
    
    async def calculate_engagement_score(
        self,
        session: Session,
        post: Post,
        user_id: str,
        pregnancy_id: str
    ) -> FamilyEngagementStats:
        """Calculate family engagement statistics for a post."""
        try:
            # Get family members for this pregnancy
            family_members = await family_member_service.get_pregnancy_members(
                session, pregnancy_id
            )
            family_member_ids = [member.user_id for member in family_members]
            
            # Get reactions from family members
            family_reactions = await self._get_family_reactions(
                session, post.id, family_member_ids
            )
            
            # Get comments from family members
            family_comments = await self._get_family_comments(
                session, post.id, family_member_ids
            )
            
            # Get views from family members
            family_views = await self._get_family_views(
                session, post.id, family_member_ids
            )
            
            # Determine if post needs family response
            needs_response = self._needs_family_response(post)
            
            # Determine if post is celebration-worthy
            celebration_worthy = self._is_celebration_worthy(post)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                len(family_reactions), len(family_comments), family_views,
                len(family_member_ids), post.created_at
            )
            
            return FamilyEngagementStats(
                family_member_reactions=len(family_reactions),
                family_member_comments=len(family_comments),
                family_member_views=family_views,
                needs_family_response=needs_response,
                celebration_worthy=celebration_worthy,
                engagement_score=engagement_score
            )
            
        except Exception as e:
            logger.error(f"Error calculating engagement score for post {post.id}: {e}")
            return FamilyEngagementStats(
                family_member_reactions=0,
                family_member_comments=0,
                family_member_views=0,
                needs_family_response=False,
                celebration_worthy=False,
                engagement_score=0.0
            )
    
    async def get_trending_posts(
        self,
        session: Session,
        pregnancy_id: str,
        limit: int = 10
    ) -> List[str]:
        """Get post IDs that are trending in the family."""
        try:
            # Get posts with high recent engagement
            cutoff_time = datetime.utcnow() - timedelta(days=3)
            
            # Query for posts with recent activity
            trending_query = select(Post).where(
                and_(
                    Post.pregnancy_id == pregnancy_id,
                    Post.status == PostStatus.PUBLISHED,
                    Post.created_at >= cutoff_time
                )
            ).order_by(
                (Post.reaction_count + Post.comment_count * 2).desc()
            ).limit(limit)
            
            trending_posts = session.exec(trending_query).all()
            return [post.id for post in trending_posts]
            
        except Exception as e:
            logger.error(f"Error getting trending posts for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def _user_has_access(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str
    ) -> bool:
        """Check if user has access to pregnancy content."""
        # Check if user owns the pregnancy
        if await pregnancy_service.user_owns_pregnancy(session, user_id, pregnancy_id):
            return True
        
        # Check if user is a family member
        memberships = await family_member_service.get_user_memberships(
            session, user_id, pregnancy_id
        )
        return len(memberships) > 0
    
    async def _build_family_feed_query(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest,
        family_memberships: List[FamilyMember]
    ):
        """Build optimized query for family feed with pagination at DB level."""
        from app.models.user import User
        from app.models.content import MediaItem
        
        # Build main query with joins to avoid N+1 queries
        query = select(
            Post,
            User.first_name.label('author_first_name'),
            User.last_name.label('author_last_name'),
            User.profile_image.label('author_profile_image'),
            User.email.label('author_email'),
            func.count(Reaction.id).label('reaction_count'),
            func.count(Comment.id).label('comment_count')
        ).select_from(Post).join(
            User, Post.author_id == User.id
        ).outerjoin(
            Reaction, and_(Reaction.post_id == Post.id, Reaction.deleted_at.is_(None))
        ).outerjoin(
            Comment, and_(Comment.post_id == Post.id, Comment.deleted_at.is_(None))
        ).where(
            and_(
                Post.pregnancy_id == pregnancy_id,
                Post.status == PostStatus.PUBLISHED,
                Post.deleted_at.is_(None)
            )
        ).group_by(
            Post.id, User.id
        )
        
        # Apply time filter if specified
        if feed_request.since:
            query = query.where(Post.created_at >= feed_request.since)
        
        # Apply content type filter
        if feed_request.filter_type != FeedFilterType.ALL:
            post_types = self._get_post_types_for_filter(feed_request.filter_type)
            if post_types:
                query = query.where(Post.type.in_(post_types))
        
        return query
    
    def _apply_feed_sorting(self, query, sort_type: FeedSortType):
        """Apply sorting to the feed query."""
        if sort_type == FeedSortType.CHRONOLOGICAL:
            return query.order_by(Post.created_at.desc())
        elif sort_type == FeedSortType.ENGAGEMENT:
            return query.order_by(
                (Post.reaction_count + Post.comment_count * 2).desc(),
                Post.created_at.desc()
            )
        elif sort_type == FeedSortType.MILESTONE_FIRST:
            return query.order_by(
                (Post.type == PostType.MILESTONE).desc(),
                Post.created_at.desc()
            )
        else:
            return query.order_by(Post.created_at.desc())
    
    def _get_post_types_for_filter(self, filter_type: FeedFilterType) -> List[PostType]:
        """Get post types for a given filter."""
        filter_mapping = {
            FeedFilterType.MILESTONES: [PostType.MILESTONE],
            FeedFilterType.PHOTOS: [PostType.BELLY_PHOTO, PostType.ULTRASOUND],
            FeedFilterType.UPDATES: [PostType.WEEKLY_UPDATE, PostType.APPOINTMENT],
            FeedFilterType.CELEBRATIONS: [PostType.CELEBRATION, PostType.ANNOUNCEMENT],
            FeedFilterType.QUESTIONS: [PostType.QUESTION],
        }
        return filter_mapping.get(filter_type, [])
    
    async def _enrich_post_for_feed(
        self,
        session: Session,
        post: Post,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest
    ) -> EnrichedPost:
        """Enrich a post with additional context for feed display."""
        # Convert SQLModel instance to dict properly
        enriched_data = post.dict()
        # Ensure all required fields are present
        enriched_data['id'] = post.id
        enriched_data['created_at'] = post.created_at
        enriched_data['updated_at'] = post.updated_at
        
        # Add author information
        author_info = await self._get_author_info(session, post.author_id)
        enriched_data["author"] = author_info
        
        # Add pregnancy context
        pregnancy_context = await self._get_pregnancy_context(session, post, pregnancy_id)
        enriched_data["pregnancy_context"] = pregnancy_context
        
        # Add reaction summary if requested
        if feed_request.include_reactions:
            reaction_summary = await self._get_reaction_summary(session, post.id, user_id)
            enriched_data["reaction_summary"] = reaction_summary
        
        # Add comment preview if requested
        if feed_request.include_comments:
            comment_preview = await self._get_comment_preview(session, post.id, user_id)
            enriched_data["comment_preview"] = comment_preview
        
        # Calculate engagement stats
        engagement_stats = await self.calculate_engagement_score(
            session, post, user_id, pregnancy_id
        )
        enriched_data["engagement_stats"] = engagement_stats
        
        # Add media items if requested
        if feed_request.include_media:
            from app.services.post_service import media_item_service
            media_items = await media_item_service.get_post_media(session, post.id)
            enriched_data["media_items"] = [item.dict() for item in media_items]
        
        # Determine if post is trending
        trending_posts = await self.get_trending_posts(session, pregnancy_id)
        enriched_data["is_trending"] = post.id in trending_posts
        
        # Other flags
        enriched_data["is_pinned"] = False  # Could be determined by family group settings
        enriched_data["requires_attention"] = engagement_stats.needs_family_response
        
        return EnrichedPost(**enriched_data)
    
    async def _batch_enrich_posts_for_feed(
        self,
        session: Session,
        posts_with_metadata: List,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest
    ) -> List[EnrichedPost]:
        """Batch enrich posts to avoid N+1 queries."""
        if not posts_with_metadata:
            return []
        
        enriched_posts = []
        post_ids = []
        
        # Extract posts and metadata from joined results
        posts_data = {}
        for row in posts_with_metadata:
            # Handle SQLAlchemy row result
            if hasattr(row, '_mapping'):
                mapping = row._mapping
                post = mapping['Post']
                post_ids.append(post.id)
                posts_data[post.id] = {
                    'post': post,
                    'author': {
                        'id': post.author_id,
                        'first_name': mapping.get('author_first_name'),
                        'last_name': mapping.get('author_last_name'),
                        'profile_image': mapping.get('author_profile_image'),
                        'email': mapping.get('author_email')
                    },
                    'reaction_count': mapping.get('reaction_count', 0),
                    'comment_count': mapping.get('comment_count', 0)
                }
            else:
                # Fallback for other result types
                post = row[0] if isinstance(row, tuple) else row
                post_ids.append(post.id)
                posts_data[post.id] = {
                    'post': post,
                    'author': None,
                    'reaction_count': 0,
                    'comment_count': 0
                }
        
        # Batch fetch reactions for all posts
        reactions_query = select(Reaction).where(
            and_(
                Reaction.post_id.in_(post_ids),
                Reaction.deleted_at.is_(None)
            )
        )
        all_reactions = session.exec(reactions_query).all()
        reactions_by_post = defaultdict(list)
        for reaction in all_reactions:
            reactions_by_post[reaction.post_id].append(reaction)
        
        # Batch fetch comments for all posts (if needed)
        comments_by_post = {}
        if feed_request.include_comments:
            comments_query = select(Comment).where(
                and_(
                    Comment.post_id.in_(post_ids),
                    Comment.deleted_at.is_(None)
                )
            ).order_by(Comment.created_at.desc())
            all_comments = session.exec(comments_query).all()
            comments_by_post = defaultdict(list)
            for comment in all_comments:
                comments_by_post[comment.post_id].append(comment)
        
        # Batch fetch media items (if needed)
        media_by_post = {}
        if feed_request.include_media:
            from app.services.post_service import media_item_service
            # Get media for all posts at once
            for post_id in post_ids:
                media_items = await media_item_service.get_post_media(session, post_id)
                media_by_post[post_id] = [item.dict() for item in media_items]
        
        # Get trending posts once
        trending_posts = await self.get_trending_posts(session, pregnancy_id)
        
        # Process each post with pre-fetched data
        for post_id, data in posts_data.items():
            post = data['post']
            # Convert SQLModel instance to dict properly
            enriched_data = post.dict()
            # Ensure all required fields are present
            enriched_data['id'] = post.id
            enriched_data['created_at'] = post.created_at
            enriched_data['updated_at'] = post.updated_at
            
            # Add author from joined data
            enriched_data["author"] = data['author']
            
            # Add pregnancy context
            pregnancy_context = await self._get_pregnancy_context(session, post, pregnancy_id)
            enriched_data["pregnancy_context"] = pregnancy_context
            
            # Add reaction summary from batch data
            if feed_request.include_reactions:
                post_reactions = reactions_by_post.get(post_id, [])
                reaction_summary = self._build_reaction_summary(post_reactions, user_id)
                enriched_data["reaction_summary"] = reaction_summary
            
            # Add comment preview from batch data
            if feed_request.include_comments:
                post_comments = comments_by_post.get(post_id, [])
                comment_preview = self._build_comment_preview(post_comments, user_id)
                enriched_data["comment_preview"] = comment_preview
            
            # Calculate engagement stats
            engagement_stats = await self.calculate_engagement_score(
                session, post, user_id, pregnancy_id
            )
            enriched_data["engagement_stats"] = engagement_stats
            
            # Add media items from batch data
            if feed_request.include_media:
                enriched_data["media_items"] = media_by_post.get(post_id, [])
            
            # Add flags
            enriched_data["is_trending"] = post_id in trending_posts
            enriched_data["is_pinned"] = False
            enriched_data["requires_attention"] = engagement_stats.needs_family_response
            
            # Update counts from joined data
            enriched_data["reaction_count"] = data['reaction_count']
            enriched_data["comment_count"] = data['comment_count']
            
            enriched_posts.append(EnrichedPost(**enriched_data))
        
        return enriched_posts
    
    def _build_reaction_summary(self, reactions: List[Reaction], user_id: str) -> ReactionSummary:
        """Build reaction summary from reaction list."""
        reaction_counts = defaultdict(int)
        user_reaction = None
        recent_reactors = []
        
        for reaction in reactions:
            reaction_counts[reaction.type] += 1
            if reaction.user_id == user_id:
                user_reaction = reaction.type
            recent_reactors.append(reaction.user_id)
        
        return ReactionSummary(
            total_count=len(reactions),
            reaction_counts=dict(reaction_counts),
            user_reaction=user_reaction,
            recent_reactors=recent_reactors[-5:]
        )
    
    def _build_comment_preview(self, comments: List[Comment], user_id: str) -> CommentPreview:
        """Build comment preview from comment list."""
        has_user_commented = any(comment.user_id == user_id for comment in comments)
        
        recent_comments = []
        for comment in comments[-3:]:  # Last 3 comments
            recent_comments.append({
                "id": comment.id,
                "content": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                "user_id": comment.user_id,
                "created_at": comment.created_at
            })
        
        return CommentPreview(
            total_count=len(comments),
            recent_comments=recent_comments,
            has_user_commented=has_user_commented
        )
    
    async def _enrich_post_for_personal_timeline(
        self,
        session: Session,
        post: Post,
        user_id: str,
        pregnancy_id: str,
        feed_request: FeedRequest
    ) -> EnrichedPost:
        """Enrich a post specifically for personal timeline view."""
        # Similar to feed enrichment but with personal context
        return await self._enrich_post_for_feed(
            session, post, user_id, pregnancy_id, feed_request
        )
    
    async def _get_author_info(
        self,
        session: Session,
        author_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get author information for a post."""
        try:
            from app.services.user_service import user_service
            author = await user_service.get_by_id(session, author_id)
            if not author:
                return None
            
            return {
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
                "profile_image": author.profile_image,
                "email": author.email
            }
        except Exception as e:
            logger.error(f"Error getting author info for user {author_id}: {e}")
            return None

    async def _get_pregnancy_context(
        self,
        session: Session,
        post: Post,
        pregnancy_id: str
    ) -> PregnancyContext:
        """Get pregnancy-specific context for a post."""
        try:
            # Get pregnancy info
            pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
            if not pregnancy:
                return PregnancyContext(days_since_post=0)
            
            # Calculate current week and trimester from pregnancy details
            current_week = None
            trimester = None
            
            # Access pregnancy details from the JSONB field
            if hasattr(pregnancy, 'pregnancy_details') and pregnancy.pregnancy_details:
                details = pregnancy.pregnancy_details
                due_date = getattr(details, 'due_date', None) if hasattr(details, 'due_date') else None
                conception_date = getattr(details, 'conception_date', None) if hasattr(details, 'conception_date') else None
                
                # Use current_week and trimester if already calculated and stored
                if hasattr(details, 'current_week') and details.current_week:
                    current_week = details.current_week
                    trimester = getattr(details, 'trimester', None) if hasattr(details, 'trimester') else None
                elif due_date or conception_date:
                    # Calculate from dates if not pre-calculated
                    if conception_date:
                        from datetime import date
                        if isinstance(conception_date, str):
                            from datetime import datetime
                            conception_date = datetime.fromisoformat(conception_date).date()
                        days_pregnant = (datetime.utcnow().date() - conception_date).days
                        current_week = min(40, max(1, days_pregnant // 7))
                    elif due_date:
                        # Calculate from due date (40 weeks = 280 days)
                        from datetime import date
                        if isinstance(due_date, str):
                            from datetime import datetime
                            due_date = datetime.fromisoformat(due_date).date()
                        days_left = (due_date - datetime.utcnow().date()).days
                        current_week = min(40, max(1, 40 - (days_left // 7)))
                    
                    if current_week:
                        trimester = 1 if current_week <= 12 else (2 if current_week <= 27 else 3)
            
            days_since_post = (datetime.utcnow() - post.created_at).days
            is_milestone_week = current_week and current_week in [4, 8, 12, 16, 20, 24, 28, 32, 36, 40]
            
            return PregnancyContext(
                current_week=current_week,
                trimester=trimester,
                days_since_post=days_since_post,
                is_milestone_week=is_milestone_week,
                baby_development=self._get_baby_development_info(current_week) if current_week else None
            )
            
        except Exception as e:
            logger.error(f"Error getting pregnancy context: {e}")
            return PregnancyContext(days_since_post=0)
    
    async def _get_reaction_summary(
        self,
        session: Session,
        post_id: str,
        user_id: str
    ) -> ReactionSummary:
        """Get reaction summary for a post."""
        try:
            reactions = await reaction_service.get_post_reactions(session, post_id)
            
            # Count reactions by type
            reaction_counts = defaultdict(int)
            user_reaction = None
            recent_reactors = []
            
            for reaction in reactions:
                reaction_counts[reaction.type] += 1
                if reaction.user_id == user_id:
                    user_reaction = reaction.type
                recent_reactors.append(reaction.user_id)
            
            return ReactionSummary(
                total_count=len(reactions),
                reaction_counts=dict(reaction_counts),
                user_reaction=user_reaction,
                recent_reactors=recent_reactors[-5:]  # Last 5 reactors
            )
            
        except Exception as e:
            logger.error(f"Error getting reaction summary for post {post_id}: {e}")
            return ReactionSummary(
                total_count=0,
                reaction_counts={},
                recent_reactors=[]
            )
    
    async def _get_comment_preview(
        self,
        session: Session,
        post_id: str,
        user_id: str
    ) -> CommentPreview:
        """Get comment preview for a post."""
        try:
            comments = await comment_service.get_post_comments(session, post_id)
            
            # Check if user has commented
            has_user_commented = any(comment.user_id == user_id for comment in comments)
            
            # Get recent comments (simplified)
            recent_comments = []
            for comment in comments[-3:]:  # Last 3 comments
                recent_comments.append({
                    "id": comment.id,
                    "content": comment.content[:100] + "..." if len(comment.content) > 100 else comment.content,
                    "user_id": comment.user_id,
                    "created_at": comment.created_at
                })
            
            return CommentPreview(
                total_count=len(comments),
                recent_comments=recent_comments,
                has_user_commented=has_user_commented
            )
            
        except Exception as e:
            logger.error(f"Error getting comment preview for post {post_id}: {e}")
            return CommentPreview(
                total_count=0,
                recent_comments=[],
                has_user_commented=False
            )
    
    async def _get_family_reactions(
        self,
        session: Session,
        post_id: str,
        family_member_ids: List[str]
    ) -> List[Reaction]:
        """Get reactions from family members."""
        try:
            all_reactions = await reaction_service.get_post_reactions(session, post_id)
            return [r for r in all_reactions if r.user_id in family_member_ids]
        except Exception:
            return []
    
    async def _get_family_comments(
        self,
        session: Session,
        post_id: str,
        family_member_ids: List[str]
    ) -> List[Comment]:
        """Get comments from family members."""
        try:
            all_comments = await comment_service.get_post_comments(session, post_id)
            return [c for c in all_comments if c.user_id in family_member_ids]
        except Exception:
            return []
    
    async def _get_family_views(
        self,
        session: Session,
        post_id: str,
        family_member_ids: List[str]
    ) -> int:
        """Get view count from family members."""
        try:
            # This would query PostView table filtered by family members
            # Simplified for now
            return 0
        except Exception:
            return 0
    
    def _needs_family_response(self, post: Post) -> bool:
        """Determine if a post needs family response."""
        # Check if it's a question or has specific keywords
        needs_response_types = [PostType.QUESTION, PostType.APPOINTMENT]
        if post.type in needs_response_types:
            return True
        
        # Check content for question indicators
        if hasattr(post.content, 'text') and post.content.text:
            question_indicators = ['?', 'what do you think', 'advice', 'opinion', 'should i']
            text_lower = post.content.text.lower()
            return any(indicator in text_lower for indicator in question_indicators)
        
        return False
    
    def _is_celebration_worthy(self, post: Post) -> bool:
        """Determine if a post is celebration-worthy."""
        celebration_types = [
            PostType.MILESTONE, PostType.ANNOUNCEMENT, 
            PostType.CELEBRATION, PostType.ULTRASOUND
        ]
        return post.type in celebration_types
    
    def _calculate_engagement_score(
        self,
        reactions: int,
        comments: int,
        views: int,
        family_size: int,
        created_at: datetime
    ) -> float:
        """Calculate engagement score for a post."""
        if family_size == 0:
            return 0.0
        
        # Base engagement score
        base_score = (reactions * 3 + comments * 5 + views) / family_size
        
        # Time decay factor (newer posts get slight boost)
        days_old = (datetime.utcnow() - created_at).days
        time_factor = max(0.5, 1.0 - (days_old * 0.1))
        
        # Normalize to 0-100 scale
        final_score = min(100.0, base_score * time_factor * 10)
        
        return round(final_score, 2)
    
    def _get_baby_development_info(self, week: int) -> str:
        """Get baby development information for a given week."""
        # Simplified development info - in reality, this would be a comprehensive database
        development_info = {
            4: "Your baby is the size of a poppy seed",
            8: "Your baby is the size of a raspberry",
            12: "Your baby is the size of a plum",
            16: "Your baby is the size of an avocado",
            20: "Your baby is the size of a banana",
            24: "Your baby is the size of an ear of corn",
            28: "Your baby is the size of an eggplant",
            32: "Your baby is the size of a jicama",
            36: "Your baby is the size of a romaine lettuce head",
            40: "Your baby is full term and ready to meet the world!"
        }
        return development_info.get(week, f"Week {week} of pregnancy")
    
    async def _get_pregnancy_summary(
        self,
        session: Session,
        pregnancy_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get pregnancy summary for feed context."""
        try:
            pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
            if not pregnancy:
                return None
            
            # Calculate basic stats from pregnancy details
            current_week = None
            due_date = None
            trimester = None
            
            if hasattr(pregnancy, 'pregnancy_details') and pregnancy.pregnancy_details:
                details = pregnancy.pregnancy_details
                due_date = getattr(details, 'due_date', None) if hasattr(details, 'due_date') else None
                conception_date = getattr(details, 'conception_date', None) if hasattr(details, 'conception_date') else None
                
                # Use stored values if available
                if hasattr(details, 'current_week') and details.current_week:
                    current_week = details.current_week
                    trimester = getattr(details, 'trimester', None) if hasattr(details, 'trimester') else None
                elif conception_date:
                    # Calculate from conception date
                    if isinstance(conception_date, str):
                        from datetime import datetime
                        conception_date = datetime.fromisoformat(conception_date).date()
                    days_pregnant = (datetime.utcnow().date() - conception_date).days
                    current_week = min(40, max(1, days_pregnant // 7))
                    
                if current_week and not trimester:
                    trimester = 1 if current_week <= 12 else (2 if current_week <= 27 else 3)
            
            return {
                "id": pregnancy.id,
                "current_week": current_week,
                "due_date": due_date.isoformat() if due_date else None,
                "trimester": trimester
            }
            
        except Exception as e:
            logger.error(f"Error getting pregnancy summary: {e}")
            return None
    
    async def _generate_feed_metadata(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        posts: List[EnrichedPost]
    ) -> Dict[str, Any]:
        """Generate metadata for the feed."""
        try:
            # Calculate feed stats
            total_reactions = sum(post.reaction_count for post in posts)
            total_comments = sum(post.comment_count for post in posts)
            
            # Get post type distribution
            post_types = defaultdict(int)
            for post in posts:
                post_types[post.type.value] += 1
            
            return {
                "total_reactions": total_reactions,
                "total_comments": total_comments,
                "post_type_distribution": dict(post_types),
                "feed_generated_at": datetime.utcnow(),
                "user_id": user_id,
                "pregnancy_id": pregnancy_id
            }
            
        except Exception:
            return {}
    
    async def _get_upcoming_milestones(
        self,
        session: Session,
        pregnancy_id: str
    ) -> List[Dict[str, Any]]:
        """Get upcoming pregnancy milestones."""
        try:
            # This would typically query a milestones table or service
            # Simplified for now
            pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
            if not pregnancy:
                return []
            
            # Check if pregnancy has details
            has_due_date = False
            if hasattr(pregnancy, 'pregnancy_details') and pregnancy.pregnancy_details:
                details = pregnancy.pregnancy_details
                due_date = getattr(details, 'due_date', None) if hasattr(details, 'due_date') else None
                has_due_date = due_date is not None
            
            if not has_due_date:
                return []
            
            # Calculate upcoming milestones based on current week
            milestones = [
                {"week": 12, "title": "End of first trimester", "description": "Risk of miscarriage decreases significantly"},
                {"week": 20, "title": "Anatomy scan", "description": "Detailed ultrasound to check baby's development"},
                {"week": 28, "title": "Third trimester begins", "description": "Baby's survival chances increase dramatically"},
                {"week": 36, "title": "Baby is full term soon", "description": "Baby's lungs are nearly fully developed"},
                {"week": 40, "title": "Due date", "description": "Your baby is ready to meet the world!"}
            ]
            
            return milestones[:3]  # Return next 3 milestones
            
        except Exception:
            return []
    
    async def _get_weekly_progress(
        self,
        session: Session,
        pregnancy_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get weekly pregnancy progress."""
        try:
            pregnancy = await pregnancy_service.get_by_id(session, pregnancy_id)
            if not pregnancy:
                return None
            
            current_week = None
            if hasattr(pregnancy, 'pregnancy_details') and pregnancy.pregnancy_details:
                details = pregnancy.pregnancy_details
                conception_date = getattr(details, 'conception_date', None) if hasattr(details, 'conception_date') else None
                
                # Use stored current_week if available
                if hasattr(details, 'current_week') and details.current_week:
                    current_week = details.current_week
                elif conception_date:
                    # Calculate from conception date
                    if isinstance(conception_date, str):
                        from datetime import datetime
                        conception_date = datetime.fromisoformat(conception_date).date()
                    days_pregnant = (datetime.utcnow().date() - conception_date).days
                    current_week = min(40, max(1, days_pregnant // 7))
            
            if not current_week:
                return None
            
            return {
                "current_week": current_week,
                "total_weeks": 40,
                "progress_percentage": (current_week / 40) * 100,
                "baby_development": self._get_baby_development_info(current_week),
                "trimester": 1 if current_week <= 12 else (2 if current_week <= 27 else 3)
            }
            
        except Exception:
            return None


# Global service instance
feed_service = FeedService()