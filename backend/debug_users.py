#!/usr/bin/env python3
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        # Check posts and their authors
        result = conn.execute(text('''
            SELECT DISTINCT author_id, COUNT(*) as post_count
            FROM posts 
            WHERE pregnancy_id = '7d9560ae-4de6-4942-b1d8-55f6e99963f0'
            GROUP BY author_id
        '''))
        
        authors = result.fetchall()
        print(f"Authors for pregnancy 7d9560ae-4de6-4942-b1d8-55f6e99963f0:")
        
        for author in authors:
            print(f"  Author ID: {author[0]} | Posts: {author[1]}")
            
        # Check pregnancy ownership
        result2 = conn.execute(text('''
            SELECT user_id, status
            FROM pregnancies 
            WHERE id = '7d9560ae-4de6-4942-b1d8-55f6e99963f0'
        '''))
        
        pregnancy = result2.fetchone()
        if pregnancy:
            print(f"\nPregnancy owner: {pregnancy[0]} | Status: {pregnancy[1]}")
        else:
            print("\nPregnancy not found!")
            
    except Exception as e:
        print(f'Error: {e}')