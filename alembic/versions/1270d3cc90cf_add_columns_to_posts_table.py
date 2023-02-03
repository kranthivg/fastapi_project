"""add columns to posts table

Revision ID: 1270d3cc90cf
Revises: 9da49f5c19d4
Create Date: 2023-02-02 06:31:42.192489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1270d3cc90cf'
down_revision = '9da49f5c19d4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('published',sa.Boolean(),nullable=False,server_default="True"),)
    op.add_column('posts',sa.Column('created_at',sa.TIMESTAMP(timezone=True),
                   server_default=sa.text('now()'),nullable=False),)
    pass


def downgrade() -> None:
    op.drop_column('posts','published')
    op.drop_column('posts','created_at')
    pass
