#!/usr/bin/env python3
from app.db.session import get_session
from app.models.content import Post
from sqlmodel import select
import asyncio

async def test_query():
    session = next(get_session())
    
    user_id = "13740f63-337a-4876-82c4-0c15bd1f8f70"
    pregnancy_id = "7d9560ae-4de6-4942-b1d8-55f6e99963f0"
    
    # Test the exact query from get_user_posts
    statement = select(Post).where(
        Post.author_id == user_id
    )
    
    if pregnancy_id:
        statement = statement.where(Post.pregnancy_id == pregnancy_id)
    
    statement = statement.order_by(Post.created_at.desc())
    statement = statement.limit(20)
    
    print("Executing query:")
    print(statement)
    
    try:
        results = session.exec(statement).all()
        print(f"Found {len(results)} posts")
        
        for post in results:
            print(f"  ID: {post.id[:8]}... | Type: {post.type} | Status: {post.status} | Created: {post.created_at}")
    except Exception as e:
        print(f"Error: {e}")
    
    session.close()

if __name__ == "__main__":
    asyncio.run(test_query())