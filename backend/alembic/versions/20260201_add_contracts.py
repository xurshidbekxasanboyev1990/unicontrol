"""Add contracts table

Revision ID: 20260201_add_contracts
Revises: 20260130_add_telegram_notified_column
Create Date: 2026-02-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '20260201_add_contracts'
down_revision = '20260130_add_telegram_notified_column'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('academic_year', sa.String(length=20), nullable=False, server_default='2025-2026'),
        sa.Column('course', sa.String(length=20), nullable=True),
        sa.Column('student_status', sa.String(length=50), nullable=True),
        sa.Column('direction', sa.String(length=200), nullable=True),
        sa.Column('education_form', sa.String(length=50), nullable=True),
        sa.Column('contract_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('grant_percentage', sa.Float(), nullable=True),
        sa.Column('grant_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('debt_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('payment_percentage', sa.Float(), nullable=True),
        sa.Column('total_paid', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('refund_amount', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('year_start_balance', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('year_end_balance', sa.Numeric(precision=15, scale=2), nullable=False, server_default='0'),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('student_id', 'academic_year', name='uq_contract_student_year'),
    )
    op.create_index(op.f('ix_contracts_student_id'), 'contracts', ['student_id'])
    op.create_index(op.f('ix_contracts_academic_year'), 'contracts', ['academic_year'])


def downgrade() -> None:
    op.drop_index(op.f('ix_contracts_academic_year'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_student_id'), table_name='contracts')
    op.drop_table('contracts')
