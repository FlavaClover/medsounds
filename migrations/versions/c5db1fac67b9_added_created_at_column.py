"""added created_at column

Revision ID: c5db1fac67b9
Revises: d5eb3f3fcb85
Create Date: 2024-12-18 00:22:34.264131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5db1fac67b9'
down_revision: Union[str, None] = 'd5eb3f3fcb85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'podcasts',
        sa.Column('created_at', sa.DateTime, server_default=sa.func.current_timestamp())
    )


def downgrade() -> None:
    op.drop_column('podcasts', 'created_at')
