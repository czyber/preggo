"""optimize feed performance indexes

Revision ID: optimize_feed_perf
Revises: [previous_revision]
Create Date: 2025-01-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'optimize_feed_perf'
down_revision = '44fe28c51a8d'  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for feed queries."""
    
    # Index on posts for pregnancy feed queries
    op.create_index(
        'idx_posts_pregnancy_status_created',
        'posts',
        ['pregnancy_id', 'status', 'created_at']
    )
    
    # Index on posts for type filtering
    op.create_index(
        'idx_posts_type_created',
        'posts',
        ['type', 'created_at']
    )
    
    # Index on reactions for post aggregation
    op.create_index(
        'idx_reactions_post_user',
        'reactions',
        ['post_id', 'user_id'],
    )
    
    # Index on comments for post aggregation
    op.create_index(
        'idx_comments_post_created',
        'comments',
        ['post_id', 'created_at'],
    )

    # Index on family_members for access control
    op.create_index(
        'idx_family_members_pregnancy_user',
        'family_members',
        ['pregnancy_id', 'user_id', 'status']
    )
    
    # Composite index for trending posts
    op.create_index(
        'idx_posts_trending',
        'posts',
        ['pregnancy_id', 'created_at', 'reaction_count', 'comment_count'],
    )


def downgrade():
    """Remove performance indexes."""
    
    op.drop_index('idx_posts_trending')
    op.drop_index('idx_family_members_pregnancy_user')
    op.drop_index('idx_comments_post_created')
    op.drop_index('idx_reactions_post_user')
    op.drop_index('idx_posts_type_created')
    op.drop_index('idx_posts_pregnancy_status_created')
