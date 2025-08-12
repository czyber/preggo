"""Add missing Instagram feed columns

Revision ID: add_missing_instagram_columns
Revises: de59728f572f
Create Date: 2025-01-12 09:21:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_missing_instagram_columns'
down_revision = 'de59728f572f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing Instagram-like feed columns."""
    
    # Add missing columns to posts table
    op.add_column('posts', sa.Column('reaction_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'))
    op.add_column('posts', sa.Column('last_family_interaction', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('trending_score', sa.Float(), nullable=False, server_default='0.0'))
    
    # Add missing columns to reactions table
    op.add_column('reactions', sa.Column('intensity', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('reactions', sa.Column('custom_message', sa.String(length=500), nullable=True))
    op.add_column('reactions', sa.Column('is_milestone_reaction', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('reactions', sa.Column('family_warmth_contribution', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('reactions', sa.Column('client_id', sa.String(length=100), nullable=True))
    
    # Add missing columns to comments table (check which are missing)
    # parent_id already exists, but let's add the threading columns
    op.add_column('comments', sa.Column('thread_path', sa.String(length=500), nullable=True))
    op.add_column('comments', sa.Column('thread_depth', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('comments', sa.Column('edited_at', sa.DateTime(), nullable=True))
    op.add_column('comments', sa.Column('edit_history', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    """Remove Instagram-like feed columns."""
    
    # Drop columns from comments
    op.drop_column('comments', 'edit_history')
    op.drop_column('comments', 'edited_at')
    op.drop_column('comments', 'is_edited')
    op.drop_column('comments', 'thread_depth')
    op.drop_column('comments', 'thread_path')
    
    # Drop columns from reactions
    op.drop_column('reactions', 'client_id')
    op.drop_column('reactions', 'family_warmth_contribution')
    op.drop_column('reactions', 'is_milestone_reaction')
    op.drop_column('reactions', 'custom_message')
    op.drop_column('reactions', 'intensity')
    
    # Drop columns from posts
    op.drop_column('posts', 'trending_score')
    op.drop_column('posts', 'last_family_interaction')
    op.drop_column('posts', 'reaction_summary')