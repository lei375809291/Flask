"""empty message

Revision ID: c3ef369d6e80
Revises: 814fdeccfd89
Create Date: 2018-08-29 20:11:30.359466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3ef369d6e80'
down_revision = '814fdeccfd89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('icon', sa.String(length=40), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'icon')
    # ### end Alembic commands ###
