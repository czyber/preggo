"""
Memory book API endpoints for the Preggo app overhaul.
Handles automatic memory curation and family collaboration.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.database import get_session
from app.services.memory_book_service import memory_book_service
from app.models.enhanced_content import MemoryType, MemoryBookItem, MemoryCollection
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory-book", tags=["memory_book"])


# Request/Response Models
class CreateMemoryRequest(BaseModel):
    """Request model for creating a manual memory"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    memory_type: MemoryType
    memory_date: datetime
    content: Optional[Dict[str, Any]] = Field(default_factory=dict)
    media_items: Optional[List[str]] = Field(default_factory=list)
    pregnancy_week: Optional[int] = Field(None, ge=1, le=42)
    tags: Optional[List[str]] = Field(default_factory=list)
    is_private: bool = Field(False)


class AddFamilyContributionRequest(BaseModel):
    """Request model for adding family contribution to memory"""
    contribution_type: str = Field(..., description="Type: comment, photo, story, reaction, well_wish")
    content: str = Field(..., min_length=1)
    relationship_to_pregnant_person: str
    media_items: Optional[List[str]] = Field(default_factory=list)


class AutoCuratePostRequest(BaseModel):
    """Request model for auto-curating a post as memory"""
    post_id: str


class MemoryResponse(BaseModel):
    """Response model for memory items"""
    id: str
    title: str
    description: str
    memory_type: str
    pregnancy_week: Optional[int]
    memory_date: str
    content: Dict[str, Any]
    media_items: List[str]
    tags: List[str]
    is_favorite: bool
    is_private: bool
    auto_generated: bool
    curation_score: float
    collaborative: bool
    family_contributions_count: int
    family_contributions: List[Dict[str, Any]]
    created_at: str
    updated_at: str


class MemoryCollectionResponse(BaseModel):
    """Response model for memory collections"""
    id: str
    title: str
    description: Optional[str]
    collection_type: str
    start_week: Optional[int]
    end_week: Optional[int]
    memory_count: int
    memory_items: List[Dict[str, Any]]
    is_shared: bool
    auto_generated: bool
    created_at: str
    updated_at: str


class MemorySuggestionResponse(BaseModel):
    """Response model for memory suggestions"""
    suggestions: List[Dict[str, Any]]
    week_number: int
    total_suggestions: int
    high_quality_suggestions: int


# API Endpoints

@router.get("/pregnancy/{pregnancy_id}")
async def get_memory_book(
    pregnancy_id: str,
    limit: Optional[int] = Query(None, ge=1, le=100, description="Number of memories to return"),
    memory_type: Optional[MemoryType] = Query(None, description="Filter by memory type"),
    session: Session = Depends(get_session)
):
    """
    Get all memories for a pregnancy, with optional filtering and limiting.
    """
    try:
        memories = memory_book_service.get_memory_book_for_pregnancy(
            session, pregnancy_id, limit, memory_type
        )
        
        return {
            "pregnancy_id": pregnancy_id,
            "memories": memories,
            "total_count": len(memories),
            "filtered_by_type": memory_type.value if memory_type else None
        }
        
    except Exception as e:
        logger.error(f"Error getting memory book: {e}")
        raise HTTPException(status_code=500, detail="Failed to get memory book")


@router.post("/memories")
async def create_manual_memory(
    memory_request: CreateMemoryRequest,
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    user_id: str = Query(..., description="User ID"),
    session: Session = Depends(get_session)
):
    """
    Create a manual memory item.
    """
    try:
        memory_item = memory_book_service.create_manual_memory(
            session=session,
            pregnancy_id=pregnancy_id,
            user_id=user_id,
            title=memory_request.title,
            description=memory_request.description,
            memory_type=memory_request.memory_type,
            memory_date=memory_request.memory_date,
            content=memory_request.content,
            media_items=memory_request.media_items,
            pregnancy_week=memory_request.pregnancy_week
        )
        
        if not memory_item:
            raise HTTPException(status_code=400, detail="Failed to create memory")
        
        return {
            "success": True,
            "memory_id": memory_item.id,
            "message": "Memory created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating manual memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to create memory")


@router.post("/auto-curate")
async def auto_curate_post_memory(
    curate_request: AutoCuratePostRequest,
    user_id: str = Query(..., description="User ID"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session)
):
    """
    Automatically curate a post as a memory if it meets criteria.
    """
    try:
        memory_item = memory_book_service.auto_curate_post_memory(
            session, curate_request.post_id, user_id
        )
        
        if not memory_item:
            return {
                "success": False,
                "message": "Post did not meet criteria for automatic curation",
                "suggestion": "You can manually add this post to your memory book if it's special to you"
            }
        
        return {
            "success": True,
            "memory_id": memory_item.id,
            "memory_type": memory_item.memory_type.value,
            "curation_score": memory_item.curation_score,
            "curation_reasons": memory_item.curation_reasons,
            "message": "Post automatically curated as memory"
        }
        
    except Exception as e:
        logger.error(f"Error auto-curating post memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to curate memory")


