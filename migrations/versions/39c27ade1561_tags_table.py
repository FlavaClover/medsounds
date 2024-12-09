"""tags table

Revision ID: 39c27ade1561
Revises: ccc1452662b1
Create Date: 2024-12-09 22:41:28.027160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '39c27ade1561'
down_revision: Union[str, None] = 'ccc1452662b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tag', sa.String(127), nullable=False),
        sa.Column('podcast_id', sa.Integer, nullable=False)
    )

    op.create_foreign_key('podcast_id_fk', 'tags', 'podcasts', ['podcast_id'], ['id'])
    op.create_unique_constraint('podcast_tag_uq', 'tags', ['tag', 'podcast_id'])


def downgrade() -> None:
    op.drop_table('tags')
