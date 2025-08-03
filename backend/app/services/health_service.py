"""
Health service for database operations using SQLModel sessions.

This service handles all health-related database operations including health tracking,
symptoms, weight, mood, and health alerts.
"""

from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from datetime import datetime, date, timedelta
from app.models.health import (
    PregnancyHealth, HealthAlert, SymptomTracking, WeightEntry, MoodEntry,
    EnergyLevel, SymptomFrequency, WeightTrend, HealthSnapshot, 
    WeightTracking, SymptomSummary, MoodTracking, SleepSummary
)
from app.services.base import BaseService
import logging

logger = logging.getLogger(__name__)


class PregnancyHealthService(BaseService[PregnancyHealth]):
    """Service for pregnancy health-related database operations."""
    
    def __init__(self):
        super().__init__(PregnancyHealth)
    
    async def get_by_pregnancy_id(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> Optional[PregnancyHealth]:
        """Get health record for a pregnancy."""
        try:
            statement = select(PregnancyHealth).where(
                PregnancyHealth.pregnancy_id == pregnancy_id
            )
            result = session.exec(statement).first()
            return result
        except Exception as e:
            logger.error(f"Error getting health record for pregnancy {pregnancy_id}: {e}")
            return None
    
    async def create_health_record(
        self, 
        session: Session, 
        pregnancy_id: str,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> Optional[PregnancyHealth]:
        """Create a new health record for a pregnancy."""
        try:
            # Create default health snapshot if none provided
            if not initial_data:
                from app.models.health import HealthSharingSettings, WeightRange
                
                default_weight_range = WeightRange(
                    min_gain=11.5,  # kg
                    max_gain=16.0,  # kg
                    unit="kg"
                )
                
                default_weight_tracking = WeightTracking(
                    current=60.0,  # Default - should be updated
                    starting_weight=60.0,
                    total_gain=0.0,
                    weekly_gain=0.0,
                    recommended_range=default_weight_range,
                    trend=WeightTrend.NORMAL
                )
                
                default_mood = MoodTracking(
                    current_mood="neutral",
                    mood_score=5,
                    last_updated=datetime.utcnow()
                )
                
                default_sleep = SleepSummary(
                    average_hours=7.5,
                    quality_score=7,
                    common_issues=[],
                    last_updated=datetime.utcnow()
                )
                
                default_snapshot = HealthSnapshot(
                    week=4,  # Default starting week
                    weight=default_weight_tracking,
                    symptoms=[],
                    mood=default_mood,
                    energy=EnergyLevel.NORMAL,
                    sleep=default_sleep,
                    appointments=[],
                    last_updated=datetime.utcnow()
                )
                
                health_data = {
                    "pregnancy_id": pregnancy_id,
                    "current_metrics": default_snapshot,
                    "sharing": HealthSharingSettings(),
                    "alerts": []
                }
            else:
                health_data = initial_data
                health_data["pregnancy_id"] = pregnancy_id
            
            return await self.create(session, health_data)
        except Exception as e:
            logger.error(f"Error creating health record: {e}")
            return None
    
    async def update_health_record(
        self, 
        session: Session, 
        pregnancy_id: str, 
        health_data: Dict[str, Any]
    ) -> Optional[PregnancyHealth]:
        """Update health record for a pregnancy."""
        try:
            db_health = await self.get_by_pregnancy_id(session, pregnancy_id)
            if not db_health:
                return None
            
            health_data["updated_at"] = datetime.utcnow()
            
            # Update last_updated in current_metrics if provided
            if "current_metrics" in health_data:
                health_data["current_metrics"]["last_updated"] = datetime.utcnow()
            
            return await self.update(session, db_health, health_data)
        except Exception as e:
            logger.error(f"Error updating health record for pregnancy {pregnancy_id}: {e}")
            return None
    
    async def get_or_create_health_record(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> Optional[PregnancyHealth]:
        """Get health record or create if it doesn't exist."""
        try:
            health_record = await self.get_by_pregnancy_id(session, pregnancy_id)
            if not health_record:
                health_record = await self.create_health_record(session, pregnancy_id)
            return health_record
        except Exception as e:
            logger.error(f"Error getting or creating health record: {e}")
            return None
    
    async def update_health_snapshot(
        self, 
        session: Session, 
        pregnancy_id: str,
        snapshot_data: Dict[str, Any]
    ) -> Optional[PregnancyHealth]:
        """Update current health snapshot."""
        try:
            health_record = await self.get_by_pregnancy_id(session, pregnancy_id)
            if not health_record:
                return None
            
            # Merge with existing snapshot
            current_snapshot = health_record.current_metrics
            if isinstance(current_snapshot, dict):
                current_snapshot.update(snapshot_data)
            else:
                # If it's a Pydantic model, convert to dict, update, then back
                current_dict = current_snapshot.dict()
                current_dict.update(snapshot_data)
                current_snapshot = current_dict
            
            current_snapshot["last_updated"] = datetime.utcnow()
            
            return await self.update_health_record(
                session, pregnancy_id, {"current_metrics": current_snapshot}
            )
        except Exception as e:
            logger.error(f"Error updating health snapshot: {e}")
            return None


class HealthAlertService(BaseService[HealthAlert]):
    """Service for health alert-related database operations."""
    
    def __init__(self):
        super().__init__(HealthAlert)
    
    async def get_active_alerts(
        self, 
        session: Session, 
        pregnancy_health_id: str
    ) -> List[HealthAlert]:
        """Get active alerts for a health record."""
        try:
            statement = select(HealthAlert).where(
                HealthAlert.pregnancy_health_id == pregnancy_health_id,
                HealthAlert.is_active == True,
                HealthAlert.resolved == False
            ).order_by(HealthAlert.created_at.desc())
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting active alerts: {e}")
            return []
    
    async def create_alert(
        self, 
        session: Session, 
        alert_data: Dict[str, Any]
    ) -> Optional[HealthAlert]:
        """Create a new health alert."""
        try:
            return await self.create(session, alert_data)
        except Exception as e:
            logger.error(f"Error creating health alert: {e}")
            return None
    
    async def acknowledge_alert(
        self, 
        session: Session, 
        alert_id: str
    ) -> Optional[HealthAlert]:
        """Mark an alert as acknowledged."""
        try:
            alert = await self.get_by_id(session, alert_id)
            if not alert:
                return None
            
            update_data = {
                "acknowledged": True,
                "acknowledged_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            return await self.update(session, alert, update_data)
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert_id}: {e}")
            return None
    
    async def resolve_alert(
        self, 
        session: Session, 
        alert_id: str,
        resolution_notes: Optional[str] = None
    ) -> Optional[HealthAlert]:
        """Mark an alert as resolved."""
        try:
            alert = await self.get_by_id(session, alert_id)
            if not alert:
                return None
            
            update_data = {
                "resolved": True,
                "resolved_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if resolution_notes:
                update_data["resolution_notes"] = resolution_notes
            
            return await self.update(session, alert, update_data)
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return None


class SymptomTrackingService(BaseService[SymptomTracking]):
    """Service for symptom tracking-related database operations."""
    
    def __init__(self):
        super().__init__(SymptomTracking)
    
    async def get_pregnancy_symptoms(
        self, 
        session: Session, 
        pregnancy_id: str,
        days_back: Optional[int] = None
    ) -> List[SymptomTracking]:
        """Get symptom tracking entries for a pregnancy."""
        try:
            statement = select(SymptomTracking).where(
                SymptomTracking.pregnancy_id == pregnancy_id
            )
            
            if days_back:
                cutoff_date = date.today() - timedelta(days=days_back)
                statement = statement.where(
                    SymptomTracking.date_recorded >= cutoff_date
                )
            
            statement = statement.order_by(SymptomTracking.date_recorded.desc())
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting symptoms for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def get_symptom_trends(
        self, 
        session: Session, 
        pregnancy_id: str,
        symptom_name: str,
        weeks_back: int = 4
    ) -> List[SymptomTracking]:
        """Get trend data for a specific symptom."""
        try:
            cutoff_date = date.today() - timedelta(weeks=weeks_back)
            
            statement = select(SymptomTracking).where(
                SymptomTracking.pregnancy_id == pregnancy_id,
                SymptomTracking.symptom_name == symptom_name,
                SymptomTracking.date_recorded >= cutoff_date
            ).order_by(SymptomTracking.date_recorded.asc())
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting symptom trends: {e}")
            return []
    
    async def create_symptom_entry(
        self, 
        session: Session, 
        symptom_data: Dict[str, Any]
    ) -> Optional[SymptomTracking]:
        """Create a new symptom tracking entry."""
        try:
            return await self.create(session, symptom_data)
        except Exception as e:
            logger.error(f"Error creating symptom entry: {e}")
            return None
    
    async def get_recent_symptom_summary(
        self, 
        session: Session, 
        pregnancy_id: str,
        days_back: int = 7
    ) -> List[SymptomSummary]:
        """Get summary of recent symptoms."""
        try:
            cutoff_date = date.today() - timedelta(days=days_back)
            
            # Get recent symptoms grouped by symptom name
            statement = select(SymptomTracking).where(
                SymptomTracking.pregnancy_id == pregnancy_id,
                SymptomTracking.date_recorded >= cutoff_date
            ).order_by(SymptomTracking.date_recorded.desc())
            
            symptoms = session.exec(statement).all()
            
            # Group by symptom name and create summaries
            symptom_groups = {}
            for symptom in symptoms:
                if symptom.symptom_name not in symptom_groups:
                    symptom_groups[symptom.symptom_name] = []
                symptom_groups[symptom.symptom_name].append(symptom)
            
            summaries = []
            for symptom_name, entries in symptom_groups.items():
                if entries:
                    # Calculate averages and trends
                    avg_severity = sum(e.severity for e in entries) / len(entries)
                    most_frequent = max(set(e.frequency for e in entries), 
                                      key=lambda x: [e.frequency for e in entries].count(x))
                    
                    summary = SymptomSummary(
                        symptom=symptom_name,
                        frequency=most_frequent,
                        severity=int(avg_severity),
                        trending=SymptomTrend.SAME,  # Would need more logic for actual trend
                        last_reported=entries[0].date_recorded
                    )
                    summaries.append(summary)
            
            return summaries
        except Exception as e:
            logger.error(f"Error getting symptom summary: {e}")
            return []


class WeightEntryService(BaseService[WeightEntry]):
    """Service for weight tracking-related database operations."""
    
    def __init__(self):
        super().__init__(WeightEntry)
    
    async def get_pregnancy_weights(
        self, 
        session: Session, 
        pregnancy_id: str,
        limit: Optional[int] = None
    ) -> List[WeightEntry]:
        """Get weight entries for a pregnancy."""
        try:
            statement = select(WeightEntry).where(
                WeightEntry.pregnancy_id == pregnancy_id
            ).order_by(WeightEntry.date_recorded.desc())
            
            if limit:
                statement = statement.limit(limit)
            
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting weights for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def create_weight_entry(
        self, 
        session: Session, 
        weight_data: Dict[str, Any]
    ) -> Optional[WeightEntry]:
        """Create a new weight entry."""
        try:
            return await self.create(session, weight_data)
        except Exception as e:
            logger.error(f"Error creating weight entry: {e}")
            return None
    
    async def get_weight_tracking_summary(
        self, 
        session: Session, 
        pregnancy_id: str
    ) -> Optional[WeightTracking]:
        """Get weight tracking summary for a pregnancy."""
        try:
            weights = await self.get_pregnancy_weights(session, pregnancy_id, 10)
            
            if not weights:
                return None
            
            # Sort by date ascending to get proper progression
            weights.sort(key=lambda x: x.date_recorded)
            
            current_weight = weights[-1].weight
            starting_weight = weights[0].weight
            total_gain = current_weight - starting_weight
            
            # Calculate weekly gain (approximate)
            if len(weights) >= 2:
                recent_weight = weights[-2].weight
                days_between = (weights[-1].date_recorded - weights[-2].date_recorded).days
                if days_between > 0:
                    weekly_gain = (current_weight - recent_weight) * (7 / days_between)
                else:
                    weekly_gain = 0.0
            else:
                weekly_gain = 0.0
            
            # Default recommended range (would normally be calculated based on BMI)
            from app.models.health import WeightRange
            recommended_range = WeightRange(
                min_gain=11.5,
                max_gain=16.0,
                unit="kg"
            )
            
            # Determine trend
            if weekly_gain > 0.5:
                trend = WeightTrend.FAST
            elif weekly_gain < 0.2:
                trend = WeightTrend.SLOW
            else:
                trend = WeightTrend.NORMAL
            
            return WeightTracking(
                current=current_weight,
                starting_weight=starting_weight,
                total_gain=total_gain,
                weekly_gain=weekly_gain,
                recommended_range=recommended_range,
                trend=trend
            )
        except Exception as e:
            logger.error(f"Error getting weight tracking summary: {e}")
            return None


class MoodEntryService(BaseService[MoodEntry]):
    """Service for mood tracking-related database operations."""
    
    def __init__(self):
        super().__init__(MoodEntry)
    
    async def get_pregnancy_moods(
        self, 
        session: Session, 
        pregnancy_id: str,
        days_back: Optional[int] = None
    ) -> List[MoodEntry]:
        """Get mood entries for a pregnancy."""
        try:
            statement = select(MoodEntry).where(
                MoodEntry.pregnancy_id == pregnancy_id
            )
            
            if days_back:
                cutoff_date = date.today() - timedelta(days=days_back)
                statement = statement.where(
                    MoodEntry.date_recorded >= cutoff_date
                )
            
            statement = statement.order_by(MoodEntry.date_recorded.desc())
            results = session.exec(statement).all()
            return results
        except Exception as e:
            logger.error(f"Error getting moods for pregnancy {pregnancy_id}: {e}")
            return []
    
    async def create_mood_entry(
        self, 
        session: Session, 
        mood_data: Dict[str, Any]
    ) -> Optional[MoodEntry]:
        """Create a new mood entry."""
        try:
            return await self.create(session, mood_data)
        except Exception as e:
            logger.error(f"Error creating mood entry: {e}")
            return None
    
    async def get_mood_tracking_summary(
        self, 
        session: Session, 
        pregnancy_id: str,
        days_back: int = 7
    ) -> Optional[MoodTracking]:
        """Get mood tracking summary."""
        try:
            moods = await self.get_pregnancy_moods(session, pregnancy_id, days_back)
            
            if not moods:
                return None
            
            # Calculate averages
            avg_score = sum(m.mood_score for m in moods) / len(moods)
            most_recent = moods[0]  # Already sorted by date desc
            
            return MoodTracking(
                current_mood=most_recent.mood,
                mood_score=int(avg_score),
                notes=most_recent.notes,
                last_updated=most_recent.date_recorded
            )
        except Exception as e:
            logger.error(f"Error getting mood tracking summary: {e}")
            return None


# Global service instances
pregnancy_health_service = PregnancyHealthService()
health_alert_service = HealthAlertService()
symptom_tracking_service = SymptomTrackingService()
weight_entry_service = WeightEntryService()
mood_entry_service = MoodEntryService()