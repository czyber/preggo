#!/usr/bin/env python3
from app.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    try:
        result = conn.execute(text('SELECT version_num FROM alembic_version'))
        version = result.scalar()
        print(f'Current version: {version if version else "No version"}')
    except Exception as e:
        print(f'Error: {e}')