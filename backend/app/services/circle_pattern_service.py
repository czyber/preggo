"""
Circle Pattern services for smart privacy selection and pattern management.

This module provides services for:
- Circle pattern CRUD operations
- Pattern suggestion algorithms 
- Pattern usage analytics and learning
- AI-powered privacy recommendations
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, and_, or_, func, desc
from datetime import datetime, timedelta
from app.services.base import BaseService
from app.models.family import (
    CirclePattern, CirclePatternUsage, PatternSuggestion,
    FamilyGroup, FamilyMember, GroupType
)
from app.models.content import PostType, PostContent
from app.services.family_service import family_group_service
import logging

logger = logging.getLogger(__name__)


class CirclePatternService(BaseService[CirclePattern]):
    """Service for managing circle patterns"""
    
    def __init__(self):
        super().__init__(CirclePattern)
    
    async def create_pattern(
        self,
        session: Session,
        pregnancy_id: str,
        name: str,
        icon: str,
        description: str,
        group_ids: List[str],
        suggested_for: List[str] = None,
        is_preset: bool = False
    ) -> Optional[CirclePattern]:
        """Create a new circle pattern"""
        try:
            pattern_data = {
                "name": name,
                "icon": icon, 
                "description": description,
                "pregnancy_id": pregnancy_id,
                "group_ids": group_ids,
                "suggested_for": suggested_for or [],
                "is_preset": is_preset
            }
            
            return await self.create(session, pattern_data)
        except Exception as e:
            logger.error(f"Error creating circle pattern: {e}")
            return None
    
    async def get_pregnancy_patterns(
        self, 
        session: Session, 
        pregnancy_id: str,
        include_inactive: bool = False
    ) -> List[CirclePattern]:
        """Get all circle patterns for a pregnancy"""
        try:
            statement = select(CirclePattern).where(
                CirclePattern.pregnancy_id == pregnancy_id
            )
            
            if not include_inactive:
                statement = statement.where(CirclePattern.is_active == True)
            
            # Order by usage frequency and creation date
            statement = statement.order_by(
                desc(CirclePattern.usage_frequency),
                desc(CirclePattern.created_at)
            )
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting pregnancy patterns: {e}")
            return []
    
    async def get_pattern_with_groups(
        self, 
        session: Session, 
        pattern_id: str
    ) -> Optional[Tuple[CirclePattern, List[FamilyGroup]]]:
        """Get pattern with associated family groups"""
        try:
            pattern = await self.get_by_id(session, pattern_id)
            if not pattern:
                return None
            
            # Get associated groups
            groups = []
            if pattern.group_ids:
                for group_id in pattern.group_ids:
                    group = await family_group_service.get_by_id(session, group_id)
                    if group:
                        groups.append(group)
            
            return pattern, groups
        except Exception as e:
            logger.error(f"Error getting pattern with groups: {e}")
            return None
    
    async def update_pattern_usage(
        self,
        session: Session,
        pattern_id: str,
        increment: int = 1
    ) -> bool:
        """Update pattern usage frequency"""
        try:
            pattern = await self.get_by_id(session, pattern_id)
            if not pattern:
                return False
            
            pattern.usage_frequency += increment
            pattern.last_used_at = datetime.utcnow()
            
            session.add(pattern)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating pattern usage: {e}")
            session.rollback()
            return False
    
    async def deactivate_pattern(
        self,
        session: Session,
        pattern_id: str
    ) -> bool:
        """Deactivate a pattern instead of deleting it"""
        try:
            pattern = await self.get_by_id(session, pattern_id)
            if not pattern:
                return False
            
            pattern.is_active = False
            session.add(pattern)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error deactivating pattern: {e}")
            session.rollback()
            return False
    
    async def create_preset_patterns(
        self,
        session: Session,
        pregnancy_id: str
    ) -> List[CirclePattern]:
        """Create default preset patterns for a new pregnancy"""
        try:
            # Get family groups for this pregnancy
            groups = await family_group_service.get_pregnancy_groups(session, pregnancy_id)
            group_map = {group.type: group.id for group in groups}
            
            presets = [
                {
                    "name": "Just Us",
                    "icon": "💕",
                    "description": "You and your partner",
                    "group_ids": [],
                    "suggested_for": [PostType.SYMPTOM_SHARE, PostType.PREPARATION]
                },
                {
                    "name": "Close Family",
                    "icon": "👨‍👩‍👧‍👦",
                    "description": "Parents, siblings, and partner",
                    "group_ids": [group_map.get(GroupType.IMMEDIATE_FAMILY)],
                    "suggested_for": [PostType.ULTRASOUND, PostType.MILESTONE]
                },
                {
                    "name": "Everyone",
                    "icon": "🌟", 
                    "description": "All your family and friends",
                    "group_ids": list(group_map.values()),
                    "suggested_for": [PostType.ANNOUNCEMENT, PostType.CELEBRATION]
                },
                {
                    "name": "Grandparents Circle",
                    "icon": "👴👵",
                    "description": "Extended family including grandparents",
                    "group_ids": [
                        group_map.get(GroupType.IMMEDIATE_FAMILY),
                        group_map.get(GroupType.EXTENDED_FAMILY)
                    ],
                    "suggested_for": [PostType.WEEKLY_UPDATE, PostType.BELLY_PHOTO]
                },
                {
                    "name": "Friend Support",
                    "icon": "🤗",
                    "description": "Close friends and support network",
                    "group_ids": [
                        group_map.get(GroupType.FRIENDS),
                        group_map.get(GroupType.SUPPORT_CIRCLE)
                    ],
                    "suggested_for": [PostType.QUESTION, PostType.MEMORY]
                }
            ]
            
            created_patterns = []
            for preset in presets:
                # Filter out None group IDs
                preset["group_ids"] = [gid for gid in preset["group_ids"] if gid is not None]
                
                pattern = await self.create_pattern(
                    session=session,
                    pregnancy_id=pregnancy_id,
                    name=preset["name"],
                    icon=preset["icon"],
                    description=preset["description"],
                    group_ids=preset["group_ids"],
                    suggested_for=preset["suggested_for"],
                    is_preset=True
                )
                if pattern:
                    created_patterns.append(pattern)
            
            return created_patterns
        except Exception as e:
            logger.error(f"Error creating preset patterns: {e}")
            return []


class PatternSuggestionService(BaseService[PatternSuggestion]):
    """Service for AI-powered pattern suggestions"""
    
    def __init__(self):
        super().__init__(PatternSuggestion)
    
    async def generate_suggestions(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        post_content: Dict[str, Any],
        post_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered pattern suggestions for a post"""
        try:
            # Get available patterns
            available_patterns = await circle_pattern_service.get_pregnancy_patterns(
                session, pregnancy_id
            )
            
            if not available_patterns:
                return []
            
            suggestions = []
            
            # Get user's historical usage for learning
            historical_patterns = await self._get_user_pattern_history(
                session, user_id, pregnancy_id
            )
            
            for pattern in available_patterns:
                confidence, reason, learned_from = await self._calculate_pattern_confidence(
                    session, pattern, post_content, post_type, historical_patterns
                )
                
                if confidence > 30:  # Only suggest patterns with >30% confidence
                    suggestion_data = {
                        "pattern": pattern,
                        "confidence": confidence,
                        "reason": reason,
                        "learned_from": learned_from
                    }
                    suggestions.append(suggestion_data)
                    
                    # Store suggestion in database
                    await self._store_suggestion(
                        session, user_id, pregnancy_id, pattern.id,
                        post_type, confidence, reason, learned_from, post_content
                    )
            
            # Sort by confidence and return top suggestions
            suggestions.sort(key=lambda x: x["confidence"], reverse=True)
            return suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            logger.error(f"Error generating pattern suggestions: {e}")
            return []
    
    async def _get_user_pattern_history(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str
    ) -> Dict[str, Any]:
        """Get user's pattern usage history for learning"""
        try:
            # Get recent pattern usage
            statement = select(CirclePatternUsage).where(
                and_(
                    CirclePatternUsage.user_id == user_id,
                    CirclePatternUsage.pregnancy_id == pregnancy_id,
                    CirclePatternUsage.used_at > datetime.utcnow() - timedelta(days=30)
                )
            ).order_by(desc(CirclePatternUsage.used_at))
            
            usage_records = session.exec(statement).all()
            
            # Analyze patterns by post type
            post_type_patterns = {}
            for usage in usage_records:
                if usage.post_type:
                    if usage.post_type not in post_type_patterns:
                        post_type_patterns[usage.post_type] = {}
                    
                    pattern_id = usage.pattern_id
                    if pattern_id not in post_type_patterns[usage.post_type]:
                        post_type_patterns[usage.post_type][pattern_id] = 0
                    post_type_patterns[usage.post_type][pattern_id] += 1
            
            return {
                "post_type_patterns": post_type_patterns,
                "total_posts": len(usage_records),
                "recent_patterns": [usage.pattern_id for usage in usage_records[:10]]
            }
            
        except Exception as e:
            logger.error(f"Error getting user pattern history: {e}")
            return {}
    
    async def _calculate_pattern_confidence(
        self,
        session: Session,
        pattern: CirclePattern,
        post_content: Dict[str, Any],
        post_type: Optional[str],
        historical_patterns: Dict[str, Any]
    ) -> Tuple[float, str, str]:
        """Calculate confidence score for a pattern suggestion"""
        try:
            confidence = 0.0
            reasons = []
            learned_from = "content_analysis"
            
            # Base confidence from pattern usage frequency
            if pattern.usage_frequency > 0:
                confidence += min(pattern.usage_frequency * 5, 30)
                reasons.append(f"Used {pattern.usage_frequency} times")
            
            # Content-based analysis
            text_content = post_content.get("text", "").lower()
            title_content = post_content.get("title", "").lower()
            all_text = f"{text_content} {title_content}"
            
            # Check for excitement/announcement keywords
            excitement_keywords = ["first", "first time", "exciting", "amazing", "can't wait", "big news"]
            if any(keyword in all_text for keyword in excitement_keywords):
                if "everyone" in pattern.name.lower():
                    confidence += 25
                    reasons.append("Exciting content usually shared widely")
            
            # Check for personal/intimate keywords
            personal_keywords = ["scared", "worried", "private", "personal", "intimate", "symptoms"]
            if any(keyword in all_text for keyword in personal_keywords):
                if "just us" in pattern.name.lower():
                    confidence += 30
                    reasons.append("Personal content best shared privately")
            
            # Historical pattern matching
            if post_type and historical_patterns.get("post_type_patterns", {}).get(post_type):
                pattern_usage = historical_patterns["post_type_patterns"][post_type]
                if pattern.id in pattern_usage:
                    historical_weight = min(pattern_usage[pattern.id] * 10, 40)
                    confidence += historical_weight
                    reasons.append(f"You usually share {post_type} posts this way")
                    learned_from = "historical_pattern"
            
            # Post type suggestions from pattern configuration
            if post_type and post_type in pattern.suggested_for:
                confidence += 20
                reasons.append(f"Recommended pattern for {post_type} posts")
                learned_from = "post_type"
            
            # Time-based suggestions (e.g., milestones for certain weeks)
            week = post_content.get("week")
            if week:
                if week in [12, 20, 32] and "everyone" in pattern.name.lower():
                    confidence += 15
                    reasons.append("Major milestone usually shared with everyone")
                    learned_from = "time_context"
            
            return min(confidence, 100), "; ".join(reasons), learned_from
            
        except Exception as e:
            logger.error(f"Error calculating pattern confidence: {e}")
            return 0.0, "Error calculating confidence", "error"
    
    async def _store_suggestion(
        self,
        session: Session,
        user_id: str,
        pregnancy_id: str,
        pattern_id: str,
        post_type: Optional[str],
        confidence: float,
        reason: str,
        learned_from: str,
        post_content: Dict[str, Any]
    ) -> Optional[PatternSuggestion]:
        """Store a pattern suggestion in the database"""
        try:
            suggestion_data = {
                "user_id": user_id,
                "pregnancy_id": pregnancy_id,
                "pattern_id": pattern_id,
                "post_type": post_type,
                "confidence": confidence,
                "reason": reason,
                "learned_from": learned_from,
                "post_content": post_content,
                "expires_at": datetime.utcnow() + timedelta(hours=1)  # Suggestions expire after 1 hour
            }
            
            return await self.create(session, suggestion_data)
        except Exception as e:
            logger.error(f"Error storing pattern suggestion: {e}")
            return None
    
    async def mark_suggestion_selected(
        self,
        session: Session,
        suggestion_id: str,
        user_feedback: Optional[str] = None
    ) -> bool:
        """Mark a suggestion as selected by user"""
        try:
            suggestion = await self.get_by_id(session, suggestion_id)
            if not suggestion:
                return False
            
            suggestion.was_selected = True
            if user_feedback:
                suggestion.user_feedback = user_feedback
            
            session.add(suggestion)
            session.commit()
            return True
        except Exception as e:
            logger.error(f"Error marking suggestion as selected: {e}")
            session.rollback()
            return False


