"""change podcast and image type

Revision ID: c8a2d3503b30
Revises: 0f8b209a32cd
Create Date: 2024-12-11 02:37:57.913188

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8a2d3503b30'
down_revision: Union[str, None] = '0f8b209a32cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'podcasts', 'image', type_=sa.Text
    )

    op.alter_column(
        'podcasts', 'podcast', type_=sa.Text
    )


def downgrade() -> None:
    op.alter_column(
        'podcasts', 'image', type_=sa.LargeBinary
    )

    op.alter_column(
        'podcasts', 'podcast', type_=sa.LargeBinary
    )
