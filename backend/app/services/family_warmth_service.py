"""
Family warmth service for the Preggo app overhaul.
Replaces traditional engagement metrics with meaningful family support visualization.
Calculates family warmth scores and provides insights about family dynamics.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, and_, func
from datetime import datetime, timedelta
from app.models.enhanced_content import (
    FamilyInteraction, FamilyWarmthCalculation, FamilyWarmthType,
    FamilyWarmthScore
)
from app.models.content import Post, Comment, Reaction
from app.models.family import FamilyGroup, FamilyMember
from app.services.base import BaseService
import logging
import re

logger = logging.getLogger(__name__)


class FamilyWarmthAnalyzer:
    """
    Analyzes family interactions to calculate warmth scores.
    This replaces traditional like/share metrics with meaningful family support indicators.
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_post_warmth(self, post_id: str) -> FamilyWarmthScore:
        """
        Calculate family warmth for a specific post.
        Returns a detailed warmth score breakdown.
        """
        try:
            # Get all interactions for this post
            interactions = self._get_post_interactions(post_id)
            
            # Get post details for context
            post = self.session.exec(select(Post).where(Post.id == post_id)).first()
            if not post:
                return FamilyWarmthScore()
            
            # Calculate different warmth components
            immediate_family_score = self._calculate_immediate_family_warmth(interactions, post.pregnancy_id)
            extended_family_score = self._calculate_extended_family_warmth(interactions, post.pregnancy_id)
            recent_engagement_score = self._calculate_recent_engagement_warmth(interactions)
            emotional_support_score = self._calculate_emotional_support_warmth(interactions)
            
            # Calculate overall warmth (weighted average)
            overall_score = (
                immediate_family_score * 0.4 +  # Immediate family most important
                emotional_support_score * 0.3 +   # Quality of support
                recent_engagement_score * 0.2 +   # Recency and consistency
                extended_family_score * 0.1       # Extended family involvement
            )
            
            # Determine trend
            trend = self._calculate_warmth_trend(post_id, overall_score)
            
            warmth_score = FamilyWarmthScore(
                immediate_family_score=immediate_family_score,
                extended_family_score=extended_family_score,
                recent_engagement_score=recent_engagement_score,
                emotional_support_score=emotional_support_score,
                overall_warmth_score=overall_score,
                warmth_trend=trend
            )
            
            return warmth_score
            
        except Exception as e:
            logger.error(f"Error calculating post warmth for post {post_id}: {e}")
            return FamilyWarmthScore()
    
    def calculate_pregnancy_warmth(
        self, 
        pregnancy_id: str, 
        days_back: int = 7
    ) -> FamilyWarmthScore:
        """
        Calculate overall family warmth for a pregnancy over a time period.
        """
        try:
            # Get all interactions for this pregnancy in the time period
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            interactions = self._get_pregnancy_interactions(pregnancy_id, cutoff_date)
            
            if not interactions:
                return FamilyWarmthScore()
            
            # Calculate warmth components
            immediate_family_score = self._calculate_immediate_family_warmth(interactions, pregnancy_id)
            extended_family_score = self._calculate_extended_family_warmth(interactions, pregnancy_id)
            recent_engagement_score = self._calculate_recent_engagement_warmth(interactions)
            emotional_support_score = self._calculate_emotional_support_warmth(interactions)
            
            # Calculate overall warmth
            overall_score = (
                immediate_family_score * 0.35 +
                emotional_support_score * 0.35 +
                recent_engagement_score * 0.2 +
                extended_family_score * 0.1
            )
            
            # Determine trend by comparing with previous period
            trend = self._calculate_pregnancy_warmth_trend(pregnancy_id, overall_score, days_back)
            
            return FamilyWarmthScore(
                immediate_family_score=immediate_family_score,
                extended_family_score=extended_family_score,
                recent_engagement_score=recent_engagement_score,
                emotional_support_score=emotional_support_score,
                overall_warmth_score=overall_score,
                warmth_trend=trend
            )
            
        except Exception as e:
            logger.error(f"Error calculating pregnancy warmth for pregnancy {pregnancy_id}: {e}")
            return FamilyWarmthScore()
    
    def analyze_comment_warmth(self, comment_text: str, context: str = "") -> Tuple[FamilyWarmthType, float]:
        """
        Analyze a comment to determine its warmth type and intensity.
        Uses keyword analysis and emotional sentiment detection.
        """
        try:
            comment_lower = comment_text.lower().strip()
            
            # Define warmth patterns and their intensities
            warmth_patterns = {
                FamilyWarmthType.EMOTIONAL_SUPPORT: {
                    'patterns': [
                        r'\b(love|loving|care|caring|support|supporting|proud|amazing|wonderful)\b',
                        r'\b(you.*got.*this|thinking.*you|sending.*love|here.*for.*you)\b',
                        r'\b(beautiful|gorgeous|glowing|incredible|strong|brave)\b'
                    ],
                    'base_intensity': 0.8
                },
                FamilyWarmthType.CELEBRATION: {
                    'patterns': [
                        r'\b(congratulations|congrats|celebrate|excited|thrilled|joy)\b',
                        r'\b(so.*happy|amazing.*news|wonderful.*news|fantastic)\b',
                        r'\b(milestone|achievement|special.*moment)\b'
                    ],
                    'base_intensity': 0.9
                },
                FamilyWarmthType.PRACTICAL_HELP: {
                    'patterns': [
                        r'\b(help|offer|need.*anything|let.*me.*know|here.*to.*help)\b',
                        r'\b(bring.*you|cook|meal|babysit|drive)\b',
                        r'\b(advice|suggest|recommend|experience)\b'
                    ],
                    'base_intensity': 0.7
                },
                FamilyWarmthType.MEMORY_SHARING: {
                    'patterns': [
                        r'\b(remember.*when|reminds.*me|memory|nostalgic)\b',
                        r'\b(same.*thing|happened.*to.*me|similar|experience)\b'
                    ],
                    'base_intensity': 0.6
                },
                FamilyWarmthType.ANTICIPATION: {
                    'patterns': [
                        r'\b(can.*wait|excited.*to.*meet|looking.*forward)\b',
                        r'\b(baby.*will|future|soon|almost.*here)\b'
                    ],
                    'base_intensity': 0.7
                },
                FamilyWarmthType.REASSURANCE: {
                    'patterns': [
                        r'\b(normal|okay|fine|worry|everything.*will)\b',
                        r'\b(been.*there|totally.*normal|same.*thing)\b',
                        r'\b(reassure|comfort|calm|peace)\b'
                    ],
                    'base_intensity': 0.8
                },
                FamilyWarmthType.INCLUSION: {
                    'patterns': [
                        r'\b(we.*all|family|everyone|together|include)\b',
                        r'\b(grandma|grandpa|aunt|uncle|cousin)\b'
                    ],
                    'base_intensity': 0.5
                }
            }
            
            best_match_type = FamilyWarmthType.EMOTIONAL_SUPPORT
            max_intensity = 0.3  # Default minimum intensity
            
            # Check each warmth type for patterns
            for warmth_type, patterns_data in warmth_patterns.items():
                patterns = patterns_data['patterns']
                base_intensity = patterns_data['base_intensity']
                
                pattern_matches = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, comment_lower))
                    pattern_matches += matches
                
                if pattern_matches > 0:
                    # Calculate intensity based on pattern matches and base intensity
                    intensity = min(base_intensity + (pattern_matches * 0.1), 1.0)
                    
                    if intensity > max_intensity:
                        max_intensity = intensity
                        best_match_type = warmth_type
            
            # Boost intensity for longer, more thoughtful comments
            if len(comment_text) > 100:
                max_intensity = min(max_intensity + 0.1, 1.0)
            
            # Boost intensity for comments with multiple sentences (more thoughtful)
            sentence_count = len([s for s in comment_text.split('.') if s.strip()])
            if sentence_count > 2:
                max_intensity = min(max_intensity + 0.1, 1.0)
            
            return best_match_type, max_intensity
            
        except Exception as e:
            logger.error(f"Error analyzing comment warmth: {e}")
            return FamilyWarmthType.EMOTIONAL_SUPPORT, 0.5
    
    def _get_post_interactions(self, post_id: str) -> List[FamilyInteraction]:
        """Get all family interactions for a specific post."""
        statement = select(FamilyInteraction).where(
            FamilyInteraction.post_id == post_id
        )
        return list(self.session.exec(statement).all())
    
    def _get_pregnancy_interactions(
        self, 
        pregnancy_id: str, 
        since_date: datetime
    ) -> List[FamilyInteraction]:
        """Get all family interactions for a pregnancy since a specific date."""
        statement = select(FamilyInteraction).where(
            and_(
                FamilyInteraction.pregnancy_id == pregnancy_id,
                FamilyInteraction.interaction_at >= since_date
            )
        )
        return list(self.session.exec(statement).all())
    
    def _calculate_immediate_family_warmth(
        self, 
        interactions: List[FamilyInteraction], 
        pregnancy_id: str
    ) -> float:
        """Calculate warmth from immediate family members (partner, parents, siblings)."""
        immediate_relationships = ['partner', 'spouse', 'mother', 'father', 'sister', 'brother']
        
        immediate_interactions = [
            i for i in interactions 
            if i.relationship_to_pregnant_person.lower() in immediate_relationships
        ]
        
        if not immediate_interactions:
            return 0.0
        
        # Calculate average warmth intensity from immediate family
        total_warmth = sum(i.warmth_intensity for i in immediate_interactions)
        average_warmth = total_warmth / len(immediate_interactions)
        
        # Boost score based on participation rate (more family members engaging)
        unique_members = len(set(i.user_id for i in immediate_interactions))
        participation_boost = min(unique_members / 4, 1.0)  # Up to 4 immediate family members
        
        return min(average_warmth * (0.7 + 0.3 * participation_boost), 1.0)
    
    def _calculate_extended_family_warmth(
        self, 
        interactions: List[FamilyInteraction], 
        pregnancy_id: str
    ) -> float:
        """Calculate warmth from extended family and friends."""
        extended_relationships = [
            'grandmother', 'grandfather', 'aunt', 'uncle', 'cousin', 
            'friend', 'family_friend', 'coworker'
        ]
        
        extended_interactions = [
            i for i in interactions 
            if i.relationship_to_pregnant_person.lower() in extended_relationships
        ]
        
        if not extended_interactions:
            return 0.0
        
        # Extended family warmth is based on breadth of support
        unique_members = len(set(i.user_id for i in extended_interactions))
        total_warmth = sum(i.warmth_intensity for i in extended_interactions)
        
        # Extended family score based on both participation and warmth
        participation_score = min(unique_members / 8, 1.0)  # Up to 8 extended family members
        warmth_score = total_warmth / len(extended_interactions) if extended_interactions else 0
        
        return min((participation_score + warmth_score) / 2, 1.0)
    
    def _calculate_recent_engagement_warmth(self, interactions: List[FamilyInteraction]) -> float:
        """Calculate warmth based on recency and consistency of engagement."""
        if not interactions:
            return 0.0
        
        now = datetime.utcnow()
        
        # Weight interactions by recency (more recent = higher weight)
        weighted_warmth = 0.0
        total_weight = 0.0
        
        for interaction in interactions:
            hours_ago = (now - interaction.interaction_at).total_seconds() / 3600
            
            # Recency weight decreases exponentially
            if hours_ago <= 2:
                weight = 1.0
            elif hours_ago <= 12:
                weight = 0.8
            elif hours_ago <= 24:
                weight = 0.6
            elif hours_ago <= 72:
                weight = 0.4
            else:
                weight = 0.2
            
            weighted_warmth += interaction.warmth_intensity * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return min(weighted_warmth / total_weight, 1.0)
    
    def _calculate_emotional_support_warmth(self, interactions: List[FamilyInteraction]) -> float:
        """Calculate warmth based on the quality of emotional support provided."""
        if not interactions:
            return 0.0
        
        # Focus on support-type interactions
        support_types = [
            FamilyWarmthType.EMOTIONAL_SUPPORT,
            FamilyWarmthType.REASSURANCE,
            FamilyWarmthType.CELEBRATION
        ]
        
        support_interactions = [
            i for i in interactions 
            if i.interaction_type in support_types
        ]
        
        if not support_interactions:
            # If no explicit support interactions, use general emotional sentiment
            total_warmth = sum(i.warmth_intensity for i in interactions)
            return min(total_warmth / len(interactions), 1.0)
        
        # Calculate weighted emotional support score
        emotional_weights = {
            FamilyWarmthType.EMOTIONAL_SUPPORT: 1.0,
            FamilyWarmthType.REASSURANCE: 0.9,
            FamilyWarmthType.CELEBRATION: 0.8
        }
        
        weighted_support = 0.0
        total_weight = 0.0
        
        for interaction in support_interactions:
            weight = emotional_weights.get(interaction.interaction_type, 0.5)
            weighted_support += interaction.warmth_intensity * weight
            total_weight += weight
        
        return min(weighted_support / total_weight if total_weight > 0 else 0.0, 1.0)
    
    def _calculate_warmth_trend(self, post_id: str, current_score: float) -> str:
        """Calculate warmth trend by comparing with recent warmth calculations."""
        try:
            # Get recent warmth calculations for this post
            statement = select(FamilyWarmthCalculation).where(
                and_(
                    FamilyWarmthCalculation.post_id == post_id,
                    FamilyWarmthCalculation.calculation_date >= datetime.utcnow() - timedelta(days=7)
                )
            ).order_by(FamilyWarmthCalculation.calculation_date.desc())
            
            recent_calculations = list(self.session.exec(statement.limit(3)).all())
            
            if len(recent_calculations) < 2:
                return "stable"
            
            # Compare current score with previous scores
            previous_scores = [calc.warmth_scores.overall_warmth_score for calc in recent_calculations]
            avg_previous = sum(previous_scores) / len(previous_scores)
            
            difference = current_score - avg_previous
            
            if difference > 0.1:
                return "increasing"
            elif difference < -0.1:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating warmth trend: {e}")
            return "stable"
    
    def _calculate_pregnancy_warmth_trend(
        self, 
        pregnancy_id: str, 
        current_score: float,
        days_back: int
    ) -> str:
        """Calculate warmth trend for overall pregnancy."""
        try:
            # Get warmth calculation from the previous period
            previous_period_start = datetime.utcnow() - timedelta(days=days_back * 2)
            previous_period_end = datetime.utcnow() - timedelta(days=days_back)
            
            statement = select(FamilyWarmthCalculation).where(
                and_(
                    FamilyWarmthCalculation.pregnancy_id == pregnancy_id,
                    FamilyWarmthCalculation.calculation_date >= previous_period_start,
                    FamilyWarmthCalculation.calculation_date <= previous_period_end
                )
            ).order_by(FamilyWarmthCalculation.calculation_date.desc())
            
            previous_calculation = self.session.exec(statement.limit(1)).first()
            
            if not previous_calculation:
                return "stable"
            
            previous_score = previous_calculation.warmth_scores.overall_warmth_score
            difference = current_score - previous_score
            
            if difference > 0.15:
                return "increasing"
            elif difference < -0.15:
                return "decreasing"
            else:
                return "stable"
                
        except Exception as e:
            logger.error(f"Error calculating pregnancy warmth trend: {e}")
            return "stable"


