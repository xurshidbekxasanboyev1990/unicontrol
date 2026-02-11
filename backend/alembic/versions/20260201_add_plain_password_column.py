"""add plain_password column to users

Revision ID: add_plain_password
Revises: 20260130_add_telegram_notified_column
Create Date: 2026-02-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_plain_password'
down_revision = '20260130_add_telegram_notified_column'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('plain_password', sa.String(255), nullable=True, comment='Plain text password for admin viewing'))


def downgrade() -> None:
    op.drop_column('users', 'plain_password')
