"""Added quantity to product model

Revision ID: 9ed7a42e53fb
Revises: b61bf821d29a
Create Date: 2025-02-20 17:57:43.229473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ed7a42e53fb'
down_revision = 'b61bf821d29a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('quantity')

    # ### end Alembic commands ###
