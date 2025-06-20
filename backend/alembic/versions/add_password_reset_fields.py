"""add_password_reset_fields

Revision ID: a4b5c6d7e8f9
Revises: a311d3d89f16
Create Date: 2023-11-26 13:45:20.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4b5c6d7e8f9'
down_revision: Union[str, None] = 'a311d3d89f16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем поля для восстановления пароля
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Удаляем поля при откате
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token') 