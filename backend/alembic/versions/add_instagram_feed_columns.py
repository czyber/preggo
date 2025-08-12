"""Add Instagram-like feed columns to posts table

Revision ID: add_instagram_feed_columns
Revises: de59728f572f
Create Date: 2025-01-12 09:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_instagram_feed_columns'
down_revision = 'de59728f572f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Instagram-like feed enhancement columns to posts table."""
    
    # Add new columns to posts table for Instagram-like features
    op.add_column('posts', sa.Column('family_warmth_score', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('posts', sa.Column('memory_book_eligible', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('posts', sa.Column('memory_book_priority', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('posts', sa.Column('celebration_trigger_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('posts', sa.Column('emotional_context', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('posts', sa.Column('reaction_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True, server_default='{}'))
    op.add_column('posts', sa.Column('last_family_interaction', sa.DateTime(), nullable=True))
    op.add_column('posts', sa.Column('trending_score', sa.Float(), nullable=False, server_default='0.0'))
    
    # Add columns to reactions table for enhanced features
    op.add_column('reactions', sa.Column('intensity', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('reactions', sa.Column('custom_message', sa.String(length=500), nullable=True))
    op.add_column('reactions', sa.Column('is_milestone_reaction', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('reactions', sa.Column('family_warmth_contribution', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('reactions', sa.Column('client_id', sa.String(length=100), nullable=True))
    
    # Add columns to comments table for threading
    op.add_column('comments', sa.Column('parent_id', sa.String(), nullable=True))
    op.add_column('comments', sa.Column('thread_path', sa.String(length=500), nullable=True))
    op.add_column('comments', sa.Column('thread_depth', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('mentions', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('comments', sa.Column('is_edited', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('comments', sa.Column('edited_at', sa.DateTime(), nullable=True))
    op.add_column('comments', sa.Column('edit_history', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Create FeedActivity table for real-time tracking
    op.create_table('feed_activities',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('pregnancy_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.String(), nullable=False),
        sa.Column('activity_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('broadcast_to_family', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['pregnancy_id'], ['pregnancies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    
    # Create indexes for performance
    op.create_index('idx_posts_family_warmth_created', 'posts', ['family_warmth_score', 'created_at'], postgresql_using='btree')
    op.create_index('idx_posts_trending_score_created', 'posts', ['trending_score', 'created_at'], postgresql_using='btree')
    op.create_index('idx_reactions_intensity', 'reactions', ['intensity'], postgresql_using='btree')
    op.create_index('idx_reactions_client_dedup', 'reactions', ['post_id', 'user_id', 'client_id'], unique=True, postgresql_where=sa.text('client_id IS NOT NULL'))
    op.create_index('idx_comments_thread_path', 'comments', ['thread_path'], postgresql_using='btree')
    op.create_index('idx_comments_parent_id', 'comments', ['parent_id'], postgresql_using='btree')
    op.create_index('idx_feed_activities_pregnancy_created', 'feed_activities', ['pregnancy_id', 'created_at'], postgresql_using='btree')
    
    # Add check constraints
    op.create_check_constraint('ck_reactions_intensity_range', 'reactions', 'intensity >= 1 AND intensity <= 3')
    op.create_check_constraint('ck_posts_family_warmth_range', 'posts', 'family_warmth_score >= 0.0 AND family_warmth_score <= 1.0')
    op.create_check_constraint('ck_posts_memory_priority_range', 'posts', 'memory_book_priority >= 0.0 AND memory_book_priority <= 1.0')
    op.create_check_constraint('ck_comments_thread_depth_range', 'comments', 'thread_depth >= 0 AND thread_depth <= 5')


def downgrade() -> None:
    """Remove Instagram-like feed enhancement columns."""
    
    # Drop constraints
    op.drop_constraint('ck_comments_thread_depth_range', 'comments', type_='check')
    op.drop_constraint('ck_posts_memory_priority_range', 'posts', type_='check')
    op.drop_constraint('ck_posts_family_warmth_range', 'posts', type_='check')
    op.drop_constraint('ck_reactions_intensity_range', 'reactions', type_='check')
    
    # Drop indexes
    op.drop_index('idx_feed_activities_pregnancy_created', table_name='feed_activities')
    op.drop_index('idx_comments_parent_id', table_name='comments')
    op.drop_index('idx_comments_thread_path', table_name='comments')
    op.drop_index('idx_reactions_client_dedup', table_name='reactions')
    op.drop_index('idx_reactions_intensity', table_name='reactions')
    op.drop_index('idx_posts_trending_score_created', table_name='posts')
    op.drop_index('idx_posts_family_warmth_created', table_name='posts')
    
    # Drop feed_activities table
    op.drop_table('feed_activities')
    
    # Drop columns from comments
    op.drop_column('comments', 'edit_history')
    op.drop_column('comments', 'edited_at')
    op.drop_column('comments', 'is_edited')
    op.drop_column('comments', 'mentions')
    op.drop_column('comments', 'thread_depth')
    op.drop_column('comments', 'thread_path')
    op.drop_column('comments', 'parent_id')
    
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
    op.drop_column('posts', 'emotional_context')
    op.drop_column('posts', 'celebration_trigger_data')
    op.drop_column('posts', 'memory_book_priority')
    op.drop_column('posts', 'memory_book_eligible')
    op.drop_column('posts', 'family_warmth_score')