"""empty message

Revision ID: ab9bb2613281
Revises: add_instagram_feed_columns, enhance_reactions_and_threading_system
Create Date: 2025-08-12 09:19:23.201118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab9bb2613281'
down_revision: Union[str, None] = ('add_instagram_feed_columns', 'enhance_reactions_and_threading_system')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass