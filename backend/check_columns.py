#!/usr/bin/env python3
"""Check which columns exist in the database tables."""

from app.db.session import engine
from sqlalchemy import text, inspect

def check_table_columns():
    inspector = inspect(engine)
    
    # Check posts table
    print("=== POSTS TABLE COLUMNS ===")
    posts_columns = inspector.get_columns('posts')
    for col in posts_columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Check reactions table
    print("\n=== REACTIONS TABLE COLUMNS ===")
    reactions_columns = inspector.get_columns('reactions')
    for col in reactions_columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Check comments table
    print("\n=== COMMENTS TABLE COLUMNS ===")
    comments_columns = inspector.get_columns('comments')
    for col in comments_columns:
        print(f"  - {col['name']}: {col['type']}")
    
    # Check if feed_activities table exists
    print("\n=== CHECKING FEED_ACTIVITIES TABLE ===")
    if 'feed_activities' in inspector.get_table_names():
        print("feed_activities table EXISTS")
        activities_columns = inspector.get_columns('feed_activities')
        for col in activities_columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("feed_activities table DOES NOT EXIST")

if __name__ == "__main__":
    check_table_columns()