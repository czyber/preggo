"""Enhance reactions and threading system

Revision ID: enhance_reactions_and_threading_system
Revises: implement_content_system_overhaul
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'enhance_reactions_and_threading_system'
down_revision = 'de59728f572f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Enhance reactions and comments system with:
    - Enhanced reaction types (9 pregnancy-specific reactions)
    - Reaction intensity levels (1-3)
    - Family warmth calculations
    - Threaded comments (up to 5 levels deep)
    - @mention system
    - Real-time typing indicators
    - Performance optimizations
    """
    
    # === ENHANCE REACTIONS TABLE ===
    
    # Add new columns for enhanced reactions
    op.add_column('reactions', sa.Column('intensity', sa.Integer(), nullable=False, server_default='2'))
    op.add_column('reactions', sa.Column('custom_message', sa.String(length=200), nullable=True))
    op.add_column('reactions', sa.Column('is_milestone_reaction', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('reactions', sa.Column('family_warmth_contribution', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('reactions', sa.Column('client_id', sa.String(length=255), nullable=True))
    
    # Add constraints for intensity
    op.create_check_constraint(
        'ck_reactions_intensity_range',
        'reactions',
        'intensity >= 1 AND intensity <= 3'
    )
    
    # Add constraints for family warmth contribution
    op.create_check_constraint(
        'ck_reactions_warmth_range',
        'reactions',
        'family_warmth_contribution >= 0.0 AND family_warmth_contribution <= 1.0'
    )
    
    # Add index for client_id (for deduplication)
    op.create_index('ix_reactions_client_id', 'reactions', ['client_id'])
    
    # Add index for milestone reactions
    op.create_index('ix_reactions_milestone', 'reactions', ['is_milestone_reaction'])
    
    # === ENHANCE COMMENTS TABLE ===
    
    # Add threading columns
    op.add_column('comments', sa.Column('thread_depth', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('comments', sa.Column('thread_path', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('comments', sa.Column('root_comment_id', sa.String(length=255), nullable=True))
    
    # Add mention system columns
    op.add_column('comments', sa.Column('mention_names', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add edit history column
    op.add_column('comments', sa.Column('edit_history', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add descendant count tracking
    op.add_column('comments', sa.Column('total_descendant_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Add real-time typing indicators
    op.add_column('comments', sa.Column('is_typing_reply', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('comments', sa.Column('last_typing_user', sa.String(length=255), nullable=True))
    op.add_column('comments', sa.Column('last_typing_at', sa.DateTime(), nullable=True))
    
    # Add reaction summary for performance
    op.add_column('comments', sa.Column('reaction_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add family warmth integration
    op.add_column('comments', sa.Column('family_warmth_contribution', sa.Float(), nullable=False, server_default='0.0'))
    
    # Update content length limit
    op.alter_column('comments', 'content', type_=sa.String(length=2000))
    
    # Add constraints for thread depth
    op.create_check_constraint(
        'ck_comments_thread_depth_range',
        'comments',
        'thread_depth >= 0 AND thread_depth <= 5'
    )
    
    # Add constraints for family warmth contribution
    op.create_check_constraint(
        'ck_comments_warmth_range',
        'comments',
        'family_warmth_contribution >= 0.0 AND family_warmth_contribution <= 1.0'
    )
    
    # Add foreign key constraint for root_comment_id
    op.create_foreign_key(
        'fk_comments_root_comment_id',
        'comments',
        'comments',
        ['root_comment_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add foreign key constraint for last_typing_user
    op.create_foreign_key(
        'fk_comments_last_typing_user',
        'comments',
        'users',
        ['last_typing_user'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add indexes for threading performance
    op.create_index('ix_comments_thread_depth', 'comments', ['thread_depth'])
    op.create_index('ix_comments_thread_path', 'comments', ['thread_path'])
    op.create_index('ix_comments_root_comment_id', 'comments', ['root_comment_id'])
    
    # Add indexes for typing indicators
    op.create_index('ix_comments_typing_reply', 'comments', ['is_typing_reply'])
    op.create_index('ix_comments_last_typing_at', 'comments', ['last_typing_at'])
    
    # Add composite index for parent/thread queries
    op.create_index('ix_comments_parent_thread', 'comments', ['parent_id', 'thread_path'])
    
    # === UPDATE POSTS TABLE FOR ENHANCED FEATURES ===
    
    # Ensure posts table has all enhanced fields (may already exist from content overhaul)
    try:
        op.add_column('posts', sa.Column('family_warmth_score', sa.Float(), nullable=False, server_default='0.0'))
    except:
        # Column already exists
        pass
    
    try:
        op.add_column('posts', sa.Column('reaction_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    except:
        # Column already exists
        pass
    
    try:
        op.add_column('posts', sa.Column('last_family_interaction', sa.DateTime(), nullable=True))
    except:
        # Column already exists
        pass
    
    # Add indexes for family warmth queries
    try:
        op.create_index('ix_posts_family_warmth_score', 'posts', ['family_warmth_score'])
    except:
        # Index already exists
        pass
    
    try:
        op.create_index('ix_posts_last_family_interaction', 'posts', ['last_family_interaction'])
    except:
        # Index already exists
        pass
    
    # === CREATE NEW INDEXES FOR PERFORMANCE ===
    
    # Optimize reaction queries
    op.create_index('ix_reactions_user_post', 'reactions', ['user_id', 'post_id'])
    op.create_index('ix_reactions_user_comment', 'reactions', ['user_id', 'comment_id'])
    op.create_index('ix_reactions_type_intensity', 'reactions', ['type', 'intensity'])
    op.create_index('ix_reactions_created_at_desc', 'reactions', [sa.text('created_at DESC')])
    
    # Optimize comment queries
    op.create_index('ix_comments_post_created', 'comments', ['post_id', sa.text('created_at ASC')])
    op.create_index('ix_comments_user_created', 'comments', ['user_id', sa.text('created_at DESC')])
    op.create_index('ix_comments_parent_created', 'comments', ['parent_id', sa.text('created_at ASC')])
    
    # === ADD TRIGGER FUNCTIONS FOR AUTOMATIC COUNTER UPDATES ===
    
    # Function to update post reaction count and family warmth
    op.execute("""
        CREATE OR REPLACE FUNCTION update_post_reaction_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                -- Update post reaction count and family warmth
                UPDATE posts 
                SET 
                    reaction_count = reaction_count + 1,
                    family_warmth_score = LEAST(
                        family_warmth_score + NEW.family_warmth_contribution,
                        1.0
                    ),
                    last_family_interaction = NEW.created_at
                WHERE id = NEW.post_id;
                
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                -- Update post reaction count and family warmth
                UPDATE posts 
                SET 
                    reaction_count = GREATEST(reaction_count - 1, 0),
                    family_warmth_score = GREATEST(
                        family_warmth_score - OLD.family_warmth_contribution,
                        0.0
                    )
                WHERE id = OLD.post_id;
                
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                -- Update family warmth difference
                UPDATE posts 
                SET 
                    family_warmth_score = GREATEST(
                        LEAST(
                            family_warmth_score - OLD.family_warmth_contribution + NEW.family_warmth_contribution,
                            1.0
                        ),
                        0.0
                    ),
                    last_family_interaction = NEW.created_at
                WHERE id = NEW.post_id;
                
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Function to update comment reaction count and family warmth
    op.execute("""
        CREATE OR REPLACE FUNCTION update_comment_reaction_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                UPDATE comments 
                SET 
                    reaction_count = reaction_count + 1,
                    family_warmth_contribution = LEAST(
                        family_warmth_contribution + NEW.family_warmth_contribution,
                        1.0
                    )
                WHERE id = NEW.comment_id;
                
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE comments 
                SET 
                    reaction_count = GREATEST(reaction_count - 1, 0),
                    family_warmth_contribution = GREATEST(
                        family_warmth_contribution - OLD.family_warmth_contribution,
                        0.0
                    )
                WHERE id = OLD.comment_id;
                
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                UPDATE comments 
                SET 
                    family_warmth_contribution = GREATEST(
                        LEAST(
                            family_warmth_contribution - OLD.family_warmth_contribution + NEW.family_warmth_contribution,
                            1.0
                        ),
                        0.0
                    )
                WHERE id = NEW.comment_id;
                
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Function to update comment reply counts
    op.execute("""
        CREATE OR REPLACE FUNCTION update_comment_reply_stats()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' AND NEW.parent_id IS NOT NULL THEN
                -- Update direct parent reply count
                UPDATE comments 
                SET reply_count = reply_count + 1
                WHERE id = NEW.parent_id;
                
                -- Update root comment descendant count
                IF NEW.root_comment_id IS NOT NULL THEN
                    UPDATE comments 
                    SET total_descendant_count = total_descendant_count + 1
                    WHERE id = NEW.root_comment_id;
                END IF;
                
                -- Update post comment count
                UPDATE posts 
                SET comment_count = comment_count + 1
                WHERE id = NEW.post_id;
                
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' AND OLD.parent_id IS NOT NULL THEN
                -- Update direct parent reply count
                UPDATE comments 
                SET reply_count = GREATEST(reply_count - 1, 0)
                WHERE id = OLD.parent_id;
                
                -- Update root comment descendant count
                IF OLD.root_comment_id IS NOT NULL THEN
                    UPDATE comments 
                    SET total_descendant_count = GREATEST(total_descendant_count - 1, 0)
                    WHERE id = OLD.root_comment_id;
                END IF;
                
                -- Update post comment count
                UPDATE posts 
                SET comment_count = GREATEST(comment_count - 1, 0)
                WHERE id = OLD.post_id;
                
                RETURN OLD;
            END IF;
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # === CREATE TRIGGERS ===
    
    # Trigger for post reaction statistics
    op.execute("""
        CREATE TRIGGER trigger_update_post_reaction_stats
            AFTER INSERT OR UPDATE OR DELETE ON reactions
            FOR EACH ROW
            WHEN (NEW.post_id IS NOT NULL OR OLD.post_id IS NOT NULL)
            EXECUTE FUNCTION update_post_reaction_stats();
    """)
    
    # Trigger for comment reaction statistics
    op.execute("""
        CREATE TRIGGER trigger_update_comment_reaction_stats
            AFTER INSERT OR UPDATE OR DELETE ON reactions
            FOR EACH ROW
            WHEN (NEW.comment_id IS NOT NULL OR OLD.comment_id IS NOT NULL)
            EXECUTE FUNCTION update_comment_reaction_stats();
    """)
    
    # Trigger for comment reply statistics
    op.execute("""
        CREATE TRIGGER trigger_update_comment_reply_stats
            AFTER INSERT OR DELETE ON comments
            FOR EACH ROW
            EXECUTE FUNCTION update_comment_reply_stats();
    """)
    
    # === UPDATE EXISTING DATA FOR NEW FEATURES ===
    
    # Set default thread paths for existing comments
    op.execute("""
        WITH numbered_comments AS (
            SELECT 
                id,
                post_id,
                parent_id,
                ROW_NUMBER() OVER (
                    PARTITION BY post_id, parent_id 
                    ORDER BY created_at ASC
                ) as comment_number
            FROM comments
            WHERE thread_path = '' OR thread_path IS NULL
        )
        UPDATE comments 
        SET 
            thread_path = CASE 
                WHEN parent_id IS NULL THEN numbered_comments.comment_number::text
                ELSE numbered_comments.comment_number::text
            END,
            thread_depth = CASE 
                WHEN parent_id IS NULL THEN 0
                ELSE 1
            END
        FROM numbered_comments
        WHERE comments.id = numbered_comments.id;
    """)
    
    # Update root_comment_id for depth-1 comments
    op.execute("""
        UPDATE comments 
        SET root_comment_id = parent_id
        WHERE thread_depth = 1 AND parent_id IS NOT NULL;
    """)
    
    # Calculate family warmth for existing reactions
    op.execute("""
        UPDATE reactions 
        SET 
            family_warmth_contribution = CASE 
                WHEN type = 'love' THEN 0.12
                WHEN type = 'excited' THEN 0.10
                WHEN type = 'supportive' OR type = 'care' THEN 0.15
                WHEN type = 'strong' OR type = 'support' THEN 0.13
                WHEN type = 'blessed' OR type = 'beautiful' THEN 0.11
                WHEN type = 'happy' OR type = 'funny' THEN 0.08
                WHEN type = 'grateful' OR type = 'praying' THEN 0.12
                WHEN type = 'celebrating' THEN 0.14
                WHEN type = 'amazed' THEN 0.09
                ELSE 0.05
            END * (intensity / 2.0)
        WHERE family_warmth_contribution = 0.0;
    """)
    
    # Update post family warmth scores from existing reactions
    op.execute("""
        WITH post_warmth AS (
            SELECT 
                post_id,
                SUM(family_warmth_contribution) as total_warmth
            FROM reactions
            WHERE post_id IS NOT NULL
            GROUP BY post_id
        )
        UPDATE posts 
        SET family_warmth_score = LEAST(post_warmth.total_warmth, 1.0)
        FROM post_warmth
        WHERE posts.id = post_warmth.post_id;
    """)
    
    print("Enhanced reactions and threading system migration completed successfully!")


def downgrade() -> None:
    """
    Reverse the enhancements to reactions and comments system.
    """
    
    # === DROP TRIGGERS ===
    op.execute("DROP TRIGGER IF EXISTS trigger_update_post_reaction_stats ON reactions;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_comment_reaction_stats ON reactions;")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_comment_reply_stats ON comments;")
    
    # === DROP TRIGGER FUNCTIONS ===
    op.execute("DROP FUNCTION IF EXISTS update_post_reaction_stats();")
    op.execute("DROP FUNCTION IF EXISTS update_comment_reaction_stats();")
    op.execute("DROP FUNCTION IF EXISTS update_comment_reply_stats();")
    
    # === DROP INDEXES ===
    
    # Reaction indexes
    op.drop_index('ix_reactions_client_id', table_name='reactions')
    op.drop_index('ix_reactions_milestone', table_name='reactions')
    op.drop_index('ix_reactions_user_post', table_name='reactions')
    op.drop_index('ix_reactions_user_comment', table_name='reactions')
    op.drop_index('ix_reactions_type_intensity', table_name='reactions')
    op.drop_index('ix_reactions_created_at_desc', table_name='reactions')
    
    # Comment indexes
    op.drop_index('ix_comments_thread_depth', table_name='comments')
    op.drop_index('ix_comments_thread_path', table_name='comments')
    op.drop_index('ix_comments_root_comment_id', table_name='comments')
    op.drop_index('ix_comments_typing_reply', table_name='comments')
    op.drop_index('ix_comments_last_typing_at', table_name='comments')
    op.drop_index('ix_comments_parent_thread', table_name='comments')
    op.drop_index('ix_comments_post_created', table_name='comments')
    op.drop_index('ix_comments_user_created', table_name='comments')
    op.drop_index('ix_comments_parent_created', table_name='comments')
    
    # === DROP FOREIGN KEY CONSTRAINTS ===
    op.drop_constraint('fk_comments_root_comment_id', 'comments', type_='foreignkey')
    op.drop_constraint('fk_comments_last_typing_user', 'comments', type_='foreignkey')
    
    # === DROP CHECK CONSTRAINTS ===
    op.drop_constraint('ck_reactions_intensity_range', 'reactions', type_='check')
    op.drop_constraint('ck_reactions_warmth_range', 'reactions', type_='check')
    op.drop_constraint('ck_comments_thread_depth_range', 'comments', type_='check')
    op.drop_constraint('ck_comments_warmth_range', 'comments', type_='check')
    
    # === REMOVE COLUMNS ===
    
    # Remove enhanced reaction columns
    op.drop_column('reactions', 'client_id')
    op.drop_column('reactions', 'family_warmth_contribution')
    op.drop_column('reactions', 'is_milestone_reaction')
    op.drop_column('reactions', 'custom_message')
    op.drop_column('reactions', 'intensity')
    
    # Remove enhanced comment columns
    op.drop_column('comments', 'family_warmth_contribution')
    op.drop_column('comments', 'reaction_summary')
    op.drop_column('comments', 'last_typing_at')
    op.drop_column('comments', 'last_typing_user')
    op.drop_column('comments', 'is_typing_reply')
    op.drop_column('comments', 'total_descendant_count')
    op.drop_column('comments', 'edit_history')
    op.drop_column('comments', 'mention_names')
    op.drop_column('comments', 'root_comment_id')
    op.drop_column('comments', 'thread_path')
    op.drop_column('comments', 'thread_depth')
    
    # Revert comment content length
    op.alter_column('comments', 'content', type_=sa.Text())
    
    print("Enhanced reactions and threading system rollback completed!")