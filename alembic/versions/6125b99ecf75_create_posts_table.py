"""create posts table

Revision ID: 6125b99ecf75
Revises: 
Create Date: 2023-02-02 06:04:17.126900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6125b99ecf75'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('posts', sa.Column('id',sa.Integer(),nullable=False,primary_key=True),
    sa.Column('title',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_table('posts')
    pass