class PatternUsageService(BaseService[CirclePatternUsage]):
    """Service for tracking pattern usage analytics"""
    
    def __init__(self):
        super().__init__(CirclePatternUsage)
    
    async def track_pattern_usage(
        self,
        session: Session,
        pattern_id: str,
        user_id: str,
        pregnancy_id: str,
        post_id: Optional[str] = None,
        post_type: Optional[str] = None,
        was_suggested: bool = False,
        suggestion_confidence: Optional[float] = None,
        selected_from_suggestions: bool = False,
        context_data: Dict[str, Any] = None
    ) -> Optional[CirclePatternUsage]:
        """Track usage of a circle pattern"""
        try:
            usage_data = {
                "pattern_id": pattern_id,
                "user_id": user_id,
                "pregnancy_id": pregnancy_id,
                "post_id": post_id,
                "post_type": post_type,
                "was_suggested": was_suggested,
                "suggestion_confidence": suggestion_confidence,
                "selected_from_suggestions": selected_from_suggestions,
                "context_data": context_data or {}
            }
            
            usage_record = await self.create(session, usage_data)
            
            # Update pattern usage frequency
            if usage_record:
                await circle_pattern_service.update_pattern_usage(session, pattern_id)
            
            return usage_record
        except Exception as e:
            logger.error(f"Error tracking pattern usage: {e}")
            return None
    
    async def get_usage_analytics(
        self,
        session: Session,
        pregnancy_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get pattern usage analytics for a pregnancy"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get usage records
            statement = select(CirclePatternUsage).where(
                and_(
                    CirclePatternUsage.pregnancy_id == pregnancy_id,
                    CirclePatternUsage.used_at >= start_date
                )
            )
            
            usage_records = session.exec(statement).all()
            
            # Analyze pattern usage
            pattern_stats = {}
            suggestion_accuracy = {"total": 0, "selected": 0}
            post_type_patterns = {}
            
            for usage in usage_records:
                # Pattern usage stats
                pattern_id = usage.pattern_id
                if pattern_id not in pattern_stats:
                    pattern_stats[pattern_id] = {
                        "total_uses": 0,
                        "suggested_uses": 0,
                        "post_types": set()
                    }
                
                pattern_stats[pattern_id]["total_uses"] += 1
                if usage.was_suggested:
                    pattern_stats[pattern_id]["suggested_uses"] += 1
                    suggestion_accuracy["total"] += 1
                    if usage.selected_from_suggestions:
                        suggestion_accuracy["selected"] += 1
                
                if usage.post_type:
                    pattern_stats[pattern_id]["post_types"].add(usage.post_type)
                    
                    # Post type pattern analysis
                    if usage.post_type not in post_type_patterns:
                        post_type_patterns[usage.post_type] = {}
                    if pattern_id not in post_type_patterns[usage.post_type]:
                        post_type_patterns[usage.post_type][pattern_id] = 0
                    post_type_patterns[usage.post_type][pattern_id] += 1
            
            # Calculate suggestion accuracy
            suggestion_accuracy_rate = 0
            if suggestion_accuracy["total"] > 0:
                suggestion_accuracy_rate = (
                    suggestion_accuracy["selected"] / suggestion_accuracy["total"]
                ) * 100
            
            return {
                "pattern_usage": pattern_stats,
                "suggestion_accuracy": suggestion_accuracy_rate,
                "post_type_patterns": post_type_patterns,
                "total_patterns_used": len(pattern_stats),
                "analysis_period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error getting usage analytics: {e}")
            return {}
    
    async def get_member_engagement(
        self,
        session: Session,
        pregnancy_id: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get family member engagement analytics"""
        try:
            # This would integrate with post engagement data
            # For now, return a placeholder structure
            return [
                {
                    "member_id": "sample_id",
                    "reaction_rate": 0.8,
                    "comment_rate": 0.6,
                    "view_rate": 0.9,
                    "favorite_content_types": [PostType.MILESTONE, PostType.ULTRASOUND]
                }
            ]
        except Exception as e:
            logger.error(f"Error getting member engagement: {e}")
            return []


# Service instances
circle_pattern_service = CirclePatternService()
pattern_suggestion_service = PatternSuggestionService()
pattern_usage_service = PatternUsageService()