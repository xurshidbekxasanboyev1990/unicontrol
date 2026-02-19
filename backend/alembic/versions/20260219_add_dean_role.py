"""add dean role

Revision ID: add_dean_role_001
Revises: 20260219_add_registrar_nb_permits
Create Date: 2026-02-19
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_dean_role_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostgreSQL: Add 'dean' value to user_role enum
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'dean' AFTER 'registrar_office'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values easily
    pass
