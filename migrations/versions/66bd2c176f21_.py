"""empty message

Revision ID: 66bd2c176f21
Revises: 1510db3e6b64
Create Date: 2025-07-15 19:01:08.571198

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66bd2c176f21'
down_revision = '1510db3e6b64'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_conf_exp', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_user_email_conf_exp'), ['email_conf_exp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_email_conf_exp'))
        batch_op.drop_column('email_conf_exp')

    # ### end Alembic commands ###
