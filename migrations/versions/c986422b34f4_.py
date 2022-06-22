"""empty message

Revision ID: c986422b34f4
Revises: 419978efff7b
Create Date: 2022-06-22 09:14:18.274611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c986422b34f4'
down_revision = '419978efff7b'
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
