"""Added username to User

Revision ID: 7ccc775b5e4f
Revises: 26d7d139fbe0
Create Date: 2023-01-14 16:25:53.505385

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ccc775b5e4f'
down_revision = '26d7d139fbe0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('username')

    # ### end Alembic commands ###
