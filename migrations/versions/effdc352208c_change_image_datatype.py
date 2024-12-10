"""change image datatype

Revision ID: effdc352208c
Revises: 643b51444149
Create Date: 2024-12-10 03:54:38.549115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'effdc352208c'
down_revision: Union[str, None] = '643b51444149'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'posts', 'image', type_=sa.Text
    )


def downgrade() -> None:
    op.alter_column(
        'posts', 'image', type_=sa.LargeBinary
    )
