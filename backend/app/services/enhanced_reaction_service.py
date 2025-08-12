"""
Enhanced Reaction Service for pregnancy-specific reactions with intensity and family warmth calculations.

This service provides optimized reaction handling with:
- 9 pregnancy-specific reaction types with intensity levels 1-3
- Family warmth contribution calculations
- Milestone-specific reaction handling
- Sub-50ms optimistic reaction support
- Real-time activity broadcasting
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlmodel import Session, select, func
from datetime import datetime, timedelta
from app.models.content import Reaction, Post, Comment, ReactionType, FeedActivity
from app.models.family import FamilyMember, MemberStatus
from app.services.base import BaseService
import logging
import asyncio

logger = logging.getLogger(__name__)


class EnhancedReactionService(BaseService[Reaction]):
    """Enhanced service for reaction operations with family warmth and performance optimizations."""
    
    def __init__(self):
        super().__init__(Reaction)
        
        # Family warmth base values for each reaction type
        self.warmth_base_values = {
            ReactionType.LOVE: 0.12,           # High warmth - core family love
            ReactionType.EXCITED: 0.10,        # High engagement - sharing excitement
            ReactionType.SUPPORTIVE: 0.15,     # Highest warmth - being there, nurturing
            ReactionType.STRONG: 0.13,         # High support - encouragement
            ReactionType.BLESSED: 0.11,        # High appreciation - grateful moments
            ReactionType.HAPPY: 0.08,          # Medium warmth - joy, laughter
            ReactionType.GRATEFUL: 0.12,       # High warmth - appreciation, prayers
            ReactionType.CELEBRATING: 0.14,    # High engagement - milestone celebrations
            ReactionType.AMAZED: 0.09,         # Medium warmth - wonder, development awe
        }
        
        # Milestone reaction bonus multipliers
        self.milestone_bonus = {
            ReactionType.CELEBRATING: 1.5,     # Extra bonus for celebration reactions
            ReactionType.EXCITED: 1.3,         # Bonus for excitement
            ReactionType.SUPPORTIVE: 1.2,      # Bonus for support
            ReactionType.AMAZED: 1.4,          # Bonus for amazement at milestones
        }
    
    async def add_optimistic_reaction(
        self,
        session: Session,
        user_id: str,
        post_id: Optional[str] = None,
        comment_id: Optional[str] = None,
        reaction_type: ReactionType = ReactionType.LOVE,
        intensity: int = 2,
        custom_message: Optional[str] = None,
        is_milestone_reaction: bool = False,
        client_id: Optional[str] = None,
        client_timestamp: Optional[datetime] = None
    ) -> Tuple[Optional[Reaction], Dict[str, Any]]:
        """
        Add reaction with optimistic processing for sub-50ms response.
        
        Returns:
            Tuple of (reaction, performance_metrics)
        """
        start_time = datetime.utcnow()
        performance_metrics = {"latency_ms": 0.0, "optimistic": True, "background_queued": False}
        
        try:
            # Validate intensity
            if intensity < 1 or intensity > 3:
                intensity = 2  # Default to medium intensity
            
            # Check for duplicate client_id to prevent double reactions
            if client_id:
                existing_query = select(Reaction).where(
                    Reaction.client_id == client_id,
                    Reaction.created_at >= start_time - timedelta(minutes=5)
                )
                existing_reaction = session.exec(existing_query).first()
                if existing_reaction:
                    performance_metrics["latency_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
                    performance_metrics["optimistic"] = False
                    return existing_reaction, performance_metrics
            
            # Calculate family warmth contribution
            family_warmth_contribution = self._calculate_family_warmth(
                reaction_type, intensity, is_milestone_reaction
            )
            
            # Create reaction with all enhanced fields
            reaction_data = {
                "user_id": user_id,
                "type": reaction_type,
                "intensity": intensity,
                "custom_message": custom_message,
                "is_milestone_reaction": is_milestone_reaction,
                "family_warmth_contribution": family_warmth_contribution,
                "client_id": client_id,
                "created_at": datetime.utcnow()
            }
            
            if post_id:
                reaction_data["post_id"] = post_id
            if comment_id:
                reaction_data["comment_id"] = comment_id
            
            # Check for existing reaction by same user and update/replace
            existing_reaction = await self._get_existing_user_reaction(
                session, user_id, post_id, comment_id
            )
            
            if existing_reaction:
                # Update existing reaction
                for field, value in reaction_data.items():
                    if hasattr(existing_reaction, field) and field != "created_at":
                        setattr(existing_reaction, field, value)
                session.add(existing_reaction)
                session.commit()
                session.refresh(existing_reaction)
                reaction = existing_reaction
            else:
                # Create new reaction
                reaction = await self.create(session, reaction_data)
                if not reaction:
                    raise Exception("Failed to create reaction")
            
            # Queue background tasks for family warmth and real-time updates
            asyncio.create_task(self._queue_background_processing(
                session, reaction, post_id, comment_id, client_timestamp
            ))
            performance_metrics["background_queued"] = True
            
            # Calculate final latency
            performance_metrics["latency_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return reaction, performance_metrics
            
        except Exception as e:
            logger.error(f"Error in optimistic reaction: {e}")
            performance_metrics["latency_ms"] = (datetime.utcnow() - start_time).total_seconds() * 1000
            performance_metrics["error"] = str(e)
            return None, performance_metrics
    
    async def get_enhanced_reaction_summary(
        self,
        session: Session,
        post_id: Optional[str] = None,
        comment_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive reaction summary with family warmth data."""
        try:
            # Build query for reactions
            query = select(Reaction)
            if post_id:
                query = query.where(Reaction.post_id == post_id)
            elif comment_id:
                query = query.where(Reaction.comment_id == comment_id)
            else:
                return {}
            
            reactions = session.exec(query).all()
            
            # Calculate summary statistics
            reaction_counts = {}
            intensity_breakdown = {}
            total_family_warmth = 0.0
            milestone_reactions = 0
            user_reaction = None
            
            for reaction in reactions:
                # Count by type
                reaction_type = reaction.type.value if hasattr(reaction.type, 'value') else str(reaction.type)
                reaction_counts[reaction_type] = reaction_counts.get(reaction_type, 0) + 1
                
                # Track intensity breakdown
                if reaction_type not in intensity_breakdown:
                    intensity_breakdown[reaction_type] = {"1": 0, "2": 0, "3": 0}
                intensity_breakdown[reaction_type][str(reaction.intensity)] += 1
                
                # Sum family warmth
                total_family_warmth += reaction.family_warmth_contribution
                
                # Count milestone reactions
                if reaction.is_milestone_reaction:
                    milestone_reactions += 1
                
                # Check for user's reaction
                if user_id and reaction.user_id == user_id:
                    user_reaction = {
                        "type": reaction_type,
                        "intensity": reaction.intensity,
                        "is_milestone": reaction.is_milestone_reaction,
                        "custom_message": reaction.custom_message,
                        "created_at": reaction.created_at.isoformat()
                    }
            
            # Calculate average intensity per reaction type
            average_intensities = {}
            for reaction_type, intensities in intensity_breakdown.items():
                total_reactions = sum(intensities.values())
                if total_reactions > 0:
                    weighted_sum = (1 * intensities["1"] + 2 * intensities["2"] + 3 * intensities["3"])
                    average_intensities[reaction_type] = round(weighted_sum / total_reactions, 2)
            
            # Get top 3 reaction types
            top_reactions = sorted(reaction_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            return {
                "total_count": len(reactions),
                "reaction_counts": reaction_counts,
                "intensity_breakdown": intensity_breakdown,
                "average_intensities": average_intensities,
                "total_family_warmth": round(total_family_warmth, 3),
                "milestone_reaction_count": milestone_reactions,
                "top_reactions": [{"type": r[0], "count": r[1]} for r in top_reactions],
                "user_reaction": user_reaction,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting enhanced reaction summary: {e}")
            return {}
    
    async def remove_user_reaction(
        self,
        session: Session,
        user_id: str,
        post_id: Optional[str] = None,
        comment_id: Optional[str] = None
    ) -> bool:
        """Remove user's reaction and update counters."""
        try:
            # Find user's existing reaction
            existing_reaction = await self._get_existing_user_reaction(
                session, user_id, post_id, comment_id
            )
            
            if not existing_reaction:
                return False
            
            # Store family warmth to subtract
            warmth_to_subtract = existing_reaction.family_warmth_contribution
            
            # Delete the reaction
            await self.delete(session, existing_reaction.id)
            
            # Update counters on parent (post or comment)
            if post_id:
                await self._update_post_reaction_summary(session, post_id, remove_warmth=warmth_to_subtract)
            elif comment_id:
                await self._update_comment_reaction_summary(session, comment_id, remove_warmth=warmth_to_subtract)
            
            # Queue background task for real-time updates
            asyncio.create_task(self._broadcast_reaction_removal(user_id, post_id, comment_id))
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing user reaction: {e}")
            return False
    
    async def get_family_reaction_insights(
        self,
        session: Session,
        pregnancy_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get family-wide reaction insights for analytics."""
        try:
            from app.models.content import Post
            from app.models.family import FamilyMember
            
            # Get recent posts for this pregnancy
            since_date = datetime.utcnow() - timedelta(days=days)
            
            posts_query = select(Post).where(
                Post.pregnancy_id == pregnancy_id,
                Post.created_at >= since_date
            )
            posts = session.exec(posts_query).all()
            post_ids = [post.id for post in posts]
            
            if not post_ids:
                return {"message": "No recent posts found"}
            
            # Get all reactions on these posts
            reactions_query = select(Reaction).where(
                Reaction.post_id.in_(post_ids)
            )
            reactions = session.exec(reactions_query).all()
            
            # Get family members for this pregnancy
            members_query = select(FamilyMember).where(
                FamilyMember.pregnancy_id == pregnancy_id,
                FamilyMember.status == MemberStatus.ACTIVE
            )
            family_members = session.exec(members_query).all()
            family_member_ids = [member.user_id for member in family_members]
            
            # Analyze reactions
            family_reactions = [r for r in reactions if r.user_id in family_member_ids]
            
            reaction_analysis = {
                "total_reactions": len(reactions),
                "family_reactions": len(family_reactions),
                "family_participation_rate": round(len(family_reactions) / max(len(reactions), 1), 2),
                "total_family_warmth": sum(r.family_warmth_contribution for r in family_reactions),
                "average_intensity": round(sum(r.intensity for r in family_reactions) / max(len(family_reactions), 1), 2),
                "milestone_celebrations": len([r for r in family_reactions if r.is_milestone_reaction]),
                "reaction_distribution": {},
                "most_supportive_members": [],
                "engagement_trends": []
            }
            
            # Reaction distribution by type
            for reaction in family_reactions:
                reaction_type = reaction.type.value if hasattr(reaction.type, 'value') else str(reaction.type)
                if reaction_type not in reaction_analysis["reaction_distribution"]:
                    reaction_analysis["reaction_distribution"][reaction_type] = {
                        "count": 0,
                        "total_intensity": 0,
                        "average_intensity": 0,
                        "family_warmth": 0
                    }
                
                dist = reaction_analysis["reaction_distribution"][reaction_type]
                dist["count"] += 1
                dist["total_intensity"] += reaction.intensity
                dist["family_warmth"] += reaction.family_warmth_contribution
                dist["average_intensity"] = round(dist["total_intensity"] / dist["count"], 2)
            
            # Most supportive family members
            member_support = {}
            for reaction in family_reactions:
                user_id = reaction.user_id
                if user_id not in member_support:
                    member_support[user_id] = {
                        "total_warmth": 0,
                        "reaction_count": 0,
                        "average_intensity": 0,
                        "milestone_reactions": 0
                    }
                
                support = member_support[user_id]
                support["total_warmth"] += reaction.family_warmth_contribution
                support["reaction_count"] += 1
                support["average_intensity"] = round(
                    (support["average_intensity"] * (support["reaction_count"] - 1) + reaction.intensity) / support["reaction_count"], 2
                )
                if reaction.is_milestone_reaction:
                    support["milestone_reactions"] += 1
            
            # Sort by total warmth contribution
            top_supporters = sorted(
                [(user_id, data) for user_id, data in member_support.items()],
                key=lambda x: x[1]["total_warmth"],
                reverse=True
            )[:5]
            
            reaction_analysis["most_supportive_members"] = [
                {"user_id": user_id, **data} for user_id, data in top_supporters
            ]
            
            return reaction_analysis
            
        except Exception as e:
            logger.error(f"Error getting family reaction insights: {e}")
            return {"error": str(e)}
    
    def _calculate_family_warmth(
        self,
        reaction_type: ReactionType,
        intensity: int,
        is_milestone_reaction: bool
    ) -> float:
        """Calculate family warmth contribution for a reaction."""
        base_value = self.warmth_base_values.get(reaction_type, 0.05)
        
        # Apply intensity multiplier (1 = 0.5x, 2 = 1.0x, 3 = 1.5x)
        intensity_multiplier = 0.5 + (intensity - 1) * 0.5
        
        # Apply milestone bonus if applicable
        milestone_multiplier = 1.0
        if is_milestone_reaction:
            milestone_multiplier = self.milestone_bonus.get(reaction_type, 1.2)
        
        final_warmth = base_value * intensity_multiplier * milestone_multiplier
        
        # Cap at maximum warmth per reaction
        return min(final_warmth, 0.25)
    
    async def _get_existing_user_reaction(
        self,
        session: Session,
        user_id: str,
        post_id: Optional[str] = None,
        comment_id: Optional[str] = None
    ) -> Optional[Reaction]:
        """Get user's existing reaction on post or comment."""
        query = select(Reaction).where(Reaction.user_id == user_id)
        
        if post_id:
            query = query.where(Reaction.post_id == post_id)
        elif comment_id:
            query = query.where(Reaction.comment_id == comment_id)
        else:
            return None
        
        return session.exec(query).first()
    
    async def _queue_background_processing(
        self,
        session: Session,
        reaction: Reaction,
        post_id: Optional[str],
        comment_id: Optional[str],
        client_timestamp: Optional[datetime]
    ):
        """Queue background tasks for reaction processing."""
        try:
            # Update reaction summary on parent
            if post_id:
                await self._update_post_reaction_summary(session, post_id)
            elif comment_id:
                await self._update_comment_reaction_summary(session, comment_id)
            
            # Create feed activity for real-time broadcasting
            activity_data = {
                "reaction_type": reaction.type.value if hasattr(reaction.type, 'value') else str(reaction.type),
                "intensity": reaction.intensity,
                "is_milestone": reaction.is_milestone_reaction,
                "family_warmth_delta": reaction.family_warmth_contribution
            }
            
            if reaction.custom_message:
                activity_data["custom_message"] = reaction.custom_message
            
            # Determine pregnancy_id for the activity
            pregnancy_id = None
            if post_id:
                post = session.get(Post, post_id)
                pregnancy_id = post.pregnancy_id if post else None
            elif comment_id:
                comment = session.get(Comment, comment_id)
                if comment:
                    post = session.get(Post, comment.post_id)
                    pregnancy_id = post.pregnancy_id if post else None
            
            if pregnancy_id:
                activity = FeedActivity(
                    pregnancy_id=pregnancy_id,
                    user_id=reaction.user_id,
                    activity_type="reaction",
                    target_id=post_id or comment_id,
                    target_type="post" if post_id else "comment",
                    activity_data=activity_data,
                    client_timestamp=client_timestamp,
                    broadcast_priority=4 if reaction.is_milestone_reaction else 2
                )
                
                session.add(activity)
                session.commit()
            
        except Exception as e:
            logger.error(f"Error in background processing: {e}")
    
    async def _update_post_reaction_summary(
        self,
        session: Session,
        post_id: str,
        remove_warmth: float = 0.0
    ):
        """Update cached reaction summary on post."""
        try:
            post = session.get(Post, post_id)
            if not post:
                return
            
            # Get all reactions for this post
            reactions_query = select(Reaction).where(Reaction.post_id == post_id)
            reactions = session.exec(reactions_query).all()
            
            # Update reaction summary
            reaction_summary = {}
            total_warmth = 0.0
            
            for reaction in reactions:
                reaction_type = reaction.type.value if hasattr(reaction.type, 'value') else str(reaction.type)
                reaction_summary[reaction_type] = reaction_summary.get(reaction_type, 0) + 1
                total_warmth += reaction.family_warmth_contribution
            
            # Subtract removed warmth if applicable
            total_warmth -= remove_warmth
            
            post.reaction_summary = reaction_summary
            post.reaction_count = len(reactions)
            post.family_warmth_score = min(total_warmth, 1.0)  # Cap at 1.0
            
            session.add(post)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error updating post reaction summary: {e}")
    
    async def _update_comment_reaction_summary(
        self,
        session: Session,
        comment_id: str,
        remove_warmth: float = 0.0
    ):
        """Update cached reaction summary on comment."""
        try:
            comment = session.get(Comment, comment_id)
            if not comment:
                return
            
            # Get all reactions for this comment
            reactions_query = select(Reaction).where(Reaction.comment_id == comment_id)
            reactions = session.exec(reactions_query).all()
            
            # Update reaction summary
            reaction_summary = {}
            total_warmth = 0.0
            
            for reaction in reactions:
                reaction_type = reaction.type.value if hasattr(reaction.type, 'value') else str(reaction.type)
                reaction_summary[reaction_type] = reaction_summary.get(reaction_type, 0) + 1
                total_warmth += reaction.family_warmth_contribution
            
            # Subtract removed warmth if applicable
            total_warmth -= remove_warmth
            
            comment.reaction_summary = reaction_summary
            comment.reaction_count = len(reactions)
            comment.family_warmth_contribution = min(total_warmth, 1.0)
            
            session.add(comment)
            session.commit()
            
        except Exception as e:
            logger.error(f"Error updating comment reaction summary: {e}")
    
    async def _broadcast_reaction_removal(
        self,
        user_id: str,
        post_id: Optional[str],
        comment_id: Optional[str]
    ):
        """Broadcast reaction removal to real-time subscribers."""
        try:
            # This would integrate with WebSocket service
            # For now, just log the action
            logger.info(f"Broadcasting reaction removal: user={user_id}, post={post_id}, comment={comment_id}")
            
        except Exception as e:
            logger.error(f"Error broadcasting reaction removal: {e}")


# Global service instance
enhanced_reaction_service = EnhancedReactionService()