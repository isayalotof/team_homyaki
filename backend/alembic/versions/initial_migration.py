"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2025-06-19 06:17:18.575306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role = postgresql.ENUM('client', 'agency_manager', 'operator_manager', 'admin', name='userrole', create_type=True)
    user_role.create(op.get_bind())
    
    user_status = postgresql.ENUM('active', 'inactive', 'blocked', 'pending', name='userstatus', create_type=True)
    user_status.create(op.get_bind())
    
    meal_type = postgresql.ENUM('RO', 'BB', 'HB', 'FB', 'AI', 'UAI', name='mealtype', create_type=True)
    meal_type.create(op.get_bind())
    
    discount_type = postgresql.ENUM('fixed', 'percentage', name='discounttype', create_type=True)
    discount_type.create(op.get_bind())
    
    # Create tables
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('role', sa.Enum('client', 'agency_manager', 'operator_manager', 'admin', name='userrole'), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', 'blocked', 'pending', name='userstatus'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    
    op.create_table(
        'hotels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('stars', sa.Integer(), nullable=False),
        sa.Column('meal_type', sa.Enum('RO', 'BB', 'HB', 'FB', 'AI', 'UAI', name='mealtype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hotels_id'), 'hotels', ['id'], unique=False)
    
    op.create_table(
        'tour_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tour_types_id'), 'tour_types', ['id'], unique=False)
    
    op.create_table(
        'discounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('fixed', 'percentage', name='discounttype'), nullable=False),
        sa.Column('value', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('conditions', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_discounts_id'), 'discounts', ['id'], unique=False)
    
    op.create_table(
        'tours',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('country', sa.String(length=255), nullable=False),
        sa.Column('city', sa.String(length=255), nullable=False),
        sa.Column('base_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('max_tourists', sa.Integer(), nullable=True),
        sa.Column('available_count', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tours_id'), 'tours', ['id'], unique=False)
    
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tour_id', sa.Integer(), nullable=False),
        sa.Column('tourists_count', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tour_id'], ['tours.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)
    
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tour_id', sa.Integer(), nullable=True),
        sa.Column('hotel_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['hotel_id'], ['hotels.id'], ),
        sa.ForeignKeyConstraint(['tour_id'], ['tours.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    
    op.create_table(
        'tour_tour_types',
        sa.Column('tour_id', sa.Integer(), nullable=False),
        sa.Column('tour_type_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['tour_id'], ['tours.id'], ),
        sa.ForeignKeyConstraint(['tour_type_id'], ['tour_types.id'], ),
        sa.PrimaryKeyConstraint('tour_id', 'tour_type_id')
    )


def downgrade() -> None:
    op.drop_table('tour_tour_types')
    op.drop_table('reviews')
    op.drop_table('bookings')
    op.drop_table('tours')
    op.drop_table('discounts')
    op.drop_table('tour_types')
    op.drop_table('hotels')
    op.drop_table('users')
    
    # Drop enum types
    sa.Enum(name='discounttype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='mealtype').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True) 