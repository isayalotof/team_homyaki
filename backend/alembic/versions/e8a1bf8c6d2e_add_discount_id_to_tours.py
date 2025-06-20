"""Add discount_id to tours table

Revision ID: e8a1bf8c6d2e
Revises: c410c48cc0ab
Create Date: 2025-06-20 08:30:00

"""
from alembic import op
import sqlalchemy as sa

revision = 'e8a1bf8c6d2e'
down_revision = 'a4b5c6d7e8f9'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('tours', sa.Column('discount_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_tours_discount', 'tours', 'discounts', ['discount_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_tours_discount', 'tours', type_='foreignkey')
    op.drop_column('tours', 'discount_id') 