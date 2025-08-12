"""Add token field to family invitations

Revision ID: add_token_invite
Revises: 54584cc27ecc
Create Date: 2025-08-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_token_invite'
down_revision: Union[str, None] = '54584cc27ecc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add token column to family_invitations table
    op.add_column('family_invitations', sa.Column('token', sa.String(), nullable=True))
    
    # Create unique index on token field
    op.create_index('ix_family_invitations_token', 'family_invitations', ['token'], unique=True)
    
    # Make email field nullable to support link-based invites
    op.alter_column('family_invitations', 'email', nullable=True)


def downgrade() -> None:
    # Drop the index
    op.drop_index('ix_family_invitations_token', table_name='family_invitations')
    
    # Remove token column
    op.drop_column('family_invitations', 'token')
    
    # Make email required again
    op.alter_column('family_invitations', 'email', nullable=False)