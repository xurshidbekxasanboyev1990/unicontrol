"""Add REGISTRAR_OFFICE role and nb_permits table

Revision ID: add_registrar_nb
Revises: None
Create Date: 2026-02-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_registrar_nb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new role to user_role enum
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'REGISTRAR_OFFICE'")
    
    # Create permit_status enum
    permit_status_enum = postgresql.ENUM(
        'issued', 'pending', 'in_progress', 'approved', 'rejected', 'expired', 'cancelled',
        name='permit_status',
        create_type=False
    )
    op.execute("DO $$ BEGIN CREATE TYPE permit_status AS ENUM ('issued', 'pending', 'in_progress', 'approved', 'rejected', 'expired', 'cancelled'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Create nb_permits table
    op.create_table(
        'nb_permits',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('permit_code', sa.String(50), unique=True, nullable=False),
        sa.Column('verification_hash', sa.String(128), nullable=False),
        sa.Column('student_id', sa.Integer(), sa.ForeignKey('students.id'), nullable=False),
        sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id'), nullable=True),
        sa.Column('subject_name', sa.String(200), nullable=False),
        sa.Column('semester', sa.Integer(), default=1),
        sa.Column('academic_year', sa.String(20), default='2025-2026'),
        sa.Column('nb_type', sa.String(50), default='nb'),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('teacher_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('teacher_name', sa.String(100), nullable=True),
        sa.Column('issued_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('issued_by_name', sa.String(100), nullable=True),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('issued', 'pending', 'in_progress', 'approved', 'rejected', 'expired', 'cancelled', name='permit_status', create_type=False), default='issued'),
        sa.Column('result_grade', sa.String(20), nullable=True),
        sa.Column('teacher_notes', sa.Text(), nullable=True),
        sa.Column('registrar_notes', sa.Text(), nullable=True),
        sa.Column('print_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_index('ix_nb_permits_permit_code', 'nb_permits', ['permit_code'], unique=True)
    op.create_index('ix_nb_permits_student_id', 'nb_permits', ['student_id'])
    op.create_index('ix_nb_permits_teacher_id', 'nb_permits', ['teacher_id'])
    op.create_index('ix_nb_permits_status', 'nb_permits', ['status'])


def downgrade() -> None:
    op.drop_table('nb_permits')
    op.execute("DROP TYPE IF EXISTS permit_status")
