"""Add enhanced post columns for content integration

Revision ID: edca5632613b
Revises: content_overhaul_001
Create Date: 2025-08-07 15:54:01.747532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'edca5632613b'
down_revision: Union[str, None] = 'content_overhaul_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add enhanced columns to posts table for content integration
    op.add_column('posts', sa.Column('integrated_content_id', sa.String(), nullable=True))
    op.add_column('posts', sa.Column('family_warmth_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('posts', sa.Column('memory_book_eligible', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('posts', sa.Column('memory_book_priority', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('posts', sa.Column('celebration_trigger_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('posts', sa.Column('emotional_context', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(None, 'posts', 'pregnancy_content', ['integrated_content_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key constraints
    op.drop_constraint(None, 'posts', type_='foreignkey')
    
    # Remove enhanced columns from posts table
    op.drop_column('posts', 'emotional_context')
    op.drop_column('posts', 'celebration_trigger_data')
    op.drop_column('posts', 'memory_book_priority')
    op.drop_column('posts', 'memory_book_eligible')
    op.drop_column('posts', 'family_warmth_score')
    op.drop_column('posts', 'integrated_content_id')