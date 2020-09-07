"""added draft flag

Revision ID: 8da8ae614ab4
Revises: 49486a564338
Create Date: 2020-08-29 19:10:43.945310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8da8ae614ab4'
down_revision = '49486a564338'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('stages', sa.Column('draft', sa.Boolean(), nullable=True))
    op.add_column('steps', sa.Column('draft', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('steps', 'draft')
    op.drop_column('stages', 'draft')
    # ### end Alembic commands ###