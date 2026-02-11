"""
UniControl - Attendance Service
===============================
Handles attendance tracking operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import joinedload

from app.models.attendance import Attendance, AttendanceStatus
from app.models.student import Student
from app.models.group import Group
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceBatch,
    AttendanceStats,
    DailyAttendanceSummary,
    StudentAttendanceSummary,
)
from app.core.exceptions import NotFoundException, ConflictException


class AttendanceService:
    """Attendance management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, attendance_id: int) -> Optional[Attendance]:
        """Get attendance by ID."""
        result = await self.db.execute(
            select(Attendance)
            .options(joinedload(Attendance.student))
            .where(Attendance.id == attendance_id)
        )
        return result.scalar_one_or_none()
    
    async def get_student_attendance(
        self,
        student_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[Attendance]:
        """Get attendance records for a student."""
        query = select(Attendance).where(Attendance.student_id == student_id)
        
        if date_from:
            query = query.where(Attendance.date >= date_from)
        if date_to:
            query = query.where(Attendance.date <= date_to)
        
        query = query.order_by(Attendance.date.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def list_attendance(
        self,
        page: int = 1,
        page_size: int = 50,
        group_id: Optional[int] = None,
        student_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        status: Optional[AttendanceStatus] = None
    ) -> Tuple[List[Attendance], int]:
        """
        List attendance with pagination and filters.
        """
        query = select(Attendance).options(joinedload(Attendance.student))
        count_query = select(func.count(Attendance.id))
        
        # Join with Student for group filtering
        if group_id:
            query = query.join(Student).where(Student.group_id == group_id)
            count_query = count_query.join(Student).where(Student.group_id == group_id)
        
        if student_id:
            query = query.where(Attendance.student_id == student_id)
            count_query = count_query.where(Attendance.student_id == student_id)
        
        if date_from:
            query = query.where(Attendance.date >= date_from)
            count_query = count_query.where(Attendance.date >= date_from)
        
        if date_to:
            query = query.where(Attendance.date <= date_to)
            count_query = count_query.where(Attendance.date <= date_to)
        
        if status:
            query = query.where(Attendance.status == status)
            count_query = count_query.where(Attendance.status == status)
        
        # Get total
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Pagination
        query = query.order_by(Attendance.date.desc(), Attendance.student_id)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        attendances = result.unique().scalars().all()
        
        return list(attendances), total
    
    async def create(
        self,
        attendance_data: AttendanceCreate,
        recorded_by: Optional[int] = None
    ) -> Tuple[Attendance, bool]:
        """Create attendance record. Returns (attendance, is_new) tuple.
        is_new=True if a new record was created, False if existing was updated (upsert)."""
        # Check if attendance already exists for this student and date
        existing_result = await self.db.execute(
            select(Attendance).where(
                and_(
                    Attendance.student_id == attendance_data.student_id,
                    Attendance.date == attendance_data.date,
                    Attendance.lesson_number == attendance_data.lesson_number
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            # Track if status actually changed
            old_status = existing.status
            # Update existing record
            for field, value in attendance_data.model_dump().items():
                setattr(existing, field, value)
            existing.recorded_by = recorded_by
            await self.db.commit()
            # Return is_new=False — this is an upsert update
            return existing, False
        
        # Create new record
        attendance = Attendance(
            **attendance_data.model_dump(),
            recorded_by=recorded_by
        )
        
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        
        return attendance, True
    
    async def update(
        self,
        attendance_id: int,
        attendance_data: AttendanceUpdate
    ) -> Attendance:
        """Update attendance record."""
        attendance = await self.get_by_id(attendance_id)
        if not attendance:
            raise NotFoundException("Attendance record not found")
        
        update_data = attendance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(attendance, field, value)
        
        await self.db.commit()
        await self.db.refresh(attendance)
        
        return attendance
    
    async def delete(self, attendance_id: int) -> bool:
        """Delete attendance record."""
        attendance = await self.get_by_id(attendance_id)
        if not attendance:
            raise NotFoundException("Attendance record not found")
        
        await self.db.delete(attendance)
        await self.db.commit()
        
        return True
    
    async def batch_create(
        self,
        batch_data: AttendanceBatch,
        recorded_by: Optional[int] = None
    ) -> Tuple[List[Attendance], int]:
        """Create attendance records in batch. 
        Returns (attendances, new_count) — new_count is how many were truly new (not upsert)."""
        attendances = []
        new_count = 0
        
        for item in batch_data.attendances:
            attendance_data = AttendanceCreate(
                student_id=item.student_id,
                date=batch_data.date,
                status=item.status,
                check_in_time=item.check_in_time,
                late_minutes=item.late_minutes,
                subject=batch_data.subject,
                lesson_number=batch_data.lesson_number,
                note=item.note,
            )
            
            attendance, is_new = await self.create(attendance_data, recorded_by)
            attendances.append(attendance)
            if is_new:
                new_count += 1
        
        return attendances, new_count
    
    async def get_daily_summary(
        self,
        target_date: date,
        group_id: Optional[str] = None
    ) -> DailyAttendanceSummary:
        """
        Get attendance summary for a day.
        group_id can be numeric ID or group name string.
        """
        query = select(Attendance).where(Attendance.date == target_date)
        
        if group_id:
            # Check if group_id is numeric or string (group name)
            if group_id.isdigit():
                query = query.join(Student).where(Student.group_id == int(group_id))
            else:
                # Find group by name first
                group_result = await self.db.execute(
                    select(Group).where(Group.name == group_id)
                )
                group = group_result.scalar_one_or_none()
                if group:
                    query = query.join(Student).where(Student.group_id == group.id)
                else:
                    # Return empty summary if group not found
                    return DailyAttendanceSummary(
                        date=target_date,
                        total_students=0,
                        present_count=0,
                        absent_count=0,
                        late_count=0,
                        excused_count=0,
                        attendance_rate=0.0
                    )
        
        result = await self.db.execute(query)
        attendances = result.scalars().all()
        
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        excused = sum(1 for a in attendances if a.status == AttendanceStatus.EXCUSED)
        
        return DailyAttendanceSummary(
            date=target_date,
            total_students=total,
            present_count=present,
            absent_count=absent,
            late_count=late,
            excused_count=excused,
            attendance_rate=float(present / total * 100) if total > 0 else 0
        )
    
    async def get_student_stats(
        self,
        student_id: int,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> AttendanceStats:
        """Get attendance statistics for a student."""
        query = select(Attendance).where(Attendance.student_id == student_id)
        
        if date_from:
            query = query.where(Attendance.date >= date_from)
        if date_to:
            query = query.where(Attendance.date <= date_to)
        
        result = await self.db.execute(query)
        attendances = result.scalars().all()
        
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        excused = sum(1 for a in attendances if a.status == AttendanceStatus.EXCUSED)
        
        return AttendanceStats(
            total_days=total,
            present_days=present,
            absent_days=absent,
            late_days=late,
            excused_days=excused,
            attendance_rate=float(present / total * 100) if total > 0 else 0,
            late_rate=float(late / total * 100) if total > 0 else 0
        )
    
    async def get_group_attendance_summary(
        self,
        group_id: int,
        date_from: date,
        date_to: date
    ) -> List[StudentAttendanceSummary]:
        """Get attendance summary for all students in a group."""
        # Get students
        students_result = await self.db.execute(
            select(Student)
            .where(Student.group_id == group_id)
            .where(Student.is_active == True)
            .options(joinedload(Student.group))
            .order_by(Student.name)
        )
        students = students_result.unique().scalars().all()
        
        summaries = []
        
        for student in students:
            stats = await self.get_student_stats(student.id, date_from, date_to)
            
            # Get total late minutes
            late_result = await self.db.execute(
                select(func.sum(Attendance.late_minutes))
                .where(Attendance.student_id == student.id)
                .where(Attendance.date >= date_from)
                .where(Attendance.date <= date_to)
            )
            total_late = late_result.scalar() or 0
            
            summaries.append(StudentAttendanceSummary(
                student_id=student.id,
                student_name=student.name,
                group_name=student.group.name if student.group else None,
                total_days=stats.total_days,
                present_days=stats.present_days,
                absent_days=stats.absent_days,
                late_days=stats.late_days,
                excused_days=stats.excused_days,
                attendance_rate=stats.attendance_rate,
                total_late_minutes=total_late
            ))
        
        return summaries
    
    async def mark_absent_for_date(
        self,
        target_date: date,
        group_id: int,
        recorded_by: Optional[int] = None
    ) -> int:
        """Mark all students without attendance as absent for a date."""
        # Get students in group
        students_result = await self.db.execute(
            select(Student.id)
            .where(Student.group_id == group_id)
            .where(Student.is_active == True)
        )
        student_ids = [row[0] for row in students_result.all()]
        
        # Get students who already have attendance
        existing_result = await self.db.execute(
            select(Attendance.student_id)
            .where(Attendance.date == target_date)
            .where(Attendance.student_id.in_(student_ids))
        )
        existing_ids = {row[0] for row in existing_result.all()}
        
        # Mark absent for missing students
        count = 0
        for student_id in student_ids:
            if student_id not in existing_ids:
                attendance = Attendance(
                    student_id=student_id,
                    date=target_date,
                    status=AttendanceStatus.ABSENT,
                    recorded_by=recorded_by
                )
                self.db.add(attendance)
                count += 1
        
        await self.db.commit()
        return count
