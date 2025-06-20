"""merge_heads

Revision ID: 488622cd3d86
Revises: baddf6e1a5a9, update_reviews_for_guests
Create Date: 2025-06-20 02:20:31.099715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '488622cd3d86'
down_revision = ('baddf6e1a5a9', 'update_reviews_for_guests')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass 