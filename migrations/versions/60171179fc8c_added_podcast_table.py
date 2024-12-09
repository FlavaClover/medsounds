"""added podcast table

Revision ID: 60171179fc8c
Revises: 
Create Date: 2024-12-09 02:56:36.868194

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60171179fc8c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'podcasts',
        sa.Column('id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('title', sa.String(127), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('duration', sa.Integer, nullable=False),
        sa.Column('likes', sa.Integer, nullable=False, server_default='0'),
        sa.Column('auditions', sa.Integer, nullable=False, server_default='0'),
        sa.Column('podcast', sa.LargeBinary, nullable=False)
    )

    op.create_check_constraint(
        'likes_gte_zero',
        'podcasts',
        'likes = 0 or likes > 0'
    )

    op.create_check_constraint(
        'auditions_gte_zero',
        'podcasts',
        'auditions = 0 or auditions > 0'
    )


def downgrade() -> None:
    op.drop_table('podcasts')
