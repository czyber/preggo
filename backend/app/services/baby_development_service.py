from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_, func
from app.models.baby_development import BabyDevelopment, TrimesterType
from app.schemas.baby_development import (
    BabyDevelopmentCreate, BabyDevelopmentUpdate,
    BabyDevelopmentSearch, BabyDevelopmentStats
)


class BabyDevelopmentService:
    """Service for managing baby development data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get(self, development_id: str) -> Optional[BabyDevelopment]:
        """Get a baby development record by ID"""
        return self.db.exec(
            select(BabyDevelopment).where(BabyDevelopment.id == development_id)
        ).first()
    
    def create(self, development_data: BabyDevelopmentCreate) -> BabyDevelopment:
        """Create a new baby development record"""
        development = BabyDevelopment(**development_data.model_dump())
        self.db.add(development)
        self.db.commit()
        self.db.refresh(development)
        return development
    
    def update(self, development_id: str, development_data: BabyDevelopmentUpdate) -> Optional[BabyDevelopment]:
        """Update an existing baby development record"""
        development = self.get(development_id)
        if not development:
            return None
        
        update_data = development_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(development, field, value)
        
        self.db.add(development)
        self.db.commit()
        self.db.refresh(development)
        return development
    
    def get_by_day(self, day: int) -> Optional[BabyDevelopment]:
        """Get baby development information for a specific pregnancy day"""
        return self.db.exec(
            select(BabyDevelopment).where(
                and_(
                    BabyDevelopment.day_of_pregnancy == day,
                    BabyDevelopment.is_active == True
                )
            )
        ).first()
    
    def get_by_week(self, week: int) -> List[BabyDevelopment]:
        """Get all baby development records for a specific week"""
        return self.db.exec(
            select(BabyDevelopment).where(
                and_(
                    BabyDevelopment.week_number == week,
                    BabyDevelopment.is_active == True
                )
            ).order_by(BabyDevelopment.day_of_pregnancy)
        ).all()
    
    def get_by_trimester(
        self, 
        trimester: TrimesterType, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BabyDevelopment]:
        """Get baby development records for a specific trimester"""
        return self.db.exec(
            select(BabyDevelopment).where(
                and_(
                    BabyDevelopment.trimester == trimester,
                    BabyDevelopment.is_active == True
                )
            ).order_by(BabyDevelopment.day_of_pregnancy).offset(skip).limit(limit)
        ).all()
    
    def search_developments(
        self, 
        search_params: BabyDevelopmentSearch,
        skip: int = 0,
        limit: int = 100
    ) -> List[BabyDevelopment]:
        """Advanced search for baby development records"""
        query = select(BabyDevelopment).where(BabyDevelopment.is_active == search_params.is_active)
        
        # Apply filters based on search parameters
        if search_params.week_number is not None:
            query = query.where(BabyDevelopment.week_number == search_params.week_number)
        
        if search_params.trimester is not None:
            query = query.where(BabyDevelopment.trimester == search_params.trimester)
        
        if search_params.day_range_start is not None:
            query = query.where(BabyDevelopment.day_of_pregnancy >= search_params.day_range_start)
        
        if search_params.day_range_end is not None:
            query = query.where(BabyDevelopment.day_of_pregnancy <= search_params.day_range_end)
        
        if search_params.search_text:
            search_term = f"%{search_params.search_text}%"
            query = query.where(
                or_(
                    BabyDevelopment.title.ilike(search_term),
                    BabyDevelopment.brief_description.ilike(search_term),
                    BabyDevelopment.baby_size_comparison.ilike(search_term),
                    BabyDevelopment.fun_fact.ilike(search_term)
                )
            )
        
        query = query.order_by(BabyDevelopment.day_of_pregnancy).offset(skip).limit(limit)
        
        return self.db.exec(query).all()
    
    def get_stats(self) -> BabyDevelopmentStats:
        """Get statistics about the baby development database"""
        total_days = self.db.exec(select(func.count(BabyDevelopment.id))).first()
        active_records = self.db.exec(
            select(func.count(BabyDevelopment.id)).where(BabyDevelopment.is_active == True)
        ).first()
        inactive_records = total_days - active_records if total_days and active_records else 0
        
        # Count days per trimester
        trimester_counts = {}
        for trimester_num in [1, 2, 3]:
            trimester_enum = TrimesterType(trimester_num)
            count = self.db.exec(
                select(func.count(BabyDevelopment.id)).where(
                    and_(
                        BabyDevelopment.trimester == trimester_enum,
                        BabyDevelopment.is_active == True
                    )
                )
            ).first()
            trimester_counts[trimester_num] = count or 0
        
        # Get weeks covered
        weeks_covered = self.db.exec(
            select(func.count(func.distinct(BabyDevelopment.week_number))).where(
                BabyDevelopment.is_active == True
            )
        ).first()
        
        # Get last update timestamp
        last_updated = self.db.exec(
            select(func.max(BabyDevelopment.updated_at)).where(
                BabyDevelopment.is_active == True
            )
        ).first()
        
        return BabyDevelopmentStats(
            total_days=total_days or 0,
            days_per_trimester=trimester_counts,
            weeks_covered=weeks_covered or 0,
            last_updated=last_updated,
            active_records=active_records or 0,
            inactive_records=inactive_records or 0
        )
    
    def get_day_range(self, start_day: int, end_day: int) -> List[BabyDevelopment]:
        """Get development data for a range of days"""
        return self.db.exec(
            select(BabyDevelopment).where(
                and_(
                    BabyDevelopment.day_of_pregnancy >= start_day,
                    BabyDevelopment.day_of_pregnancy <= end_day,
                    BabyDevelopment.is_active == True
                )
            ).order_by(BabyDevelopment.day_of_pregnancy)
        ).all()
    
    def get_weekly_summary(self) -> Dict[int, List[BabyDevelopment]]:
        """Get all developments organized by week"""
        developments = self.db.exec(
            select(BabyDevelopment).where(
                BabyDevelopment.is_active == True
            ).order_by(BabyDevelopment.day_of_pregnancy)
        ).all()
        
        weekly_data = {}
        for dev in developments:
            if dev.week_number not in weekly_data:
                weekly_data[dev.week_number] = []
            weekly_data[dev.week_number].append(dev)
        
        return weekly_data
    
    def soft_delete(self, development_id: str) -> bool:
        """Soft delete a baby development record (marks as inactive)"""
        development = self.get(development_id)
        if development:
            development.is_active = False
            self.db.add(development)
            self.db.commit()
            return True
        return False
    
    def bulk_create_from_json(self, json_data_list: List[Dict[str, Any]]) -> List[BabyDevelopment]:
        """Bulk create baby development records from JSON data"""
        created_records = []
        
        for data in json_data_list:
            # Convert JSON format to our model format
            development_data = self._convert_json_to_model(data)
            
            try:
                # Check if record already exists for this day
                existing = self.get_by_day(development_data.day_of_pregnancy)
                if not existing:
                    created_record = self.create(development_data)
                    created_records.append(created_record)
            except Exception as e:
                # Log the error but continue processing other records
                print(f"Error creating record for day {development_data.day_of_pregnancy}: {e}")
                continue
        
        return created_records
    
    def _convert_json_to_model(self, json_data: Dict[str, Any]) -> BabyDevelopmentCreate:
        """Convert JSON content format to our model format"""
        week = json_data.get('week', 1)
        # Calculate day from week (assuming each week starts on day 1 of that week)
        day_of_pregnancy = (week - 1) * 7 + 1
        
        # Extract size comparison - prioritize creative over traditional
        size_comparison = json_data.get('size_comparison', {})
        if isinstance(size_comparison, dict):
            baby_size_comparison = (
                size_comparison.get('creative') or 
                size_comparison.get('traditional') or 
                size_comparison.get('personal') or
                "Unknown size"
            )
        else:
            baby_size_comparison = str(size_comparison) or "Unknown size"
        
        # Combine highlights and facts into development highlights
        development_highlights = []
        development_highlights.extend(json_data.get('development_highlights', []))
        development_highlights.extend(json_data.get('amazing_facts', []))
        
        # Get symptoms from various possible fields
        symptoms_to_expect = []
        if 'symptoms_to_expect' in json_data:
            symptoms_to_expect.extend(json_data['symptoms_to_expect'])
        elif 'what_baby_can_do' in json_data:
            symptoms_to_expect.extend(json_data['what_baby_can_do'])
        
        return BabyDevelopmentCreate(
            day_of_pregnancy=day_of_pregnancy,
            baby_size_comparison=baby_size_comparison,
            title=json_data.get('title', f'Development Day {day_of_pregnancy}'),
            brief_description=json_data.get('subtitle', json_data.get('family_sharing_prompt', '')[:500]),
            detailed_description=json_data.get('family_sharing_prompt', ''),
            development_highlights=development_highlights,
            symptoms_to_expect=symptoms_to_expect,
            medical_milestones=json_data.get('medical_accuracy_notes', '').split(';') if json_data.get('medical_accuracy_notes') else [],
            mother_changes=json_data.get('mother_changes', 'Various changes may be occurring in your body at this stage.'),
            tips_and_advice='\n'.join(json_data.get('connection_activities', [])),
            emotional_notes=json_data.get('emotional_tone', ''),
            partner_tips='Support and encourage during this special time.',
            fun_fact='\n'.join(json_data.get('amazing_facts', [])),
            content_version="1.0"
        )