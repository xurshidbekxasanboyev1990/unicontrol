"""Add telegram_notified column to attendances table

Revision ID: add_telegram_notified
Revises: 0e185a7fabdd
Create Date: 2026-01-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_telegram_notified'
down_revision: Union[str, None] = '0e185a7fabdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add telegram_notified column to attendances table
    # Default False - records not yet notified by backend
    op.add_column(
        'attendances',
        sa.Column(
            'telegram_notified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            comment='Whether Telegram notification was already sent by backend'
        )
    )


def downgrade() -> None:
    op.drop_column('attendances', 'telegram_notified')
