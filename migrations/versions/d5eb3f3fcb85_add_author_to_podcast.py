"""add author to podcast

Revision ID: d5eb3f3fcb85
Revises: 0796df17dfb4
Create Date: 2024-12-17 01:32:32.049344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5eb3f3fcb85'
down_revision: Union[str, None] = '0796df17dfb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'podcasts',
        sa.Column('author', sa.String(127), nullable=True)
    )


def downgrade() -> None:
    op.drop_column(
        'podcasts', 'author'
    )
