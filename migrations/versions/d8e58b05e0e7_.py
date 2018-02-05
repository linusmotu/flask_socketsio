"""empty message

Revision ID: d8e58b05e0e7
Revises: 7cb215bd27eb
Create Date: 2018-01-30 18:10:36.576604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8e58b05e0e7'
down_revision = '7cb215bd27eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('slavenode', sa.Column('masternode_name', sa.String(length=64), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('slavenode', 'masternode_name')
    # ### end Alembic commands ###