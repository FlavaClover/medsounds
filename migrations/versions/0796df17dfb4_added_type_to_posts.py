"""added type to posts

Revision ID: 0796df17dfb4
Revises: c8a2d3503b30
Create Date: 2024-12-13 02:22:59.871790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0796df17dfb4'
down_revision: Union[str, None] = 'c8a2d3503b30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('type', sa.String(255), server_default='academy'))


def downgrade() -> None:
    op.drop_column('posts', 'type')
