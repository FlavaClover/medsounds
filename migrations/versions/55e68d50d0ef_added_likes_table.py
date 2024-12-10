"""added likes table

Revision ID: 55e68d50d0ef
Revises: effdc352208c
Create Date: 2024-12-11 01:20:14.486455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55e68d50d0ef'
down_revision: Union[str, None] = 'effdc352208c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'post_likes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('browser_ident', sa.String(255), nullable=False),
        sa.Column('post_id', sa.Integer, nullable=False)
    )

    op.create_unique_constraint(
        'browser_ident_post_id_uq', 'post_likes', ['browser_ident', 'post_id']
    )

    op.create_foreign_key(
        'post_id_fk', 'post_likes', 'posts', ['post_id'], ['id'], ondelete='CASCADE'
    )

    op.create_table(
        'podcast_likes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('browser_ident', sa.String(255), nullable=False),
        sa.Column('podcast_id', sa.Integer, nullable=False)
    )

    op.create_unique_constraint(
        'browser_ident_podcast_id_uq', 'podcast_likes', ['browser_ident', 'podcast_id']
    )

    op.create_foreign_key(
        'podcast_id_fk', 'podcast_likes', 'podcasts', ['podcast_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_table('post_likes')
    op.drop_table('podcast_likes')