@router.post("/memories/{memory_id}/contributions")
async def add_family_contribution(
    memory_id: str,
    contribution_request: AddFamilyContributionRequest,
    user_id: str = Query(..., description="Contributor user ID"),
    session: Session = Depends(get_session)
):
    """
    Add a family member's contribution to a memory.
    """
    try:
        contribution = memory_book_service.add_family_contribution(
            session=session,
            memory_item_id=memory_id,
            contributor_user_id=user_id,
            contribution_type=contribution_request.contribution_type,
            content=contribution_request.content,
            relationship=contribution_request.relationship_to_pregnant_person,
            media_items=contribution_request.media_items
        )
        
        if not contribution:
            raise HTTPException(status_code=400, detail="Failed to add family contribution")
        
        return {
            "success": True,
            "contribution_id": contribution.id,
            "message": "Family contribution added successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding family contribution: {e}")
        raise HTTPException(status_code=500, detail="Failed to add contribution")


@router.get("/memories/{memory_id}")
async def get_memory_details(
    memory_id: str,
    session: Session = Depends(get_session)
):
    """
    Get detailed information about a specific memory, including all family contributions.
    """
    try:
        from sqlmodel import select
        from app.models.enhanced_content import FamilyMemoryContribution
        from app.models.user import User
        
        # Get memory item
        memory_item = session.get(MemoryBookItem, memory_id)
        if not memory_item:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Get family contributions with user details
        contribution_query = select(FamilyMemoryContribution, User).join(
            User, FamilyMemoryContribution.contributor_user_id == User.id
        ).where(FamilyMemoryContribution.memory_item_id == memory_id)
        
        contribution_results = session.exec(contribution_query).all()
        
        # Format contributions
        contributions = []
        for contrib, user in contribution_results:
            contributions.append({
                "id": contrib.id,
                "contributor_name": f"{user.first_name} {user.last_name}",
                "contributor_user_id": contrib.contributor_user_id,
                "contribution_type": contrib.contribution_type,
                "content": contrib.content,
                "relationship": contrib.relationship_to_pregnant_person,
                "media_items": contrib.media_items,
                "created_at": contrib.created_at.isoformat()
            })
        
        return {
            "id": memory_item.id,
            "title": memory_item.title,
            "description": memory_item.description,
            "memory_type": memory_item.memory_type.value,
            "pregnancy_week": memory_item.pregnancy_week,
            "memory_date": memory_item.memory_date.isoformat(),
            "content": memory_item.content,
            "media_items": memory_item.media_items,
            "tags": memory_item.tags,
            "is_favorite": memory_item.is_favorite,
            "is_private": memory_item.is_private,
            "auto_generated": memory_item.auto_generated,
            "curation_score": memory_item.curation_score,
            "curation_reasons": memory_item.curation_reasons,
            "collaborative": memory_item.collaborative,
            "family_contributions": contributions,
            "family_contributions_count": len(contributions),
            "created_at": memory_item.created_at.isoformat(),
            "updated_at": memory_item.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get memory details")


@router.put("/memories/{memory_id}")
async def update_memory(
    memory_id: str,
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    is_favorite: Optional[bool] = Query(None),
    is_private: Optional[bool] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Update memory details.
    """
    try:
        memory_item = session.get(MemoryBookItem, memory_id)
        if not memory_item:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Update fields if provided
        if title is not None:
            memory_item.title = title
        if description is not None:
            memory_item.description = description
        if tags is not None:
            memory_item.tags = tags
        if is_favorite is not None:
            memory_item.is_favorite = is_favorite
        if is_private is not None:
            memory_item.is_private = is_private
        
        memory_item.updated_at = datetime.utcnow()
        
        session.add(memory_item)
        session.commit()
        
        return {
            "success": True,
            "message": "Memory updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to update memory")


@router.get("/collections/{pregnancy_id}")
async def get_memory_collections(
    pregnancy_id: str,
    collection_type: Optional[str] = Query(None, description="Filter by collection type"),
    session: Session = Depends(get_session)
):
    """
    Get memory collections for a pregnancy.
    """
    try:
        collections = memory_book_service.get_memory_collections(
            session, pregnancy_id, collection_type
        )
        
        return {
            "pregnancy_id": pregnancy_id,
            "collections": collections,
            "total_count": len(collections),
            "filtered_by_type": collection_type
        }
        
    except Exception as e:
        logger.error(f"Error getting memory collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get collections")


@router.post("/collections/generate-weekly")
async def generate_weekly_collections(
    pregnancy_id: str = Query(..., description="Pregnancy ID"),
    start_week: int = Query(1, ge=1, le=42),
    end_week: int = Query(42, ge=1, le=42),
    session: Session = Depends(get_session)
):
    """
    Generate weekly memory collections for a pregnancy.
    This creates automatic collections of significant moments for each week.
    """
    try:
        if start_week > end_week:
            raise HTTPException(status_code=400, detail="Start week must be less than or equal to end week")
        
        collections = memory_book_service.generate_weekly_memory_collections(
            session, pregnancy_id, start_week, end_week
        )
        
        return {
            "success": True,
            "collections_created": len(collections),
            "week_range": f"{start_week}-{end_week}",
            "collection_ids": [col.id for col in collections],
            "message": f"Generated {len(collections)} weekly memory collections"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating weekly collections: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate collections")


@router.get("/suggestions/{pregnancy_id}/{week_number}")
async def get_memory_suggestions(
    pregnancy_id: str,
    week_number: int = Field(..., ge=1, le=42),
    session: Session = Depends(get_session)
):
    """
    Get memory curation suggestions for a specific week.
    Shows posts and moments that could be added to the memory book.
    """
    try:
        from app.services.memory_book_service import MemoryCurationEngine
        
        engine = MemoryCurationEngine(session)
        suggestions = engine.suggest_weekly_memories(pregnancy_id, week_number)
        
        high_quality_suggestions = [s for s in suggestions if s['curation_score'] >= 0.7]
        
        return {
            "week_number": week_number,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "high_quality_suggestions": len(high_quality_suggestions),
            "curation_threshold": 0.6,
            "message": f"Found {len(suggestions)} potential memories for week {week_number}"
        }
        
    except Exception as e:
        logger.error(f"Error getting memory suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get suggestions")


@router.get("/stats/{pregnancy_id}")
async def get_memory_book_stats(
    pregnancy_id: str,
    session: Session = Depends(get_session)
):
    """
    Get statistics about the memory book for a pregnancy.
    """
    try:
        from sqlmodel import select, func
        from app.models.enhanced_content import FamilyMemoryContribution
        
        # Get total memories count
        memory_count_query = select(func.count(MemoryBookItem.id)).where(
            MemoryBookItem.pregnancy_id == pregnancy_id
        )
        total_memories = session.exec(memory_count_query).one()
        
        # Get memories by type
        type_count_query = select(
            MemoryBookItem.memory_type,
            func.count(MemoryBookItem.id).label("count")
        ).where(
            MemoryBookItem.pregnancy_id == pregnancy_id
        ).group_by(MemoryBookItem.memory_type)
        
        type_counts = session.exec(type_count_query).all()
        
        # Get auto vs manual memories
        from sqlmodel import and_
        auto_count_query = select(func.count(MemoryBookItem.id)).where(
            and_(
                MemoryBookItem.pregnancy_id == pregnancy_id,
                MemoryBookItem.auto_generated == True
            )
        )
        auto_memories = session.exec(auto_count_query).one()
        
        # Get total family contributions
        contribution_count_query = select(func.count(FamilyMemoryContribution.id)).join(
            MemoryBookItem, FamilyMemoryContribution.memory_item_id == MemoryBookItem.id
        ).where(MemoryBookItem.pregnancy_id == pregnancy_id)
        
        total_contributions = session.exec(contribution_count_query).one()
        
        # Get favorite memories count
        favorite_count_query = select(func.count(MemoryBookItem.id)).where(
            and_(
                MemoryBookItem.pregnancy_id == pregnancy_id,
                MemoryBookItem.is_favorite == True
            )
        )
        favorite_memories = session.exec(favorite_count_query).one()
        
        # Get memory collections count
        collection_count_query = select(func.count(MemoryCollection.id)).where(
            MemoryCollection.pregnancy_id == pregnancy_id
        )
        total_collections = session.exec(collection_count_query).one()
        
        return {
            "pregnancy_id": pregnancy_id,
            "total_memories": total_memories,
            "auto_curated_memories": auto_memories,
            "manually_created_memories": total_memories - auto_memories,
            "favorite_memories": favorite_memories,
            "total_family_contributions": total_contributions,
            "total_collections": total_collections,
            "memories_by_type": [
                {"type": result.memory_type.value, "count": result.count}
                for result in type_counts
            ],
            "completion_rate": f"{min(total_memories / 42 * 100, 100):.1f}%",  # Assuming 1 memory per week ideally
            "family_engagement_score": min(total_contributions / max(total_memories, 1) * 100, 100)
        }
        
    except Exception as e:
        logger.error(f"Error getting memory book stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get stats")


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: str,
    session: Session = Depends(get_session)
):
    """
    Delete a memory item and all its contributions.
    """
    try:
        from sqlmodel import delete
        from app.models.enhanced_content import FamilyMemoryContribution
        
        # Get memory item to verify it exists
        memory_item = session.get(MemoryBookItem, memory_id)
        if not memory_item:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        # Delete family contributions first (due to foreign key constraint)
        delete_contributions = delete(FamilyMemoryContribution).where(
            FamilyMemoryContribution.memory_item_id == memory_id
        )
        session.exec(delete_contributions)
        
        # Delete memory item
        session.delete(memory_item)
        session.commit()
        
        return {
            "success": True,
            "message": "Memory deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete memory")