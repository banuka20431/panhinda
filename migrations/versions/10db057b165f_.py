"""empty message

Revision ID: 10db057b165f
Revises: 
Create Date: 2025-07-16 17:58:04.453410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10db057b165f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=32), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=32), nullable=False),
    sa.Column('last_name', sa.String(length=32), nullable=False),
    sa.Column('date_of_birth', sa.Date(), nullable=False),
    sa.Column('gender', sa.Enum('M', 'F', name='genderenum'), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('phone_number', sa.String(length=256), nullable=False),
    sa.Column('phone_number_last_digits', sa.String(length=3), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('profile_picture_uri', sa.String(length=512), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('otp_hash', sa.String(length=256), nullable=True),
    sa.Column('otp_expiration', sa.DateTime(), nullable=True),
    sa.Column('email_conf_exp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_email_conf_exp'), ['email_conf_exp'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_otp_expiration'), ['otp_expiration'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_phone_number'), ['phone_number'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('article',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=256), nullable=False),
    sa.Column('body', sa.String(length=12288), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('edited', sa.DateTime(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description'),
    sa.UniqueConstraint('title')
    )
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_article_author_id'), ['author_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_article_category_id'), ['category_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_article_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_article_edited'), ['edited'], unique=False)

    op.create_table('sub_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('label', sa.String(length=32), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('sub_category', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sub_category_category_id'), ['category_id'], unique=False)

    op.create_table('user_interest',
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'user_id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=1024), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('edited', sa.DateTime(), nullable=True),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_comment_created'), ['created'], unique=False)
        batch_op.create_index(batch_op.f('ix_comment_edited'), ['edited'], unique=False)

    op.create_table('like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('added', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_like_added'), ['added'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('like', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_like_added'))

    op.drop_table('like')
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_comment_edited'))
        batch_op.drop_index(batch_op.f('ix_comment_created'))

    op.drop_table('comment')
    op.drop_table('user_interest')
    with op.batch_alter_table('sub_category', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sub_category_category_id'))

    op.drop_table('sub_category')
    with op.batch_alter_table('article', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_article_edited'))
        batch_op.drop_index(batch_op.f('ix_article_created'))
        batch_op.drop_index(batch_op.f('ix_article_category_id'))
        batch_op.drop_index(batch_op.f('ix_article_author_id'))

    op.drop_table('article')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_phone_number'))
        batch_op.drop_index(batch_op.f('ix_user_otp_expiration'))
        batch_op.drop_index(batch_op.f('ix_user_email_conf_exp'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('category')
    # ### end Alembic commands ###
