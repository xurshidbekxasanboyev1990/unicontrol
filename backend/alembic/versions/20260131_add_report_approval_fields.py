"""Add report approval fields and enum values

Revision ID: add_report_approval
Revises: 20260130_add_telegram_notified_column
Create Date: 2026-01-31
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_report_approval'
down_revision = None  # standalone migration
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add new enum values to reportstatus
    # PostgreSQL requires ALTER TYPE to add new enum values
    op.execute("ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'APPROVED'")
    op.execute("ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'REJECTED'")

    # 2. Add new columns for approval workflow
    op.add_column('reports', sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
    op.add_column('reports', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('reports', sa.Column('rejection_reason', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('reports', 'rejection_reason')
    op.drop_column('reports', 'approved_at')
    op.drop_column('reports', 'approved_by')
    # Note: PostgreSQL does not support removing enum values easily
