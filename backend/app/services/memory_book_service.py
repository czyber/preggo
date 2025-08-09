"""
Memory book service for the Preggo app overhaul.
Handles automatic curation of pregnancy memories and family collaboration.
Creates meaningful collections of moments for long-term preservation.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, and_, or_, func
from datetime import datetime, timedelta
from app.models.enhanced_content import (
    MemoryBookItem, MemoryCollection, FamilyMemoryContribution,
    MemoryType
)
from app.models.content import Post, PostType, MediaItem
from app.models.milestone import Milestone
from app.services.base import BaseService
import logging
import re

logger = logging.getLogger(__name__)


class MemoryCurationEngine:
    """
    Intelligent memory curation engine that automatically identifies
    significant moments and suggests memory book additions.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def analyze_post_for_memory_potential(self, post_id: str) -> Tuple[bool, float, List[str]]:
        """
        Analyze a post to determine if it should be automatically curated as a memory.
        Returns (should_curate, confidence_score, reasons)
        """
        try:
            post = self.session.exec(select(Post).where(Post.id == post_id)).first()
            if not post:
                return False, 0.0, []
            
            confidence_score = 0.0
            curation_reasons = []
            
            # High-value post types automatically get higher scores
            high_value_types = {
                PostType.MILESTONE: 0.8,
                PostType.ULTRASOUND: 0.9,
                PostType.ANNOUNCEMENT: 0.85,
                PostType.BELLY_PHOTO: 0.6,
                PostType.CELEBRATION: 0.75
            }
            
            if post.type in high_value_types:
                confidence_score += high_value_types[post.type]
                curation_reasons.append(f"Important post type: {post.type.value}")
            
            # Analyze post content for memory-worthy indicators
            content_score, content_reasons = self._analyze_content_significance(post)
            confidence_score += content_score
            curation_reasons.extend(content_reasons)
            
            # Check family engagement (warmth score indicates importance to family)
            if post.family_warmth_score >= 0.7:
                confidence_score += 0.2
                curation_reasons.append("High family engagement and warmth")
            elif post.family_warmth_score >= 0.5:
                confidence_score += 0.1
                curation_reasons.append("Good family engagement")
            
            # Check for media attachments (photos/videos are memory-worthy)
            media_items = self.session.exec(
                select(MediaItem).where(MediaItem.post_id == post_id)
            ).all()
            
            if len(media_items) >= 3:
                confidence_score += 0.15
                curation_reasons.append("Multiple media items captured")
            elif len(media_items) >= 1:
                confidence_score += 0.1
                curation_reasons.append("Media content included")
            
            # Check pregnancy week significance
            if post.content.week:
                week_score, week_reason = self._analyze_week_significance(post.content.week)
                confidence_score += week_score
                if week_reason:
                    curation_reasons.append(week_reason)
            
            # Normalize score to 0-1 range
            confidence_score = min(confidence_score, 1.0)
            
            # Decision threshold
            should_curate = confidence_score >= 0.6
            
            return should_curate, confidence_score, curation_reasons
            
        except Exception as e:
            logger.error(f"Error analyzing post for memory potential: {e}")
            return False, 0.0, []
    
    def suggest_weekly_memories(self, pregnancy_id: str, week_number: int) -> List[Dict[str, Any]]:
        """
        Suggest memories for a specific week based on posts, milestones, and content.
        """
        try:
            suggestions = []
            
            # Get posts from this week
            week_start = datetime.utcnow() - timedelta(days=7)
            posts = self.session.exec(
                select(Post).where(
                    and_(
                        Post.pregnancy_id == pregnancy_id,
                        Post.created_at >= week_start,
                        Post.status == "published"
                    )
                )
            ).all()
            
            for post in posts:
                should_curate, score, reasons = self.analyze_post_for_memory_potential(post.id)
                if should_curate:
                    suggestions.append({
                        'type': 'post_memory',
                        'source_post_id': post.id,
                        'title': self._generate_memory_title(post),
                        'description': self._generate_memory_description(post),
                        'curation_score': score,
                        'reasons': reasons,
                        'memory_type': self._determine_memory_type_from_post(post),
                        'week_number': week_number
                    })
            
            # Check for completed milestones this week
            milestones = self.session.exec(
                select(Milestone).where(
                    and_(
                        Milestone.pregnancy_id == pregnancy_id,
                        Milestone.week == week_number,
                        Milestone.completed == True,
                        Milestone.completed_at >= week_start
                    )
                )
            ).all()
            
            for milestone in milestones:
                suggestions.append({
                    'type': 'milestone_memory',
                    'source_milestone_id': milestone.id,
                    'title': f"Milestone: {milestone.title}",
                    'description': milestone.description,
                    'curation_score': 0.9,  # Milestones are always high-value memories
                    'reasons': ["Completed pregnancy milestone"],
                    'memory_type': MemoryType.MILESTONE_MOMENT,
                    'week_number': week_number
                })
            
            # Sort by curation score
            suggestions.sort(key=lambda x: x['curation_score'], reverse=True)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting weekly memories: {e}")
            return []
    
    def create_weekly_highlight_collection(self, pregnancy_id: str, week_number: int) -> Optional[MemoryCollection]:
        """
        Automatically create a weekly highlight collection if there are enough memories.
        """
        try:
            # Get memory suggestions for the week
            suggestions = self.suggest_weekly_memories(pregnancy_id, week_number)
            high_quality_suggestions = [s for s in suggestions if s['curation_score'] >= 0.7]
            
            if len(high_quality_suggestions) < 2:
                return None  # Not enough significant content for a weekly collection
            
            # Create memory items for high-quality suggestions
            memory_item_ids = []
            for suggestion in high_quality_suggestions[:5]:  # Limit to top 5
                memory_item = self._create_memory_item_from_suggestion(pregnancy_id, suggestion)
                if memory_item:
                    memory_item_ids.append(memory_item.id)
            
            if not memory_item_ids:
                return None
            
            # Create the weekly collection
            collection = MemoryCollection(
                pregnancy_id=pregnancy_id,
                created_by_user_id="system",  # System-generated
                title=f"Week {week_number} Highlights",
                description=f"Special moments and milestones from pregnancy week {week_number}",
                collection_type="weekly",
                memory_item_ids=memory_item_ids,
                start_week=week_number,
                end_week=week_number,
                auto_generated=True,
                generation_schedule="weekly"
            )
            
            self.session.add(collection)
            self.session.commit()
            self.session.refresh(collection)
            
            return collection
            
        except Exception as e:
            logger.error(f"Error creating weekly highlight collection: {e}")
            return None
    
    def _analyze_content_significance(self, post: Post) -> Tuple[float, List[str]]:
        """Analyze post content for memory significance indicators."""
        if not post.content.text:
            return 0.0, []
        
        content = post.content.text.lower()
        significance_score = 0.0
        reasons = []
        
        # Emotional significance indicators
        emotional_patterns = {
            r'\b(first|finally|amazing|incredible|overwhelming|beautiful|perfect)\b': (0.15, "Contains emotional significance markers"),
            r'\b(love|loved|loving|heart|feel|feeling|felt)\b': (0.1, "Expresses deep emotions"),
            r'\b(excited|thrilled|happy|joy|grateful|blessed)\b': (0.1, "Shows positive emotional state"),
            r'\b(scared|nervous|worried|anxious)\b': (0.08, "Shows vulnerable emotional sharing")
        }
        
        for pattern, (score, reason) in emotional_patterns.items():
            if re.search(pattern, content):
                significance_score += score
                reasons.append(reason)
                break  # Don't double-count similar patterns
        
        # Milestone/achievement indicators
        achievement_patterns = {
            r'\b(milestone|achievement|accomplished|reached|completed)\b': (0.2, "Mentions achievements or milestones"),
            r'\b(first.*time|never.*before|new.*experience)\b': (0.15, "Describes first-time experiences"),
            r'\b(graduation|appointment|scan|ultrasound)\b': (0.15, "References significant events"),
            r'\b(movement|kick|heartbeat|hiccup)\b': (0.15, "Describes baby development experiences")
        }
        
        for pattern, (score, reason) in achievement_patterns.items():
            if re.search(pattern, content):
                significance_score += score
                reasons.append(reason)
                break
        
        # Family/relationship significance
        family_patterns = {
            r'\b(family|together|share|sharing|everyone|celebrate)\b': (0.1, "Includes family in the experience"),
            r'\b(partner|husband|wife|mom|dad|grandma|grandpa)\b': (0.08, "Mentions important family members"),
            r'\b(support|help|there.*for.*me)\b': (0.08, "Acknowledges family support")
        }
        
        for pattern, (score, reason) in family_patterns.items():
            if re.search(pattern, content):
                significance_score += score
                reasons.append(reason)
                break
        
        # Length and thoughtfulness indicators
        if len(content) > 200:
            significance_score += 0.1
            reasons.append("Thoughtful, detailed sharing")
        
        # Question marks indicate engagement/curiosity
        if content.count('?') >= 2:
            significance_score += 0.05
            reasons.append("Engaging with family through questions")
        
        return significance_score, reasons
    
    def _analyze_week_significance(self, week_number: int) -> Tuple[float, Optional[str]]:
        """Analyze if a pregnancy week has special significance."""
        significant_weeks = {
            4: (0.1, "Very early pregnancy confirmation"),
            6: (0.15, "First heartbeat week"),
            8: (0.1, "End of embryonic period"),
            12: (0.2, "End of first trimester"),
            13: (0.15, "Start of second trimester"),
            16: (0.1, "Possible gender determination"),
            18: (0.15, "Anatomy scan week"),
            20: (0.2, "Halfway milestone"),
            24: (0.15, "Viability milestone"),
            28: (0.15, "Start of third trimester"),
            32: (0.1, "Baby development acceleration"),
            36: (0.15, "Early term approaching"),
            37: (0.2, "Full term achieved"),
            40: (0.25, "Due date week"),
            41: (0.15, "Post-due date"),
            42: (0.15, "Extended pregnancy")
        }
        
        if week_number in significant_weeks:
            return significant_weeks[week_number]
        
        return 0.0, None
    
    def _generate_memory_title(self, post: Post) -> str:
        """Generate an appropriate title for a memory based on the post."""
        if post.content.title:
            return post.content.title
        
        # Generate title based on post type
        type_titles = {
            PostType.MILESTONE: "Special Milestone",
            PostType.ULTRASOUND: "Ultrasound Memory",
            PostType.ANNOUNCEMENT: "Big Announcement",
            PostType.BELLY_PHOTO: "Pregnancy Progress",
            PostType.CELEBRATION: "Celebration Moment",
            PostType.WEEKLY_UPDATE: "Weekly Update",
            PostType.APPOINTMENT: "Appointment Day"
        }
        
        base_title = type_titles.get(post.type, "Special Moment")
        
        if post.content.week:
            return f"{base_title} - Week {post.content.week}"
        
        return base_title
    
    def _generate_memory_description(self, post: Post) -> str:
        """Generate a description for a memory based on the post content."""
        if post.content.text and len(post.content.text) <= 200:
            return post.content.text
        elif post.content.text:
            return post.content.text[:200] + "..."
        else:
            return f"A special {post.type.value} moment from your pregnancy journey."
    
    def _determine_memory_type_from_post(self, post: Post) -> MemoryType:
        """Determine the appropriate memory type based on post characteristics."""
        type_mapping = {
            PostType.MILESTONE: MemoryType.MILESTONE_MOMENT,
            PostType.ULTRASOUND: MemoryType.ULTRASOUND_MEMORY,
            PostType.BELLY_PHOTO: MemoryType.BELLY_PHOTO_SERIES,
            PostType.CELEBRATION: MemoryType.CELEBRATION_MEMORY,
            PostType.ANNOUNCEMENT: MemoryType.CELEBRATION_MEMORY,
            PostType.WEEKLY_UPDATE: MemoryType.WEEKLY_HIGHLIGHT,
            PostType.PREPARATION: MemoryType.PREPARATION_MEMORY,
            PostType.SYMPTOM_SHARE: MemoryType.EMOTIONAL_MOMENT
        }
        
        return type_mapping.get(post.type, MemoryType.AUTO_CURATED)
    
    def _create_memory_item_from_suggestion(
        self, 
        pregnancy_id: str, 
        suggestion: Dict[str, Any]
    ) -> Optional[MemoryBookItem]:
        """Create a memory item from a curation suggestion."""
        try:
            memory_item = MemoryBookItem(
                pregnancy_id=pregnancy_id,
                source_post_id=suggestion.get('source_post_id'),
                created_by_user_id="system",
                memory_type=suggestion['memory_type'],
                title=suggestion['title'],
                description=suggestion['description'],
                pregnancy_week=suggestion.get('week_number'),
                memory_date=datetime.utcnow(),
                auto_generated=True,
                curation_score=suggestion['curation_score'],
                curation_reasons=suggestion['reasons'],
                collaborative=True  # Allow family contributions by default
            )
            
            # Add content from the source post if available
            if suggestion.get('source_post_id'):
                post = self.session.exec(
                    select(Post).where(Post.id == suggestion['source_post_id'])
                ).first()
                
                if post:
                    memory_item.content = {
                        'original_post_content': post.content.dict(),
                        'original_post_type': post.type.value,
                        'created_at': post.created_at.isoformat()
                    }
                    
                    # Get associated media
                    media_items = self.session.exec(
                        select(MediaItem).where(MediaItem.post_id == post.id)
                    ).all()
                    
                    memory_item.media_items = [media.id for media in media_items]
            
            self.session.add(memory_item)
            self.session.commit()
            self.session.refresh(memory_item)
            
            return memory_item
            
        except Exception as e:
            logger.error(f"Error creating memory item from suggestion: {e}")
            return None


class MemoryBookService(BaseService):
    """
    Service for managing the pregnancy memory book system.
    """
    
    def __init__(self):
        super().__init__(MemoryBookItem)
    
    def auto_curate_post_memory(
        self,
        session: Session,
        post_id: str,
        user_id: str
    ) -> Optional[MemoryBookItem]:
        """
        Automatically curate a post as a memory if it meets criteria.
        """
        try:
            engine = MemoryCurationEngine(session)
            should_curate, score, reasons = engine.analyze_post_for_memory_potential(post_id)
            
            if not should_curate:
                return None
            
            # Get post details
            post = session.exec(select(Post).where(Post.id == post_id)).first()
            if not post:
                return None
            
            # Create memory item
            memory_item = MemoryBookItem(
                pregnancy_id=post.pregnancy_id,
                source_post_id=post_id,
                created_by_user_id=user_id,
                memory_type=engine._determine_memory_type_from_post(post),
                title=engine._generate_memory_title(post),
                description=engine._generate_memory_description(post),
                pregnancy_week=post.content.week,
                memory_date=post.created_at,
                auto_generated=True,
                curation_score=score,
                curation_reasons=reasons,
                collaborative=True
            )
            
            # Add post content to memory
            memory_item.content = {
                'original_post_content': post.content.dict(),
                'original_post_type': post.type.value,
                'family_warmth_score': post.family_warmth_score
            }
            
            # Get associated media
            media_items = session.exec(
                select(MediaItem).where(MediaItem.post_id == post_id)
            ).all()
            memory_item.media_items = [media.id for media in media_items]
            
            session.add(memory_item)
            session.commit()
            session.refresh(memory_item)
            
            return memory_item
            
        except Exception as e:
            logger.error(f"Error auto-curating post memory: {e}")
            return None
    
    def create_manual_memory(
        self,
        session: Session,
        pregnancy_id: str,
        user_id: str,
        title: str,
        description: str,
        memory_type: MemoryType,
        memory_date: datetime,
        content: Optional[Dict[str, Any]] = None,
        media_items: Optional[List[str]] = None,
        pregnancy_week: Optional[int] = None
    ) -> Optional[MemoryBookItem]:
        """
        Create a manual memory item.
        """
        try:
            memory_item = MemoryBookItem(
                pregnancy_id=pregnancy_id,
                created_by_user_id=user_id,
                memory_type=memory_type,
                title=title,
                description=description,
                pregnancy_week=pregnancy_week,
                memory_date=memory_date,
                content=content or {},
                media_items=media_items or [],
                auto_generated=False,
                curation_score=0.8,  # Manual memories are considered high-value
                curation_reasons=["Manually created by user"],
                collaborative=True
            )
            
            session.add(memory_item)
            session.commit()
            session.refresh(memory_item)
            
            return memory_item
            
        except Exception as e:
            logger.error(f"Error creating manual memory: {e}")
            return None
    
    def add_family_contribution(
        self,
        session: Session,
        memory_item_id: str,
        contributor_user_id: str,
        contribution_type: str,
        content: str,
        relationship: str,
        media_items: Optional[List[str]] = None
    ) -> Optional[FamilyMemoryContribution]:
        """
        Add a family member's contribution to a memory.
        """
        try:
            # Verify the memory exists and allows collaboration
            memory_item = session.exec(
                select(MemoryBookItem).where(MemoryBookItem.id == memory_item_id)
            ).first()
            
            if not memory_item or not memory_item.collaborative:
                logger.error(f"Memory item {memory_item_id} not found or not collaborative")
                return None
            
            contribution = FamilyMemoryContribution(
                memory_item_id=memory_item_id,
                contributor_user_id=contributor_user_id,
                contribution_type=contribution_type,
                content=content,
                relationship_to_pregnant_person=relationship,
                media_items=media_items or []
            )
            
            session.add(contribution)
            
            # Update the memory item's family contributions
            if not memory_item.family_contributions:
                memory_item.family_contributions = []
            
            memory_item.family_contributions.append({
                'contributor_id': contributor_user_id,
                'contribution_type': contribution_type,
                'content_preview': content[:100] + "..." if len(content) > 100 else content,
                'relationship': relationship,
                'added_at': datetime.utcnow().isoformat()
            })
            
            session.add(memory_item)
            session.commit()
            session.refresh(contribution)
            
            return contribution
            
        except Exception as e:
            logger.error(f"Error adding family contribution: {e}")
            return None
    
    def get_memory_book_for_pregnancy(
        self,
        session: Session,
        pregnancy_id: str,
        limit: Optional[int] = None,
        memory_type: Optional[MemoryType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all memories for a pregnancy, formatted for display.
        """
        try:
            query = select(MemoryBookItem).where(
                MemoryBookItem.pregnancy_id == pregnancy_id
            )
            
            if memory_type:
                query = query.where(MemoryBookItem.memory_type == memory_type)
            
            query = query.order_by(MemoryBookItem.memory_date.desc())
            
            if limit:
                query = query.limit(limit)
            
            memory_items = session.exec(query).all()
            
            formatted_memories = []
            for memory in memory_items:
                # Get family contributions
                contributions = session.exec(
                    select(FamilyMemoryContribution).where(
                        FamilyMemoryContribution.memory_item_id == memory.id
                    )
                ).all()
                
                formatted_memory = {
                    'id': memory.id,
                    'title': memory.title,
                    'description': memory.description,
                    'memory_type': memory.memory_type.value,
                    'pregnancy_week': memory.pregnancy_week,
                    'memory_date': memory.memory_date.isoformat(),
                    'content': memory.content,
                    'media_items': memory.media_items,
                    'tags': memory.tags,
                    'is_favorite': memory.is_favorite,
                    'auto_generated': memory.auto_generated,
                    'curation_score': memory.curation_score,
                    'collaborative': memory.collaborative,
                    'family_contributions_count': len(contributions),
                    'family_contributions': [
                        {
                            'id': contrib.id,
                            'contributor_user_id': contrib.contributor_user_id,
                            'contribution_type': contrib.contribution_type,
                            'content': contrib.content,
                            'relationship': contrib.relationship_to_pregnant_person,
                            'created_at': contrib.created_at.isoformat()
                        }
                        for contrib in contributions
                    ],
                    'created_at': memory.created_at.isoformat(),
                    'updated_at': memory.updated_at.isoformat()
                }
                
                formatted_memories.append(formatted_memory)
            
            return formatted_memories
            
        except Exception as e:
            logger.error(f"Error getting memory book for pregnancy: {e}")
            return []
    
    def generate_weekly_memory_collections(
        self,
        session: Session,
        pregnancy_id: str,
        start_week: int = 1,
        end_week: int = 42
    ) -> List[MemoryCollection]:
        """
        Generate weekly memory collections for a pregnancy.
        """
        try:
            created_collections = []
            engine = MemoryCurationEngine(session)
            
            for week in range(start_week, end_week + 1):
                collection = engine.create_weekly_highlight_collection(pregnancy_id, week)
                if collection:
                    created_collections.append(collection)
            
            return created_collections
            
        except Exception as e:
            logger.error(f"Error generating weekly memory collections: {e}")
            return []
    
    def get_memory_collections(
        self,
        session: Session,
        pregnancy_id: str,
        collection_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get memory collections for a pregnancy.
        """
        try:
            query = select(MemoryCollection).where(
                MemoryCollection.pregnancy_id == pregnancy_id
            )
            
            if collection_type:
                query = query.where(MemoryCollection.collection_type == collection_type)
            
            query = query.order_by(MemoryCollection.created_at.desc())
            collections = session.exec(query).all()
            
            formatted_collections = []
            for collection in collections:
                # Get memory items in this collection
                memory_items = []
                if collection.memory_item_ids:
                    memory_items_query = select(MemoryBookItem).where(
                        MemoryBookItem.id.in_(collection.memory_item_ids)
                    )
                    memory_items = list(session.exec(memory_items_query).all())
                
                formatted_collection = {
                    'id': collection.id,
                    'title': collection.title,
                    'description': collection.description,
                    'collection_type': collection.collection_type,
                    'start_week': collection.start_week,
                    'end_week': collection.end_week,
                    'memory_count': len(memory_items),
                    'memory_items': [
                        {
                            'id': item.id,
                            'title': item.title,
                            'memory_type': item.memory_type.value,
                            'pregnancy_week': item.pregnancy_week,
                            'memory_date': item.memory_date.isoformat()
                        }
                        for item in memory_items
                    ],
                    'is_shared': collection.is_shared,
                    'auto_generated': collection.auto_generated,
                    'created_at': collection.created_at.isoformat(),
                    'updated_at': collection.updated_at.isoformat()
                }
                
                formatted_collections.append(formatted_collection)
            
            return formatted_collections
            
        except Exception as e:
            logger.error(f"Error getting memory collections: {e}")
            return []


# Global service instance
memory_book_service = MemoryBookService()