"""update reviews table for guest reviews

Revision ID: update_reviews_for_guests
Revises: f2b8d9c1add4
Create Date: 2023-06-25

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_reviews_for_guests'
down_revision = 'f2b8d9c1add4'
branch_labels = None
depends_on = None


def upgrade():
    # Make user_id nullable
    op.alter_column('reviews', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    
    # Set comment to not nullable
    op.alter_column('reviews', 'comment',
               existing_type=sa.TEXT(),
               nullable=False)
    
    # Add new columns
    op.add_column('reviews', sa.Column('author_name', sa.String(length=100), nullable=True))
    op.add_column('reviews', sa.Column('author_email', sa.String(length=255), nullable=True))
    op.add_column('reviews', sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    # Drop new columns
    op.drop_column('reviews', 'verified')
    op.drop_column('reviews', 'author_email')
    op.drop_column('reviews', 'author_name')
    
    # Make user_id not nullable
    op.alter_column('reviews', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    
    # Make comment nullable again
    op.alter_column('reviews', 'comment',
               existing_type=sa.TEXT(),
               nullable=True) 