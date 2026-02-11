"""
UniControl - Schedule Service
=============================
Handles schedule management operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date, time, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload

from app.models.schedule import Schedule, WeekDay, ScheduleType
from app.models.group import Group
from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleUpdate,
    WeekSchedule,
    DaySchedule,
    ScheduleResponse,
)
from app.core.exceptions import NotFoundException, ConflictException
from app.config import today_tashkent


class ScheduleService:
    """Schedule management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, schedule_id: int) -> Optional[Schedule]:
        """Get schedule by ID."""
        result = await self.db.execute(
            select(Schedule)
            .options(joinedload(Schedule.group), joinedload(Schedule.teacher))
            .where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    async def list_schedules(
        self,
        page: int = 1,
        page_size: int = 50,
        group_id: Optional[int] = None,
        day_of_week: Optional[WeekDay] = None,
        is_active: Optional[bool] = True,
        semester: Optional[int] = None,
        academic_year: Optional[str] = None
    ) -> Tuple[List[Schedule], int]:
        """List schedules with pagination and filters."""
        query = select(Schedule).options(joinedload(Schedule.group))
        count_query = select(func.count(Schedule.id))
        
        if group_id:
            query = query.where(Schedule.group_id == group_id)
            count_query = count_query.where(Schedule.group_id == group_id)
        
        if day_of_week:
            query = query.where(Schedule.day_of_week == day_of_week)
            count_query = count_query.where(Schedule.day_of_week == day_of_week)
        
        if is_active is not None:
            query = query.where(Schedule.is_active == is_active)
            count_query = count_query.where(Schedule.is_active == is_active)
        
        if semester:
            query = query.where(Schedule.semester == semester)
            count_query = count_query.where(Schedule.semester == semester)
        
        if academic_year:
            query = query.where(Schedule.academic_year == academic_year)
            count_query = count_query.where(Schedule.academic_year == academic_year)
        
        # Get total
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Order by day and time
        query = query.order_by(Schedule.day_of_week, Schedule.start_time)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        schedules = result.unique().scalars().all()
        
        return list(schedules), total
    
    async def create(self, schedule_data: ScheduleCreate) -> Schedule:
        """Create schedule."""
        # Verify group exists
        group_result = await self.db.execute(
            select(Group).where(Group.id == schedule_data.group_id)
        )
        if not group_result.scalar_one_or_none():
            raise NotFoundException("Group not found")
        
        # Check for time conflicts
        await self._check_time_conflict(schedule_data)
        
        schedule = Schedule(**schedule_data.model_dump())
        
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def update(
        self,
        schedule_id: int,
        schedule_data: ScheduleUpdate
    ) -> Schedule:
        """Update schedule."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Schedule not found")
        
        # Check for time conflicts if time is changing
        if schedule_data.start_time or schedule_data.end_time or schedule_data.day_of_week:
            # Build a schedule-like object for conflict check
            check_data = ScheduleCreate(
                group_id=schedule.group_id,
                subject=schedule.subject,
                start_time=schedule_data.start_time or schedule.start_time,
                end_time=schedule_data.end_time or schedule.end_time,
                day_of_week=schedule_data.day_of_week or schedule.day_of_week,
            )
            await self._check_time_conflict(check_data, exclude_id=schedule_id)
        
        update_data = schedule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def delete(self, schedule_id: int) -> bool:
        """Delete schedule."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Schedule not found")
        
        await self.db.delete(schedule)
        await self.db.commit()
        
        return True
    
    async def _check_time_conflict(
        self,
        schedule_data: ScheduleCreate,
        exclude_id: Optional[int] = None
    ) -> None:
        """Check for time conflicts."""
        query = select(Schedule).where(
            and_(
                Schedule.group_id == schedule_data.group_id,
                Schedule.day_of_week == schedule_data.day_of_week,
                Schedule.is_active == True,
                or_(
                    # New schedule starts during existing
                    and_(
                        Schedule.start_time <= schedule_data.start_time,
                        Schedule.end_time > schedule_data.start_time
                    ),
                    # New schedule ends during existing
                    and_(
                        Schedule.start_time < schedule_data.end_time,
                        Schedule.end_time >= schedule_data.end_time
                    ),
                    # New schedule contains existing
                    and_(
                        Schedule.start_time >= schedule_data.start_time,
                        Schedule.end_time <= schedule_data.end_time
                    )
                )
            )
        )
        
        if exclude_id:
            query = query.where(Schedule.id != exclude_id)
        
        result = await self.db.execute(query)
        conflict = result.scalar_one_or_none()
        
        if conflict:
            raise ConflictException(
                f"Time conflict with existing schedule: {conflict.subject} "
                f"({conflict.start_time.strftime('%H:%M')} - {conflict.end_time.strftime('%H:%M')})"
            )
    
    async def get_group_week_schedule(
        self,
        group_id: int,
        semester: Optional[int] = None
    ) -> WeekSchedule:
        """Get weekly schedule for a group."""
        query = select(Schedule).where(
            and_(
                Schedule.group_id == group_id,
                Schedule.is_active == True,
                Schedule.day_of_week.isnot(None)
            )
        )
        
        if semester:
            query = query.where(Schedule.semester == semester)
        
        query = query.order_by(Schedule.start_time)
        
        result = await self.db.execute(query)
        schedules = result.scalars().all()
        
        week = WeekSchedule()
        
        for schedule in schedules:
            day_name = schedule.day_of_week.value.lower()
            day_list = getattr(week, day_name)
            day_list.append(ScheduleResponse.model_validate(schedule))
        
        return week
    
    async def get_day_schedule(
        self,
        group_id: int,
        target_date: date
    ) -> DaySchedule:
        """Get schedule for a specific day."""
        day_of_week = WeekDay(target_date.strftime("%A").lower())
        
        # Get recurring schedules for this day
        query = select(Schedule).where(
            and_(
                Schedule.group_id == group_id,
                Schedule.is_active == True,
                or_(
                    Schedule.day_of_week == day_of_week,
                    Schedule.specific_date == target_date
                )
            )
        ).order_by(Schedule.start_time)
        
        result = await self.db.execute(query)
        schedules = result.scalars().all()
        
        return DaySchedule(
            date=target_date,
            day_of_week=day_of_week,
            schedules=[ScheduleResponse.model_validate(s) for s in schedules]
        )
    
    async def cancel_schedule(
        self,
        schedule_id: int,
        reason: str
    ) -> Schedule:
        """Cancel a schedule."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Schedule not found")
        
        schedule.is_cancelled = True
        schedule.cancellation_reason = reason
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def restore_schedule(self, schedule_id: int) -> Schedule:
        """Restore a cancelled schedule."""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundException("Schedule not found")
        
        schedule.is_cancelled = False
        schedule.cancellation_reason = None
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def get_today_schedules(
        self,
        group_id: Optional[int] = None
    ) -> List[Schedule]:
        """Get today's schedules."""
        today = today_tashkent()
        day_of_week = WeekDay(today.strftime("%A").lower())
        
        query = select(Schedule).where(
            and_(
                Schedule.is_active == True,
                Schedule.is_cancelled == False,
                or_(
                    Schedule.day_of_week == day_of_week,
                    Schedule.specific_date == today
                )
            )
        )
        
        if group_id:
            query = query.where(Schedule.group_id == group_id)
        
        query = query.order_by(Schedule.start_time)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def bulk_create(
        self,
        schedules_data: List[ScheduleCreate]
    ) -> Tuple[int, int, List[str]]:
        """Bulk create schedules."""
        created = 0
        skipped = 0
        errors = []
        
        for data in schedules_data:
            try:
                await self.create(data)
                created += 1
            except Exception as e:
                skipped += 1
                errors.append(f"{data.subject}: {str(e)}")
        
        return created, skipped, errors
