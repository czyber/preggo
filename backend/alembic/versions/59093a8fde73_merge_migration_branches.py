"""Merge migration branches

Revision ID: 59093a8fde73
Revises: ab9bb2613281, add_missing_instagram_columns
Create Date: 2025-08-12 09:23:26.794258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59093a8fde73'
down_revision: Union[str, None] = ('ab9bb2613281', 'add_missing_instagram_columns')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass