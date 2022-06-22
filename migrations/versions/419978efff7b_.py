"""empty message

Revision ID: 419978efff7b
Revises: 7ea29cde2250
Create Date: 2022-06-22 09:11:47.883051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '419978efff7b'
down_revision = '7ea29cde2250'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('comments', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'comments')
    # ### end Alembic commands ###