"""implement Instagram-like feed overhaul with performance enhancements

Revision ID: instagram_feed_overhaul
Revises: latest_revision
Create Date: 2025-01-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'instagram_feed_overhaul'
down_revision = None  # Will be updated automatically
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Implement Instagram-like feed enhancements."""
    
    # Add new columns to reactions table for Instagram-like features
    op.add_column('reactions', sa.Column('intensity', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('reactions', sa.Column('custom_message', sa.String(length=200), nullable=True))
    op.add_column('reactions', sa.Column('is_milestone_reaction', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('reactions', sa.Column('family_warmth_contribution', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('reactions', sa.Column('client_id', sa.String(), nullable=True))
    
    # Add new columns to posts table for enhanced feed features
    op.add_column('posts', sa.Column('reaction_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('posts', sa.Column('last_family_interaction', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('trending_score', sa.Float(), nullable=False, server_default='0.0'))
    
    # Create new feed_activities table for real-time activity tracking
    op.create_table('feed_activities',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pregnancy_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('activity_type', sa.String(), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('activity_data', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('broadcast_to_family', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('broadcast_priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('client_timestamp', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['pregnancy_id'], ['pregnancies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add check constraints for data integrity
    op.create_check_constraint(
        'ck_reactions_intensity_valid', 
        'reactions', 
        'intensity >= 1 AND intensity <= 3'
    )
    op.create_check_constraint(
        'ck_reactions_family_warmth_valid', 
        'reactions', 
        'family_warmth_contribution >= 0.0 AND family_warmth_contribution <= 1.0'
    )
    op.create_check_constraint(
        'ck_posts_trending_score_valid', 
        'posts', 
        'trending_score >= 0.0 AND trending_score <= 1.0'
    )
    op.create_check_constraint(
        'ck_feed_activities_priority_valid', 
        'feed_activities', 
        'broadcast_priority >= 1 AND broadcast_priority <= 5'
    )
    
    # Create strategic performance indexes based on design document
    
    # Feed query optimization - primary feed loading index
    op.create_index(
        'idx_posts_pregnancy_created_published',
        'posts',
        ['pregnancy_id', 'created_at', 'status'],
        postgresql_where=sa.text("status = 'published'"),
        postgresql_concurrently=True
    )
    
    # Trending posts optimization
    op.create_index(
        'idx_posts_trending_score_created',
        'posts',
        ['trending_score', 'created_at'],
        postgresql_where=sa.text("trending_score > 0.0"),
        postgresql_concurrently=True
    )
    
    # Family warmth optimization
    op.create_index(
        'idx_posts_family_warmth_created',
        'posts',
        ['family_warmth_score', 'created_at'],
        postgresql_where=sa.text("family_warmth_score > 0.3"),
        postgresql_concurrently=True
    )
    
    # Reaction aggregation optimization
    op.create_index(
        'idx_reactions_post_type_created',
        'reactions',
        ['post_id', 'type', 'created_at']
    )
    
    # Real-time activity query optimization
    op.create_index(
        'idx_feed_activities_pregnancy_created',
        'feed_activities',
        ['pregnancy_id', 'created_at']
    )
    
    # Activity broadcasting optimization
    op.create_index(
        'idx_feed_activities_broadcast_priority',
        'feed_activities',
        ['broadcast_priority', 'created_at'],
        postgresql_where=sa.text("broadcast_to_family = true AND processed_at IS NULL")
    )
    
    # Comment threading optimization
    op.create_index(
        'idx_comments_post_parent_created',
        'comments',
        ['post_id', 'parent_id', 'created_at']
    )
    
    # Memory book priority optimization
    op.create_index(
        'idx_posts_memory_priority',
        'posts',
        ['memory_book_priority', 'created_at'],
        postgresql_where=sa.text("memory_book_eligible = true")
    )
    
    # User reaction lookup optimization
    op.create_index(
        'idx_reactions_user_post_unique',
        'reactions',
        ['user_id', 'post_id'],
        unique=True,
        postgresql_where=sa.text("post_id IS NOT NULL")
    )
    
    # Client-side deduplication for optimistic updates
    op.create_index(
        'idx_reactions_client_dedup',
        'reactions',
        ['client_id', 'created_at'],
        postgresql_where=sa.text("client_id IS NOT NULL")
    )


def downgrade() -> None:
    """Rollback Instagram-like feed enhancements."""
    
    # Drop indexes (most recent first)
    op.drop_index('idx_reactions_client_dedup', table_name='reactions')
    op.drop_index('idx_reactions_user_post_unique', table_name='reactions')
    op.drop_index('idx_posts_memory_priority', table_name='posts')
    op.drop_index('idx_comments_post_parent_created', table_name='comments')
    op.drop_index('idx_feed_activities_broadcast_priority', table_name='feed_activities')
    op.drop_index('idx_feed_activities_pregnancy_created', table_name='feed_activities')
    op.drop_index('idx_reactions_post_type_created', table_name='reactions')
    op.drop_index('idx_posts_family_warmth_created', table_name='posts')
    op.drop_index('idx_posts_trending_score_created', table_name='posts')
    op.drop_index('idx_posts_pregnancy_created_published', table_name='posts')
    
    # Drop check constraints
    op.drop_constraint('ck_feed_activities_priority_valid', 'feed_activities', type_='check')
    op.drop_constraint('ck_posts_trending_score_valid', 'posts', type_='check')
    op.drop_constraint('ck_reactions_family_warmth_valid', 'reactions', type_='check')
    op.drop_constraint('ck_reactions_intensity_valid', 'reactions', type_='check')
    
    # Drop feed_activities table
    op.drop_table('feed_activities')
    
    # Remove added columns from posts
    op.drop_column('posts', 'trending_score')
    op.drop_column('posts', 'last_family_interaction')
    op.drop_column('posts', 'reaction_summary')
    
    # Remove added columns from reactions
    op.drop_column('reactions', 'client_id')
    op.drop_column('reactions', 'family_warmth_contribution')
    op.drop_column('reactions', 'is_milestone_reaction')
    op.drop_column('reactions', 'custom_message')
    op.drop_column('reactions', 'intensity')