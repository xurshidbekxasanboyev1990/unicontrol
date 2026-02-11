"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('login', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('avatar', sa.String(500), nullable=True),
        sa.Column('role', sa.Enum('STUDENT', 'LEADER', 'ADMIN', 'SUPERADMIN', name='user_role'), nullable=False, default='STUDENT'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_first_login', sa.Boolean(), nullable=False, default=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('refresh_token', sa.String(500), nullable=True),
        sa.Column('settings', sa.Text(), nullable=True),
        sa.Column('device_tokens', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_login', 'users', ['login'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'])

    # Create groups table
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('faculty', sa.String(100), nullable=True),
        sa.Column('course', sa.Integer(), nullable=True),
        sa.Column('academic_year', sa.String(20), nullable=True),
        sa.Column('leader_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('mutoola_id', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['leader_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_groups_code', 'groups', ['code'], unique=True)
    op.create_index('ix_groups_name', 'groups', ['name'])

    # Create students table
    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('hemis_id', sa.String(50), nullable=True),
        sa.Column('student_id', sa.String(50), nullable=True),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('contract_number', sa.String(50), nullable=True),
        sa.Column('contract_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('scholarship_type', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('mutoola_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_students_hemis_id', 'students', ['hemis_id'], unique=True)
    op.create_index('ix_students_student_id', 'students', ['student_id'])
    op.create_index('ix_students_group_id', 'students', ['group_id'])
    op.create_index('ix_students_full_name', 'students', ['full_name'])

    # Create attendance table
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('present', 'absent', 'late', 'excused', name='attendancestatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('marked_by', sa.Integer(), nullable=True),
        sa.Column('marked_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['marked_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attendance_student_date', 'attendance', ['student_id', 'date'])
    op.create_index('ix_attendance_date', 'attendance', ['date'])

    # Create schedules table
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('subject_name', sa.String(150), nullable=False),
        sa.Column('teacher_name', sa.String(100), nullable=True),
        sa.Column('day_of_week', sa.Enum('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', name='weekday'), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('room', sa.String(50), nullable=True),
        sa.Column('building', sa.String(100), nullable=True),
        sa.Column('schedule_type', sa.Enum('lecture', 'practice', 'lab', 'seminar', 'exam', name='scheduletype'), nullable=True),
        sa.Column('semester', sa.Integer(), nullable=True),
        sa.Column('academic_year', sa.String(20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_cancelled', sa.Boolean(), nullable=True, default=False),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('mutoola_id', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_schedules_group_id', 'schedules', ['group_id'])
    op.create_index('ix_schedules_day_of_week', 'schedules', ['day_of_week'])

    # Add schedule_id foreign key to attendance
    op.create_foreign_key(
        'fk_attendance_schedule_id',
        'attendance', 'schedules',
        ['schedule_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.Enum('info', 'warning', 'error', 'success', 'attendance', 'schedule', 'report', name='notificationtype'), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True, default=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('action_url', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.Enum('attendance', 'performance', 'group_summary', 'student_report', 'custom', name='reporttype'), nullable=False),
        sa.Column('status', sa.Enum('draft', 'pending', 'approved', 'rejected', name='reportstatus'), nullable=True, default='draft'),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('file_path', sa.String(255), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reports_report_type', 'reports', ['report_type'])
    op.create_index('ix_reports_status', 'reports', ['status'])

    # Create mutoola_sync table
    op.create_table(
        'mutoola_sync',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('sync_type', sa.Enum('full', 'incremental', 'manual', name='synctype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', name='syncstatus'), nullable=False),
        sa.Column('records_synced', sa.Integer(), nullable=True, default=0),
        sa.Column('records_failed', sa.Integer(), nullable=True, default=0),
        sa.Column('errors', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_mutoola_sync_entity_type', 'mutoola_sync', ['entity_type'])
    op.create_index('ix_mutoola_sync_status', 'mutoola_sync', ['status'])

    # Create activity_logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('old_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_activity_logs_user_id', 'activity_logs', ['user_id'])
    op.create_index('ix_activity_logs_action', 'activity_logs', ['action'])
    op.create_index('ix_activity_logs_entity_type', 'activity_logs', ['entity_type'])
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('activity_logs')
    op.drop_table('mutoola_sync')
    op.drop_table('reports')
    op.drop_table('notifications')
    op.drop_constraint('fk_attendance_schedule_id', 'attendance', type_='foreignkey')
    op.drop_table('schedules')
    op.drop_table('attendance')
    op.drop_table('students')
    op.drop_table('groups')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS user_role')
    op.execute('DROP TYPE IF EXISTS attendancestatus')
    op.execute('DROP TYPE IF EXISTS weekday')
    op.execute('DROP TYPE IF EXISTS scheduletype')
    op.execute('DROP TYPE IF EXISTS notificationtype')
    op.execute('DROP TYPE IF EXISTS reporttype')
    op.execute('DROP TYPE IF EXISTS reportstatus')
    op.execute('DROP TYPE IF EXISTS synctype')
    op.execute('DROP TYPE IF EXISTS syncstatus')
