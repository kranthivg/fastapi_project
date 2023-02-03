"""add content column to posts table

Revision ID: 49952049012c
Revises: 6125b99ecf75
Create Date: 2023-02-02 06:12:28.894910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49952049012c'
down_revision = '6125b99ecf75'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('content',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts','content')
    pass
