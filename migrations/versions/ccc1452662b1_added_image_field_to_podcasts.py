"""added image field to podcasts

Revision ID: ccc1452662b1
Revises: 60171179fc8c
Create Date: 2024-12-09 03:58:49.174358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccc1452662b1'
down_revision: Union[str, None] = '60171179fc8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'podcasts',
        sa.Column('image', sa.LargeBinary, nullable=False)
    )


def downgrade() -> None:
    op.drop_column('podcasts', 'image')
