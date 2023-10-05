"""initial migration

Revision ID: c0b85395fddf
Revises: 
Create Date: 2023-09-27 16:12:36.240202

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c0b85395fddf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('api_key', sa.String(length=80), nullable=False),
    sa.Column('budget', sa.Integer(), nullable=False),
    sa.Column('course', sa.String(length=80), nullable=False),
    sa.Column('usage', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('api_key'),
    sa.UniqueConstraint('name')
    )
    op.create_table('chat',
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.Column('model_type', sa.String(length=80), nullable=True),
    sa.Column('instruction_prefix', sa.Text(), nullable=True),
    sa.Column('user_prefix', sa.Text(), nullable=True),
    sa.Column('assistant_prefix', sa.Text(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_chat_account_id'), ['account_id'], unique=False)

    op.create_table('user',
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('code', sa.String(length=80), nullable=False),
    sa.Column('account_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('message',
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='messagerole'), nullable=True),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('model_args', sa.JSON(), nullable=True),
    sa.Column('usage', sa.JSON(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_message_chat_id'), ['chat_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_message_chat_id'))

    op.drop_table('message')
    op.drop_table('user')
    with op.batch_alter_table('chat', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_chat_account_id'))

    op.drop_table('chat')
    op.drop_table('account')
    # ### end Alembic commands ###