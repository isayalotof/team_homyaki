"""Add client status and favorites manually

Revision ID: 72b276ce0572
Revises: a63992c0c01a
Create Date: 2025-06-19 13:46:16.892015

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72b276ce0572'
down_revision = 'a63992c0c01a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_favorite_tours',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('tour_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['tour_id'], ['tours.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'tour_id')
    )
    op.add_column('users', sa.Column('client_status', sa.Enum('REGULAR', 'SILVER', 'GOLD', 'PLATINUM', name='clientstatus'), nullable=True))
    op.execute("UPDATE users SET client_status = 'REGULAR'")
    op.alter_column('users', 'client_status', nullable=False)
    
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))


def downgrade():
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'client_status')
    op.drop_table('user_favorite_tours') 