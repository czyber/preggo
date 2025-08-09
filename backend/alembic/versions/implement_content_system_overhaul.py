"""Implement content system overhaul

Revision ID: content_overhaul_001
Revises: optimize_feed_performance
Create Date: 2025-01-07 15:30:00.000000

This migration implements the comprehensive content management system for the Preggo app overhaul:
- Pregnancy content system with personalization
- Baby development content with creative size comparisons
- Family warmth system (replacing engagement metrics)
- Memory book system for automatic curation
- Enhanced post models for pregnancy context integration

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "content_overhaul_001"
down_revision = "optimize_feed_perf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema for content system overhaul."""

    # =========================================================================
    # CONTENT CATEGORIES
    # =========================================================================
    op.create_table(
        "content_categories",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon_name", sa.String(length=50), nullable=True),
        sa.Column("color_hex", sa.String(length=7), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("parent_category_id", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["parent_category_id"], ["content_categories.id"]),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        "idx_content_categories_active", "content_categories", ["is_active"]
    )
    op.create_index("idx_content_categories_sort", "content_categories", ["sort_order"])

    # =========================================================================
    # PREGNANCY CONTENT SYSTEM
    # =========================================================================
    op.create_table(
        "pregnancy_content",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("category_id", sa.String(), nullable=True),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=True),
        sa.Column("trimester", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("subtitle", sa.String(length=300), nullable=True),
        sa.Column("content_body", sa.Text(), nullable=False),
        sa.Column("content_summary", sa.String(length=500), nullable=True),
        sa.Column("reading_time_minutes", sa.Integer(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("featured_image", sa.String(), nullable=True),
        sa.Column(
            "media_urls", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "external_links", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "personalization_rules",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "target_audience", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "medical_review_status",
            sa.String(),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("medical_reviewer_id", sa.String(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "delivery_methods",
            postgresql.JSONB(),
            nullable=False,
            server_default='["feed_integration"]',
        ),
        sa.Column("optimal_delivery_time", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("parent_content_id", sa.String(), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("helpful_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "not_helpful_count", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["category_id"], ["content_categories.id"]),
        sa.ForeignKeyConstraint(["medical_reviewer_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["parent_content_id"], ["pregnancy_content.id"]),
        sa.CheckConstraint(
            "week_number >= 1 AND week_number <= 42", name="check_week_range"
        ),
        sa.CheckConstraint(
            "trimester >= 1 AND trimester <= 3", name="check_trimester_range"
        ),
    )
    op.create_index("idx_pregnancy_content_active", "pregnancy_content", ["is_active"])
    op.create_index("idx_pregnancy_content_week", "pregnancy_content", ["week_number"])
    op.create_index("idx_pregnancy_content_type", "pregnancy_content", ["content_type"])
    op.create_index("idx_pregnancy_content_priority", "pregnancy_content", ["priority"])
    op.create_index(
        "idx_pregnancy_content_medical_status",
        "pregnancy_content",
        ["medical_review_status"],
    )

    # =========================================================================
    # BABY DEVELOPMENT CONTENT
    # =========================================================================
    op.create_table(
        "baby_development_content",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("length_mm", sa.Float(), nullable=True),
        sa.Column("weight_grams", sa.Float(), nullable=True),
        sa.Column("size_comparison", sa.String(), nullable=False),
        sa.Column("size_comparison_category", sa.String(), nullable=False),
        sa.Column(
            "alternative_comparisons",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "major_developments",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "sensory_developments",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "body_system_developments",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("amazing_fact", sa.Text(), nullable=False),
        sa.Column("connection_moment", sa.Text(), nullable=False),
        sa.Column("what_baby_can_do", sa.Text(), nullable=False),
        sa.Column(
            "bonding_activities",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "conversation_starters",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("illustration_url", sa.String(), nullable=True),
        sa.Column("size_comparison_image", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "week_number >= 1 AND week_number <= 42", name="check_dev_week_range"
        ),
    )
    op.create_unique_index(
        "idx_baby_dev_week", "baby_development_content", ["week_number"]
    )

    # =========================================================================
    # USER CONTENT PREFERENCES
    # =========================================================================
    op.create_table(
        "user_content_preferences",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("pregnancy_id", sa.String(), nullable=False),
        sa.Column(
            "content_frequency", sa.String(), nullable=False, server_default="daily"
        ),
        sa.Column(
            "preferred_delivery_time",
            sa.String(),
            nullable=False,
            server_default="09:00",
        ),
        sa.Column(
            "delivery_methods",
            postgresql.JSONB(),
            nullable=False,
            server_default='["feed_integration"]',
        ),
        sa.Column(
            "preferred_categories",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "blocked_categories",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "detail_level", sa.String(), nullable=False, server_default="standard"
        ),
        sa.Column("emotional_tone", sa.String(), nullable=False, server_default="warm"),
        sa.Column(
            "medical_info_level", sa.String(), nullable=False, server_default="balanced"
        ),
        sa.Column(
            "cultural_preferences",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "language_preference", sa.String(), nullable=False, server_default="en"
        ),
        sa.Column(
            "family_sharing_level",
            sa.String(),
            nullable=False,
            server_default="moderate",
        ),
        sa.Column(
            "partner_involvement_level",
            sa.String(),
            nullable=False,
            server_default="high",
        ),
        sa.Column(
            "interaction_patterns",
            postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["pregnancy_id"], ["pregnancies.id"]),
    )
    op.create_index(
        "idx_content_prefs_user_pregnancy",
        "user_content_preferences",
        ["user_id", "pregnancy_id"],
    )

    # =========================================================================
    # CONTENT DELIVERY LOG
    # =========================================================================
    op.create_table(
        "content_delivery_log",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("pregnancy_id", sa.String(), nullable=False),
        sa.Column("content_id", sa.String(), nullable=False),
        sa.Column("delivery_method", sa.String(), nullable=False),
        sa.Column(
            "delivery_context", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column(
            "delivered_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("first_viewed_at", sa.DateTime(), nullable=True),
        sa.Column("last_viewed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "total_view_time_seconds", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reaction", sa.String(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column(
            "shared_with_family", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "added_to_memory_book", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "triggered_follow_up", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["pregnancy_id"], ["pregnancies.id"]),
        sa.ForeignKeyConstraint(["content_id"], ["pregnancy_content.id"]),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )
    op.create_index("idx_content_delivery_user", "content_delivery_log", ["user_id"])
    op.create_index(
        "idx_content_delivery_content", "content_delivery_log", ["content_id"]
    )
    op.create_index(
        "idx_content_delivery_date", "content_delivery_log", ["delivered_at"]
    )

    # =========================================================================
    # FAMILY WARMTH SYSTEM
    # =========================================================================
    op.create_table(
        "family_interactions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("post_id", sa.String(), nullable=True),
        sa.Column("pregnancy_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("interaction_type", sa.String(), nullable=False),
        sa.Column("interaction_content", sa.Text(), nullable=False),
        sa.Column("emotional_sentiment", sa.String(), nullable=True),
        sa.Column("warmth_intensity", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("relationship_to_pregnant_person", sa.String(), nullable=False),
        sa.Column("family_group_level", sa.String(), nullable=False),
        sa.Column(
            "interaction_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["pregnancy_id"], ["pregnancies.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.CheckConstraint(
            "warmth_intensity >= 0.0 AND warmth_intensity <= 1.0",
            name="check_warmth_range",
        ),
    )
    op.create_index(
        "idx_family_interactions_pregnancy", "family_interactions", ["pregnancy_id"]
    )
    op.create_index("idx_family_interactions_post", "family_interactions", ["post_id"])
    op.create_index(
        "idx_family_interactions_date", "family_interactions", ["interaction_at"]
    )

    op.create_table(
        "family_warmth_calculations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("post_id", sa.String(), nullable=True),
        sa.Column("pregnancy_id", sa.String(), nullable=False),
        sa.Column(
            "warmth_scores", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column(
            "calculation_date",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "total_interactions", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "active_family_members", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "calculation_period_days", sa.Integer(), nullable=False, server_default="7"
        ),
        sa.Column(
            "warmth_insights", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["pregnancy_id"], ["pregnancies.id"]),
    )
    op.create_index(
        "idx_warmth_calc_pregnancy", "family_warmth_calculations", ["pregnancy_id"]
    )
    op.create_index(
        "idx_warmth_calc_date", "family_warmth_calculations", ["calculation_date"]
    )

    # =========================================================================
    # MEMORY BOOK SYSTEM
    # =========================================================================
    op.create_table(
        "memory_book_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("pregnancy_id", sa.String(), nullable=False),
        sa.Column("source_post_id", sa.String(), nullable=True),
        sa.Column("created_by_user_id", sa.String(), nullable=False),
        sa.Column("memory_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column(
            "media_items", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column("pregnancy_week", sa.Integer(), nullable=True),
        sa.Column("memory_date", sa.DateTime(), nullable=False),
        sa.Column(
            "family_contributions",
            postgresql.JSONB(),
            nullable=False,
            server_default="[]",
        ),
        sa.Column(
            "collaborative", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "auto_generated", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("curation_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column(
            "curation_reasons", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["pregnancy_id"], ["pregnancies.id"]),
        sa.ForeignKeyConstraint(["source_post_id"], ["posts.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.CheckConstraint(
            "pregnancy_week >= 1 AND pregnancy_week <= 42",
            name="check_memory_week_range",
        ),
        sa.CheckConstraint(
            "curation_score >= 0.0 AND curation_score <= 1.0",
            name="check_curation_score_range",
        ),
    )
    op.create_index("idx_memory_book_pregnancy", "memory_book_items", ["pregnancy_id"])
    op.create_index("idx_memory_book_week", "memory_book_items", ["pregnancy_week"])
    op.create_index("idx_memory_book_type", "memory_book_items", ["memory_type"])
    op.create_index("idx_memory_book_date", "memory_book_items", ["memory_date"])

    op.create_table(
        "memory_collections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("pregnancy_id", sa.String(), nullable=False),
        sa.Column("created_by_user_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collection_type", sa.String(), nullable=False),
        sa.Column(
            "memory_item_ids", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column("start_week", sa.Integer(), nullable=True),
        sa.Column("end_week", sa.Integer(), nullable=True),
        sa.Column("is_shared", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "shared_with", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column(
            "auto_generated", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("generation_schedule", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["pregnancy_id"], ["pregnancies.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.CheckConstraint(
            "start_week >= 1 AND start_week <= 42", name="check_collection_start_week"
        ),
        sa.CheckConstraint(
            "end_week >= 1 AND end_week <= 42", name="check_collection_end_week"
        ),
    )
    op.create_index(
        "idx_memory_collections_pregnancy", "memory_collections", ["pregnancy_id"]
    )
    op.create_index(
        "idx_memory_collections_type", "memory_collections", ["collection_type"]
    )

    op.create_table(
        "family_memory_contributions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("memory_item_id", sa.String(), nullable=False),
        sa.Column("contributor_user_id", sa.String(), nullable=False),
        sa.Column("contribution_type", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "media_items", postgresql.JSONB(), nullable=False, server_default="[]"
        ),
        sa.Column("relationship_to_pregnant_person", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["memory_item_id"], ["memory_book_items.id"]),
        sa.ForeignKeyConstraint(["contributor_user_id"], ["users.id"]),
    )
    op.create_index(
        "idx_memory_contributions_item",
        "family_memory_contributions",
        ["memory_item_id"],
    )
    op.create_index(
        "idx_memory_contributions_contributor",
        "family_memory_contributions",
        ["contributor_user_id"],
    )

    # =========================================================================
    # ENHANCE EXISTING POSTS TABLE
    # =========================================================================
    # Add new columns for pregnancy context integration
    op.add_column(
        "posts", sa.Column("integrated_content_id", sa.String(), nullable=True)
    )
    op.add_column(
        "posts",
        sa.Column(
            "family_warmth_score", sa.Float(), nullable=False, server_default="0.0"
        ),
    )
    op.add_column(
        "posts",
        sa.Column(
            "memory_book_eligible", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "posts",
        sa.Column(
            "memory_book_priority", sa.Float(), nullable=False, server_default="0.0"
        ),
    )
    op.add_column(
        "posts",
        sa.Column("celebration_trigger_data", postgresql.JSONB(), nullable=True),
    )
    op.add_column(
        "posts", sa.Column("emotional_context", postgresql.JSONB(), nullable=True)
    )

    # Add foreign key constraints
    op.create_foreign_key(
        "fk_posts_integrated_content",
        "posts",
        "pregnancy_content",
        ["integrated_content_id"],
        ["id"],
    )

    # Add check constraints
    op.create_check_constraint(
        "check_family_warmth_range",
        "posts",
        "family_warmth_score >= 0.0 AND family_warmth_score <= 1.0",
    )
    op.create_check_constraint(
        "check_memory_priority_range",
        "posts",
        "memory_book_priority >= 0.0 AND memory_book_priority <= 1.0",
    )

    # Add indexes for new columns
    op.create_index("idx_posts_warmth_score", "posts", ["family_warmth_score"])
    op.create_index("idx_posts_memory_eligible", "posts", ["memory_book_eligible"])
    op.create_index("idx_posts_integrated_content", "posts", ["integrated_content_id"])

    # =========================================================================
    # SEED INITIAL CONTENT CATEGORIES
    # =========================================================================
    # Insert initial content categories
    op.execute("""
        INSERT INTO content_categories (id, name, slug, description, icon_name, color_hex, sort_order, is_active) VALUES
        ('cat_weekly_tips', 'Weekly Tips', 'weekly-tips', 'Week-by-week pregnancy guidance', 'calendar', '#FF6B8A', 1, true),
        ('cat_baby_dev', 'Baby Development', 'baby-development', 'How your baby is growing', 'baby', '#FFB3C1', 2, true),
        ('cat_health', 'Health & Wellness', 'health-wellness', 'Physical and mental health guidance', 'heart', '#FF8FA3', 3, true),
        ('cat_emotional', 'Emotional Support', 'emotional-support', 'Feelings and emotional guidance', 'support', '#FFC6D2', 4, true),
        ('cat_preparation', 'Preparation', 'preparation', 'Getting ready for baby', 'checklist', '#FFCAD4', 5, true),
        ('cat_family', 'Family & Partner', 'family-partner', 'Involving your support network', 'family', '#FFD1DC', 6, true),
        ('cat_milestones', 'Milestones', 'milestones', 'Celebrating special moments', 'star', '#FFDBEA', 7, true)
    """)


def downgrade() -> None:
    """Downgrade database schema by removing content system overhaul."""

    # Remove indexes first
    op.drop_index("idx_posts_integrated_content", table_name="posts")
    op.drop_index("idx_posts_memory_eligible", table_name="posts")
    op.drop_index("idx_posts_warmth_score", table_name="posts")

    # Remove check constraints
    op.drop_constraint("check_memory_priority_range", "posts", type_="check")
    op.drop_constraint("check_family_warmth_range", "posts", type_="check")

    # Remove foreign key constraint
    op.drop_constraint("fk_posts_integrated_content", "posts", type_="foreignkey")

    # Remove enhanced post columns
    op.drop_column("posts", "emotional_context")
    op.drop_column("posts", "celebration_trigger_data")
    op.drop_column("posts", "memory_book_priority")
    op.drop_column("posts", "memory_book_eligible")
    op.drop_column("posts", "family_warmth_score")
    op.drop_column("posts", "integrated_content_id")

    # Drop memory book tables (in reverse order due to foreign keys)
    op.drop_table("family_memory_contributions")
    op.drop_table("memory_collections")
    op.drop_table("memory_book_items")

    # Drop family warmth tables
    op.drop_table("family_warmth_calculations")
    op.drop_table("family_interactions")

    # Drop content system tables
    op.drop_table("content_delivery_log")
    op.drop_table("user_content_preferences")
    op.drop_table("baby_development_content")
    op.drop_table("pregnancy_content")
    op.drop_table("content_categories")
