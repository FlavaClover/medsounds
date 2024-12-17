"""added cascade to foreign keys

Revision ID: 23bb945ba1c4
Revises: c5db1fac67b9
Create Date: 2024-12-18 01:45:24.049530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23bb945ba1c4'
down_revision: Union[str, None] = 'c5db1fac67b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('podcast_id_fk', 'podcast_tags')
    op.create_foreign_key(
        'podcast_id_fk', 'podcast_tags', 'podcasts', ['podcast_id'], ['id'], ondelete='CASCADE'
    )

    op.drop_constraint('post_id_fk', 'post_tags')
    op.create_foreign_key(
        'post_id_fk', 'post_tags', 'posts', ['post_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('podcast_id_fk', 'podcast_tags')
    op.create_foreign_key('podcast_id_fk', 'tags', 'podcasts', ['podcast_id'], ['id'])

    op.drop_constraint('post_id_fk', 'post_tags')
    op.create_foreign_key('post_id_fk', 'post_tags', 'posts', ['post_id'], ['id'])
