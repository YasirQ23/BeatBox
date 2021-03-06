"""empty message

Revision ID: bf5c2fe322a2
Revises: 3313c03fd565
Create Date: 2022-06-12 19:52:51.891752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf5c2fe322a2'
down_revision = '3313c03fd565'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('grid', sa.Column('track_img', sa.String(length=200), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('grid', 'track_img')
    # ### end Alembic commands ###
