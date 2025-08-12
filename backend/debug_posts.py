#!/usr/bin/env python3
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        # Check if there are any posts for this pregnancy
        result = conn.execute(text('''
            SELECT 
                id, author_id, pregnancy_id, type, status, created_at
            FROM posts 
            WHERE pregnancy_id = '7d9560ae-4de6-4942-b1d8-55f6e99963f0'
            ORDER BY created_at DESC
        '''))
        
        posts = result.fetchall()
        print(f"Found {len(posts)} posts for pregnancy 7d9560ae-4de6-4942-b1d8-55f6e99963f0:")
        
        for post in posts:
            print(f"  ID: {post[0][:8]}... | Author: {post[1][:8]}... | Type: {post[3]} | Status: {post[4]} | Created: {post[5]}")
        
        if len(posts) == 0:
            # Check if there are any posts at all
            result2 = conn.execute(text('SELECT COUNT(*) FROM posts'))
            total_posts = result2.scalar()
            print(f"\nTotal posts in database: {total_posts}")
            
            # Check all pregnancies
            result3 = conn.execute(text('SELECT DISTINCT pregnancy_id FROM posts LIMIT 5'))
            pregnancy_ids = result3.fetchall()
            print("Sample pregnancy IDs in posts:", [p[0][:8] + "..." for p in pregnancy_ids])
            
    except Exception as e:
        print(f'Error: {e}')