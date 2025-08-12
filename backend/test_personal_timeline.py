#!/usr/bin/env python3
import asyncio
from app.db.session import get_session
from app.services.feed_service import feed_service
from app.schemas.feed import FeedRequest, FeedFilterType, FeedSortType

async def test_personal_timeline():
    session = next(get_session())
    
    user_id = "13740f63-337a-4876-82c4-0c15bd1f8f70"
    pregnancy_id = "7d9560ae-4de6-4942-b1d8-55f6e99963f0"
    
    feed_request = FeedRequest(
        limit=20,
        cursor=None,
        offset=0,
        filter_type=FeedFilterType.ALL,
        sort_by=FeedSortType.CHRONOLOGICAL,
        include_reactions=True,
        include_comments=True,
        include_media=True
    )
    
    try:
        print("Testing get_personal_timeline...")
        timeline_response = await feed_service.get_personal_timeline(
            session, user_id, pregnancy_id, feed_request
        )
        
        print(f"Posts returned: {len(timeline_response.posts)}")
        print(f"Total count: {timeline_response.total_count}")
        print(f"Has more: {timeline_response.has_more}")
        print(f"Milestones coming up: {len(timeline_response.milestones_coming_up)}")
        
        if timeline_response.posts:
            for i, post in enumerate(timeline_response.posts):
                print(f"  Post {i+1}: {post.id[:8]}... | Type: {post.type}")
        
    except Exception as e:
        print(f"Error in test: {e}")
        import traceback
        traceback.print_exc()
    
    session.close()

if __name__ == "__main__":
    asyncio.run(test_personal_timeline())