class FamilyWarmthService(BaseService):
    """
    Service for managing family warmth calculations and interactions.
    """
    
    def __init__(self):
        super().__init__(FamilyInteraction)
    
    def record_family_interaction(
        self,
        session: Session,
        post_id: Optional[str],
        pregnancy_id: str,
        user_id: str,
        interaction_content: str,
        relationship: str,
        family_group_level: str = "immediate"
    ) -> Optional[FamilyInteraction]:
        """
        Record a family interaction (comment, reaction, etc.) and analyze its warmth.
        """
        try:
            # Analyze the warmth of this interaction
            analyzer = FamilyWarmthAnalyzer(session)
            warmth_type, intensity = analyzer.analyze_comment_warmth(interaction_content)
            
            # Create family interaction record
            interaction = FamilyInteraction(
                post_id=post_id,
                pregnancy_id=pregnancy_id,
                user_id=user_id,
                interaction_type=warmth_type,
                interaction_content=interaction_content,
                warmth_intensity=intensity,
                relationship_to_pregnant_person=relationship,
                family_group_level=family_group_level
            )
            
            session.add(interaction)
            session.commit()
            session.refresh(interaction)
            
            # If this is for a specific post, update the post's warmth score
            if post_id:
                self._update_post_warmth_score(session, post_id)
            
            return interaction
            
        except Exception as e:
            logger.error(f"Error recording family interaction: {e}")
            return None
    
    def calculate_and_store_warmth(
        self,
        session: Session,
        pregnancy_id: str,
        post_id: Optional[str] = None,
        force_recalculate: bool = False
    ) -> Optional[FamilyWarmthCalculation]:
        """
        Calculate and store family warmth scores for a post or pregnancy.
        """
        try:
            analyzer = FamilyWarmthAnalyzer(session)
            
            if post_id:
                # Calculate post-specific warmth
                warmth_scores = analyzer.calculate_post_warmth(post_id)
                
                # Check if we already have a recent calculation
                if not force_recalculate:
                    existing = session.exec(
                        select(FamilyWarmthCalculation).where(
                            and_(
                                FamilyWarmthCalculation.post_id == post_id,
                                FamilyWarmthCalculation.calculation_date >= datetime.utcnow() - timedelta(hours=1)
                            )
                        )
                    ).first()
                    
                    if existing:
                        return existing
            else:
                # Calculate pregnancy-wide warmth
                warmth_scores = analyzer.calculate_pregnancy_warmth(pregnancy_id)
            
            # Get interaction count for metadata
            interactions = analyzer._get_pregnancy_interactions(
                pregnancy_id, 
                datetime.utcnow() - timedelta(days=7)
            )
            
            # Generate insights
            insights = self._generate_warmth_insights(warmth_scores, len(interactions))
            
            # Create warmth calculation record
            calculation = FamilyWarmthCalculation(
                post_id=post_id,
                pregnancy_id=pregnancy_id,
                warmth_scores=warmth_scores,
                total_interactions=len(interactions),
                active_family_members=len(set(i.user_id for i in interactions)),
                calculation_period_days=7,
                warmth_insights=insights
            )
            
            session.add(calculation)
            session.commit()
            session.refresh(calculation)
            
            return calculation
            
        except Exception as e:
            logger.error(f"Error calculating and storing warmth: {e}")
            return None
    
    def get_family_warmth_summary(
        self,
        session: Session,
        pregnancy_id: str,
        days_back: int = 7
    ) -> Dict[str, Any]:
        """
        Get a comprehensive family warmth summary for a pregnancy.
        """
        try:
            # Get or calculate current warmth
            warmth_calculation = self.calculate_and_store_warmth(
                session, pregnancy_id, None, False
            )
            
            if not warmth_calculation:
                return {}
            
            warmth_scores = warmth_calculation.warmth_scores
            
            # Get recent interactions for additional context
            analyzer = FamilyWarmthAnalyzer(session)
            recent_interactions = analyzer._get_pregnancy_interactions(
                pregnancy_id, 
                datetime.utcnow() - timedelta(days=days_back)
            )
            
            # Analyze interaction patterns
            interaction_patterns = self._analyze_interaction_patterns(recent_interactions)
            
            # Generate family activity summary
            family_activity = self._generate_family_activity_summary(recent_interactions)
            
            return {
                'overall_warmth_score': warmth_scores.overall_warmth_score,
                'warmth_breakdown': {
                    'immediate_family': warmth_scores.immediate_family_score,
                    'extended_family': warmth_scores.extended_family_score,
                    'recent_engagement': warmth_scores.recent_engagement_score,
                    'emotional_support': warmth_scores.emotional_support_score
                },
                'warmth_trend': warmth_scores.warmth_trend,
                'total_interactions': warmth_calculation.total_interactions,
                'active_family_members': warmth_calculation.active_family_members,
                'calculation_period_days': warmth_calculation.calculation_period_days,
                'insights': warmth_calculation.warmth_insights,
                'interaction_patterns': interaction_patterns,
                'family_activity': family_activity,
                'calculated_at': warmth_calculation.calculation_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting family warmth summary: {e}")
            return {}
    
    def _update_post_warmth_score(self, session: Session, post_id: str) -> None:
        """Update the family warmth score stored on a post."""
        try:
            analyzer = FamilyWarmthAnalyzer(session)
            warmth_scores = analyzer.calculate_post_warmth(post_id)
            
            # Update post with new warmth score
            post = session.exec(select(Post).where(Post.id == post_id)).first()
            if post:
                post.family_warmth_score = warmth_scores.overall_warmth_score
                session.add(post)
                session.commit()
                
        except Exception as e:
            logger.error(f"Error updating post warmth score: {e}")
    
    def _generate_warmth_insights(
        self, 
        warmth_scores: FamilyWarmthScore, 
        interaction_count: int
    ) -> List[str]:
        """Generate human-readable insights about family warmth patterns."""
        insights = []
        
        # Overall warmth insights
        if warmth_scores.overall_warmth_score >= 0.8:
            insights.append("Your family is showing incredible love and support!")
        elif warmth_scores.overall_warmth_score >= 0.6:
            insights.append("Your family is actively engaged and supportive.")
        elif warmth_scores.overall_warmth_score >= 0.4:
            insights.append("Your family cares deeply and is staying connected.")
        else:
            insights.append("Your family loves you - encourage them to share more!")
        
        # Immediate family insights
        if warmth_scores.immediate_family_score >= 0.8:
            insights.append("Your closest family members are very engaged in your journey.")
        elif warmth_scores.immediate_family_score < 0.4:
            insights.append("Consider sharing more with your partner and immediate family.")
        
        # Extended family insights
        if warmth_scores.extended_family_score >= 0.6:
            insights.append("Your extended family and friends are actively involved.")
        elif warmth_scores.extended_family_score < 0.3:
            insights.append("Your extended family would love to hear more updates!")
        
        # Emotional support insights
        if warmth_scores.emotional_support_score >= 0.8:
            insights.append("Your family is providing wonderful emotional support.")
        elif warmth_scores.emotional_support_score < 0.4:
            insights.append("Share how you're feeling - your family wants to support you.")
        
        # Trend insights
        if warmth_scores.warmth_trend == "increasing":
            insights.append("Family engagement is growing stronger over time.")
        elif warmth_scores.warmth_trend == "decreasing":
            insights.append("Consider sharing more updates to keep family engaged.")
        
        # Interaction volume insights
        if interaction_count >= 20:
            insights.append("Your updates are generating lots of family conversation!")
        elif interaction_count < 5:
            insights.append("Try asking questions to encourage more family interaction.")
        
        return insights
    
    def _analyze_interaction_patterns(self, interactions: List[FamilyInteraction]) -> Dict[str, Any]:
        """Analyze patterns in family interactions."""
        if not interactions:
            return {}
        
        # Analyze by relationship type
        relationship_counts = {}
        relationship_warmth = {}
        
        for interaction in interactions:
            rel = interaction.relationship_to_pregnant_person
            relationship_counts[rel] = relationship_counts.get(rel, 0) + 1
            if rel not in relationship_warmth:
                relationship_warmth[rel] = []
            relationship_warmth[rel].append(interaction.warmth_intensity)
        
        # Calculate average warmth by relationship
        relationship_avg_warmth = {
            rel: sum(warmth_list) / len(warmth_list)
            for rel, warmth_list in relationship_warmth.items()
        }
        
        # Analyze interaction types
        type_counts = {}
        for interaction in interactions:
            interaction_type = interaction.interaction_type.value
            type_counts[interaction_type] = type_counts.get(interaction_type, 0) + 1
        
        return {
            'most_active_relationships': sorted(
                relationship_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3],
            'warmest_relationships': sorted(
                relationship_avg_warmth.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:3],
            'interaction_types': type_counts,
            'total_interactions': len(interactions),
            'unique_family_members': len(set(i.user_id for i in interactions))
        }
    
    def _generate_family_activity_summary(self, interactions: List[FamilyInteraction]) -> Dict[str, Any]:
        """Generate a summary of recent family activity."""
        if not interactions:
            return {}
        
        # Group by day
        daily_activity = {}
        for interaction in interactions:
            day = interaction.interaction_at.date()
            if day not in daily_activity:
                daily_activity[day] = []
            daily_activity[day].append(interaction)
        
        # Find most active day
        most_active_day = max(daily_activity.items(), key=lambda x: len(x[1]))
        
        # Find most supportive interactions
        supportive_interactions = sorted(
            interactions,
            key=lambda x: x.warmth_intensity,
            reverse=True
        )[:3]
        
        return {
            'most_active_day': {
                'date': most_active_day[0].isoformat(),
                'interaction_count': len(most_active_day[1])
            },
            'daily_activity_count': {
                day.isoformat(): len(interactions)
                for day, interactions in daily_activity.items()
            },
            'most_supportive_interactions': [
                {
                    'content': interaction.interaction_content[:100] + "..." 
                    if len(interaction.interaction_content) > 100 
                    else interaction.interaction_content,
                    'relationship': interaction.relationship_to_pregnant_person,
                    'warmth_intensity': interaction.warmth_intensity,
                    'date': interaction.interaction_at.isoformat()
                }
                for interaction in supportive_interactions
            ]
        }


# Global service instance
family_warmth_service = FamilyWarmthService()