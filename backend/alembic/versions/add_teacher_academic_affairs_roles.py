"""Add TEACHER and ACADEMIC_AFFAIRS to user_role enum

Revision ID: add_teacher_academic
Revises: None
Create Date: 2026-02-18
"""
from alembic import op

# revision identifiers
revision = 'add_teacher_academic'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new values to user_role enum
    # Note: ALTER TYPE ... ADD VALUE cannot run inside a transaction in some PG versions
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'TEACHER'")
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'ACADEMIC_AFFAIRS'")


def downgrade() -> None:
    # PostgreSQL does not support removing enum values easily
    # This is intentionally left as a no-op
    pass
