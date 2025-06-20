"""Add image_url to discounts table

Revision ID: f2b8d9c1add4
Revises: e8a1bf8c6d2e
Create Date: 2025-06-20 08:50:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'f2b8d9c1add4'
down_revision = 'e8a1bf8c6d2e'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('discounts', sa.Column('image_url', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('discounts', 'image_url') 