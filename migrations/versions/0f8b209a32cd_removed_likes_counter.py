"""removed likes counter

Revision ID: 0f8b209a32cd
Revises: 55e68d50d0ef
Create Date: 2024-12-11 01:25:02.194353

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f8b209a32cd'
down_revision: Union[str, None] = '55e68d50d0ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('likes_gte_zero', 'podcasts')
    op.drop_column('podcasts', 'likes')


def downgrade() -> None:
    op.add_column('podcasts', sa.Column('likes', sa.Integer, server_default='0'))

    op.create_check_constraint(
        'likes_gte_zero',
        'podcasts',
        'likes = 0 or likes > 0'
    )
