"""
Content management service for the Preggo app overhaul.
Handles personalized content delivery, medical review workflow, and content adaptation.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, and_, or_
from datetime import datetime, timedelta
from app.models.enhanced_content import (
    PregnancyContent, ContentCategory, BabyDevelopmentContent,
    UserContentPreferences, ContentDeliveryLog, ContentType,
    ContentDeliveryMethod, MedicalReviewStatus, PersonalizationContext
)
from app.models.pregnancy import Pregnancy
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class ContentPersonalizationEngine:
    """
    Advanced personalization engine that delivers the right content
    at the right time with the right emotional tone.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_personalized_content(
        self,
        user_id: str,
        pregnancy_id: str,
        context: PersonalizationContext,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized content based on user context and pregnancy stage.
        This is the core intelligence of the content system.
        """
        try:
            # Get user preferences
            preferences = self._get_user_preferences(user_id, pregnancy_id)
            if not preferences:
                # Create default preferences if none exist
                preferences = self._create_default_preferences(user_id, pregnancy_id)
            
            # Build content query based on personalization context
            content_query = self._build_personalized_query(context, preferences)
            
            # Execute query and get content
            results = self.session.exec(content_query.limit(limit)).all()
            
            # Apply additional personalization filters
            personalized_content = []
            for content in results:
                # Skip if user has blocked this category
                if (content.category_id and 
                    content.category_id in preferences.blocked_categories):
                    continue
                
                # Calculate personalization score
                personalization_score = self._calculate_personalization_score(
                    content, context, preferences
                )
                
                # Adapt content based on preferences
                adapted_content = self._adapt_content_for_user(
                    content, preferences, personalization_score
                )
                
                personalized_content.append(adapted_content)
            
            # Sort by personalization score and return
            personalized_content.sort(
                key=lambda x: x.get('personalization_score', 0), 
                reverse=True
            )
            
            return personalized_content[:limit]
            
        except Exception as e:
            logger.error(f"Error getting personalized content for user {user_id}: {e}")
            return []
    
    def get_weekly_content(
        self,
        user_id: str,
        pregnancy_id: str,
        week_number: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive weekly content including tips, development, and guidance.
        """
        try:
            context = self._build_week_context(pregnancy_id, week_number)
            
            # Get different types of weekly content
            weekly_tips = self._get_weekly_tips(week_number, context)
            baby_development = self._get_baby_development_content(week_number)
            health_guidance = self._get_health_wellness_content(week_number, context)
            emotional_support = self._get_emotional_support_content(week_number, context)
            
            return {
                'week_number': week_number,
                'trimester': context.trimester,
                'weekly_tips': weekly_tips,
                'baby_development': baby_development,
                'health_guidance': health_guidance,
                'emotional_support': emotional_support,
                'personalization_context': context.dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting weekly content for week {week_number}: {e}")
            return {}
    
    def _get_user_preferences(
        self, 
        user_id: str, 
        pregnancy_id: str
    ) -> Optional[UserContentPreferences]:
        """Get user's content preferences."""
        statement = select(UserContentPreferences).where(
            and_(
                UserContentPreferences.user_id == user_id,
                UserContentPreferences.pregnancy_id == pregnancy_id
            )
        )
        return self.session.exec(statement).first()
    
    def _create_default_preferences(
        self, 
        user_id: str, 
        pregnancy_id: str
    ) -> UserContentPreferences:
        """Create default preferences for new user."""
        preferences = UserContentPreferences(
            user_id=user_id,
            pregnancy_id=pregnancy_id,
            content_frequency="daily",
            preferred_delivery_time="09:00",
            detail_level="standard",
            emotional_tone="warm",
            medical_info_level="balanced",
            family_sharing_level="moderate",
            partner_involvement_level="high"
        )
        
        self.session.add(preferences)
        self.session.commit()
        return preferences
    
    def _build_personalized_query(
        self, 
        context: PersonalizationContext, 
        preferences: UserContentPreferences
    ):
        """Build database query based on personalization context."""
        base_query = select(PregnancyContent).where(
            and_(
                PregnancyContent.is_active == True,
                PregnancyContent.medical_review_status == MedicalReviewStatus.APPROVED
            )
        )
        
        # Filter by pregnancy week (current week ± 1 for flexibility)
        week_filters = [
            PregnancyContent.week_number == context.pregnancy_week,
            PregnancyContent.week_number == context.pregnancy_week - 1,
            PregnancyContent.week_number == context.pregnancy_week + 1,
            PregnancyContent.week_number.is_(None)  # Cross-week content
        ]
        base_query = base_query.where(or_(*week_filters))
        
        # Filter by trimester
        trimester_filters = [
            PregnancyContent.trimester == context.trimester,
            PregnancyContent.trimester.is_(None)  # All trimester content
        ]
        base_query = base_query.where(or_(*trimester_filters))
        
        # Filter by preferred categories if specified
        if preferences.preferred_categories:
            base_query = base_query.where(
                PregnancyContent.category_id.in_(preferences.preferred_categories)
            )
        
        # Order by priority and recency
        base_query = base_query.order_by(
            PregnancyContent.priority.desc(),
            PregnancyContent.created_at.desc()
        )
        
        return base_query
    
    def _calculate_personalization_score(
        self,
        content: PregnancyContent,
        context: PersonalizationContext,
        preferences: UserContentPreferences
    ) -> float:
        """
        Calculate how well this content matches the user's current needs.
        Score from 0.0 to 1.0.
        """
        score = 0.5  # Base score
        
        # Week relevance (highest priority)
        if content.week_number == context.pregnancy_week:
            score += 0.3
        elif content.week_number and abs(content.week_number - context.pregnancy_week) == 1:
            score += 0.2
        elif content.week_number is None:
            score += 0.1  # Cross-week content is generally useful
        
        # Trimester relevance
        if content.trimester == context.trimester:
            score += 0.1
        elif content.trimester is None:
            score += 0.05
        
        # User preference alignment
        if content.category_id in preferences.preferred_categories:
            score += 0.2
        
        # First-time parent considerations
        if context.first_time_parent and "first_time_parent" in content.target_audience:
            score += 0.15
        
        # High-risk pregnancy considerations
        if context.is_high_risk and "high_risk" in content.target_audience:
            score += 0.15
        
        # Multiple pregnancy considerations
        if context.is_multiple_pregnancy and "multiple_pregnancy" in content.target_audience:
            score += 0.15
        
        # Emotional state matching
        if (context.emotional_state and 
            context.emotional_state in content.personalization_rules.get('emotional_states', [])):
            score += 0.1
        
        # Time of day matching
        if (context.time_of_day and 
            content.optimal_delivery_time and
            self._is_optimal_time(context.time_of_day, content.optimal_delivery_time)):
            score += 0.05
        
        # Ensure score stays within bounds
        return min(max(score, 0.0), 1.0)
    
    def _adapt_content_for_user(
        self,
        content: PregnancyContent,
        preferences: UserContentPreferences,
        personalization_score: float
    ) -> Dict[str, Any]:
        """
        Adapt content presentation based on user preferences.
        """
        adapted = {
            'id': content.id,
            'title': content.title,
            'subtitle': content.subtitle,
            'content_type': content.content_type,
            'week_number': content.week_number,
            'trimester': content.trimester,
            'personalization_score': personalization_score,
            'reading_time_minutes': content.reading_time_minutes,
            'featured_image': content.featured_image,
            'tags': content.tags
        }
        
        # Adapt content detail based on user preference
        if preferences.detail_level == "minimal":
            adapted['content'] = content.content_summary or content.content_body[:200] + "..."
        elif preferences.detail_level == "detailed":
            adapted['content'] = content.content_body
            adapted['external_links'] = content.external_links
        else:  # standard
            adapted['content'] = content.content_body
        
        # Adapt emotional tone if specified in personalization rules
        if preferences.emotional_tone in content.personalization_rules.get('tone_variations', {}):
            tone_variation = content.personalization_rules['tone_variations'][preferences.emotional_tone]
            adapted['title'] = tone_variation.get('title', adapted['title'])
            adapted['subtitle'] = tone_variation.get('subtitle', adapted['subtitle'])
        
        # Include cultural adaptations if relevant
        if preferences.cultural_preferences:
            cultural_key = preferences.cultural_preferences.get('primary_culture')
            if cultural_key and cultural_key in content.personalization_rules.get('cultural_adaptations', {}):
                cultural_adaptation = content.personalization_rules['cultural_adaptations'][cultural_key]
                adapted.update(cultural_adaptation)
        
        return adapted
    
    def _get_weekly_tips(
        self, 
        week_number: int, 
        context: PersonalizationContext
    ) -> List[Dict[str, Any]]:
        """Get weekly tips specific to the pregnancy week."""
        statement = select(PregnancyContent).where(
            and_(
                PregnancyContent.content_type == ContentType.WEEKLY_TIP,
                PregnancyContent.week_number == week_number,
                PregnancyContent.is_active == True,
                PregnancyContent.medical_review_status == MedicalReviewStatus.APPROVED
            )
        ).order_by(PregnancyContent.priority.desc())
        
        tips = self.session.exec(statement).all()
        return [self._format_content_for_response(tip) for tip in tips]
    
    def _get_baby_development_content(self, week_number: int) -> Optional[Dict[str, Any]]:
        """Get baby development information for the week."""
        statement = select(BabyDevelopmentContent).where(
            BabyDevelopmentContent.week_number == week_number
        )
        
        development = self.session.exec(statement).first()
        if not development:
            return None
        
        return {
            'week_number': development.week_number,
            'size_comparison': development.size_comparison,
            'size_comparison_category': development.size_comparison_category,
            'alternative_comparisons': development.alternative_comparisons,
            'length_mm': development.length_mm,
            'weight_grams': development.weight_grams,
            'major_developments': development.major_developments,
            'sensory_developments': development.sensory_developments,
            'body_system_developments': development.body_system_developments,
            'amazing_fact': development.amazing_fact,
            'connection_moment': development.connection_moment,
            'what_baby_can_do': development.what_baby_can_do,
            'bonding_activities': development.bonding_activities,
            'conversation_starters': development.conversation_starters,
            'illustration_url': development.illustration_url,
            'size_comparison_image': development.size_comparison_image
        }
    
    def _get_health_wellness_content(
        self, 
        week_number: int, 
        context: PersonalizationContext
    ) -> List[Dict[str, Any]]:
        """Get health and wellness content for the week."""
        statement = select(PregnancyContent).where(
            and_(
                PregnancyContent.content_type == ContentType.HEALTH_WELLNESS,
                or_(
                    PregnancyContent.week_number == week_number,
                    PregnancyContent.trimester == context.trimester,
                    PregnancyContent.week_number.is_(None)
                ),
                PregnancyContent.is_active == True,
                PregnancyContent.medical_review_status == MedicalReviewStatus.APPROVED
            )
        ).order_by(PregnancyContent.priority.desc())
        
        content = self.session.exec(statement).all()
        return [self._format_content_for_response(item) for item in content[:3]]
    
    def _get_emotional_support_content(
        self, 
        week_number: int, 
        context: PersonalizationContext
    ) -> List[Dict[str, Any]]:
        """Get emotional support content appropriate for the week and context."""
        statement = select(PregnancyContent).where(
            and_(
                PregnancyContent.content_type == ContentType.EMOTIONAL_SUPPORT,
                or_(
                    PregnancyContent.week_number == week_number,
                    PregnancyContent.trimester == context.trimester,
                    PregnancyContent.week_number.is_(None)
                ),
                PregnancyContent.is_active == True,
                PregnancyContent.medical_review_status == MedicalReviewStatus.APPROVED
            )
        ).order_by(PregnancyContent.priority.desc())
        
        content = self.session.exec(statement).all()
        
        # Filter by emotional state if provided
        if context.emotional_state:
            filtered_content = []
            for item in content:
                emotional_states = item.personalization_rules.get('emotional_states', [])
                if context.emotional_state in emotional_states or not emotional_states:
                    filtered_content.append(item)
            content = filtered_content
        
        return [self._format_content_for_response(item) for item in content[:2]]
    
    def _build_week_context(
        self, 
        pregnancy_id: str, 
        week_number: int
    ) -> PersonalizationContext:
        """Build personalization context for a specific week."""
        # Get pregnancy details
        pregnancy = self.session.exec(
            select(Pregnancy).where(Pregnancy.id == pregnancy_id)
        ).first()
        
        if not pregnancy:
            raise ValueError(f"Pregnancy {pregnancy_id} not found")
        
        # Calculate trimester
        if week_number <= 13:
            trimester = 1
        elif week_number <= 27:
            trimester = 2
        else:
            trimester = 3
        
        pregnancy_details = pregnancy.pregnancy_details
        
        return PersonalizationContext(
            pregnancy_week=week_number,
            trimester=trimester,
            is_high_risk=(pregnancy_details.risk_level.value != "low"),
            is_multiple_pregnancy=pregnancy_details.is_multiple,
            first_time_parent=True,  # TODO: Determine from user history
            preferred_detail_level="standard",
            time_of_day=datetime.now().strftime("%H:%M")
        )
    
    def _format_content_for_response(self, content: PregnancyContent) -> Dict[str, Any]:
        """Format content for API response."""
        return {
            'id': content.id,
            'title': content.title,
            'subtitle': content.subtitle,
            'content': content.content_body,
            'content_summary': content.content_summary,
            'content_type': content.content_type,
            'week_number': content.week_number,
            'trimester': content.trimester,
            'reading_time_minutes': content.reading_time_minutes,
            'featured_image': content.featured_image,
            'tags': content.tags,
            'priority': content.priority,
            'created_at': content.created_at.isoformat() if content.created_at else None
        }
    
    def _is_optimal_time(self, current_time: str, optimal_time: str) -> bool:
        """Check if current time is within 2 hours of optimal delivery time."""
        try:
            current_hour = int(current_time.split(':')[0])
            optimal_hour = int(optimal_time.split(':')[0])
            return abs(current_hour - optimal_hour) <= 2
        except (ValueError, IndexError):
            return False


class ContentService(BaseService):
    """
    Main content service that handles all content-related operations.
    """
    
    def __init__(self):
        super().__init__(PregnancyContent)
        
    def get_personalized_feed_content(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get personalized content for the user's feed integration.
        This is the main entry point for content delivery.
        """
        try:
            # Get current pregnancy week
            pregnancy = session.exec(
                select(Pregnancy).where(Pregnancy.id == pregnancy_id)
            ).first()
            
            if not pregnancy:
                logger.error(f"Pregnancy {pregnancy_id} not found")
                return []
            
            # Build personalization context
            current_week = pregnancy.pregnancy_details.current_week
            engine = ContentPersonalizationEngine(session)
            context = engine._build_week_context(pregnancy_id, current_week)
            
            # Get personalized content
            content = engine.get_personalized_content(
                user_id, pregnancy_id, context, limit
            )
            
            # Log content delivery
            self._log_content_delivery(session, user_id, pregnancy_id, content)
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting personalized feed content: {e}")
            return []
    
    def get_weekly_pregnancy_content(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        week_number: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive weekly content for a specific pregnancy week.
        """
        try:
            engine = ContentPersonalizationEngine(session)
            weekly_content = engine.get_weekly_content(user_id, pregnancy_id, week_number)
            
            # Log content delivery
            if weekly_content:
                content_list = [
                    {'id': 'weekly_content', 'content_type': 'weekly_summary'}
                ]
                self._log_content_delivery(session, user_id, pregnancy_id, content_list)
            
            return weekly_content
            
        except Exception as e:
            logger.error(f"Error getting weekly content for week {week_number}: {e}")
            return {}
    
    def record_content_interaction(
        self,
        session: Session,
        user_id: str,
        content_id: str,
        interaction_type: str,
        interaction_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record user interaction with content for personalization learning.
        """
        try:
            # Get existing delivery log entry
            statement = select(ContentDeliveryLog).where(
                and_(
                    ContentDeliveryLog.user_id == user_id,
                    ContentDeliveryLog.content_id == content_id
                )
            ).order_by(ContentDeliveryLog.delivered_at.desc())
            
            delivery_log = session.exec(statement).first()
            
            if delivery_log:
                # Update existing log
                if interaction_type == "view":
                    if delivery_log.first_viewed_at is None:
                        delivery_log.first_viewed_at = datetime.utcnow()
                    delivery_log.last_viewed_at = datetime.utcnow()
                    delivery_log.view_count += 1
                    
                    if interaction_data and 'time_spent' in interaction_data:
                        delivery_log.total_view_time_seconds += interaction_data['time_spent']
                
                elif interaction_type in ["helpful", "not_helpful", "saved", "shared"]:
                    delivery_log.reaction = interaction_type
                    
                    if interaction_type == "helpful":
                        delivery_log.added_to_memory_book = interaction_data.get('save_to_memory', False)
                    elif interaction_type == "shared":
                        delivery_log.shared_with_family = True
                
                session.add(delivery_log)
                session.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error recording content interaction: {e}")
            return False
    
    def _log_content_delivery(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        content_list: List[Dict[str, Any]]
    ) -> None:
        """Log content delivery for analytics and personalization."""
        try:
            for content_item in content_list:
                if 'id' in content_item:
                    delivery_log = ContentDeliveryLog(
                        user_id=user_id,
                        pregnancy_id=pregnancy_id,
                        content_id=content_item['id'],
                        delivery_method=ContentDeliveryMethod.FEED_INTEGRATION,
                        delivery_context={
                            'content_type': content_item.get('content_type'),
                            'delivery_time': datetime.utcnow().isoformat(),
                            'personalization_score': content_item.get('personalization_score', 0.0)
                        }
                    )
                    session.add(delivery_log)
            
            session.commit()
            
        except Exception as e:
            logger.error(f"Error logging content delivery: {e}")


# Global service instance
content_service = ContentService()