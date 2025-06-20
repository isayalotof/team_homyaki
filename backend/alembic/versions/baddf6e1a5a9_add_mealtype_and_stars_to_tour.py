"""add meal_type and stars to tours

Revision ID: baddf6e1a5a9
Revises: f2b8d9c1add4
Create Date: 2025-06-20
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'baddf6e1a5a9'
down_revision = 'f2b8d9c1add4'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tours', sa.Column('meal_type', sa.String(length=3), nullable=True))
    op.add_column('tours', sa.Column('stars', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('tours', 'stars')
    op.drop_column('tours', 'meal_type') 