"""Create baby_development table

Revision ID: 20250807_baby_dev
Revises: 13c8ccd7022d
Create Date: 2025-08-07 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250807_baby_dev'
down_revision: Union[str, None] = '13c8ccd7022d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'baby_development' not in inspector.get_table_names():
        # Create the baby_development table
        op.create_table('baby_development',
            sa.Column('id', sa.String(), nullable=False),
            sa.Column('day_of_pregnancy', sa.Integer(), nullable=False),
            sa.Column('week_number', sa.Integer(), nullable=False),
            sa.Column('trimester', sa.Integer(), nullable=False),
            sa.Column('baby_size_comparison', sa.String(length=200), nullable=False),
            sa.Column('baby_length_cm', sa.Float(), nullable=True),
            sa.Column('baby_weight_grams', sa.Float(), nullable=True),
            sa.Column('title', sa.String(length=300), nullable=False),
            sa.Column('brief_description', sa.String(length=500), nullable=False),
            sa.Column('detailed_description', sa.Text(), nullable=False),
            sa.Column('development_highlights', sa.JSON(), nullable=False),
            sa.Column('symptoms_to_expect', sa.JSON(), nullable=False),
            sa.Column('medical_milestones', sa.JSON(), nullable=False),
            sa.Column('mother_changes', sa.Text(), nullable=False),
            sa.Column('tips_and_advice', sa.Text(), nullable=False),
            sa.Column('emotional_notes', sa.Text(), nullable=False),
            sa.Column('partner_tips', sa.Text(), nullable=False),
            sa.Column('fun_fact', sa.String(length=1000), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('content_version', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('day_of_pregnancy')
        )
        
        # Create indexes
        op.create_index('ix_baby_development_day', 'baby_development', ['day_of_pregnancy'])
        op.create_index('ix_baby_development_week', 'baby_development', ['week_number'])
        op.create_index('ix_baby_development_trimester', 'baby_development', ['trimester'])
        op.create_index('ix_baby_development_active', 'baby_development', ['is_active'])
        op.create_index('ix_baby_development_week_trimester', 'baby_development', ['week_number', 'trimester'])
        
        # Add constraints
        op.create_check_constraint(
            'check_day_range', 
            'baby_development', 
            'day_of_pregnancy >= 1 AND day_of_pregnancy <= 310'
        )
        op.create_check_constraint(
            'check_week_range', 
            'baby_development', 
            'week_number >= 1 AND week_number <= 45'
        )
        op.create_check_constraint(
            'check_trimester_range', 
            'baby_development', 
            'trimester >= 1 AND trimester <= 3'
        )
        
        print("✓ Created baby_development table with all indexes and constraints")
    else:
        print("✓ baby_development table already exists, skipping creation")


def downgrade() -> None:
    # Remove the baby_development table and all related indexes/constraints
    op.drop_table('baby_development')
    print("✓ Dropped baby_development table")