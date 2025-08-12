"""empty message

Revision ID: de59728f572f
Revises: 20250807_baby_dev, add_token_invite, instagram_feed_overhaul
Create Date: 2025-08-09 13:50:11.608078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de59728f572f'
down_revision: Union[str, None] = ('20250807_baby_dev', 'add_token_invite', 'instagram_feed_overhaul')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass