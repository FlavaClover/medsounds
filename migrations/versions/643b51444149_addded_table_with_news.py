"""addded table with news

Revision ID: 643b51444149
Revises: 39c27ade1561
Create Date: 2024-12-09 23:06:24.921433

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '643b51444149'
down_revision: Union[str, None] = '39c27ade1561'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('tags', new_table_name='podcast_tags')

    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('image', sa.LargeBinary, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.current_timestamp())
    )

    op.create_table(
        'post_tags',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tag', sa.String(127), nullable=False),
        sa.Column('post_id', sa.Integer, nullable=False)
    )

    op.create_foreign_key('post_id_fk', 'post_tags', 'posts', ['post_id'], ['id'])
    op.create_unique_constraint('post_tag_uq', 'post_tags', ['tag', 'post_id'])


def downgrade() -> None:
    op.drop_table('post_tags')
    op.rename_table('podcast_tags', new_table_name='tags')
    op.drop_table('posts')
