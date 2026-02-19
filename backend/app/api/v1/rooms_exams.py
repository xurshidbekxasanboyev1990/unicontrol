"""
UniControl - Rooms & Exam Schedule API
========================================
API endpoints for room management and exam schedule.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional, List
from datetime import date, time
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, distinct, delete
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.room import Room
from app.models.exam_schedule import ExamSchedule
from app.models.group import Group
from app.models.student import Student
from app.models.subject import Subject, Direction
from app.models.schedule import Schedule, WeekDay
from app.core.dependencies import get_current_active_user

router = APIRouter()


# ============================================
# Dependencies
# ============================================

async def require_academic(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Require academic_affairs, admin, or superadmin role."""
    if current_user.role not in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.ACADEMIC_AFFAIRS]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akademik ishlar paneli uchun ruxsat yo'q"
        )
    return current_user


# ============================================
# Pydantic Schemas
# ============================================

class RoomCreate(BaseModel):
    name: str
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: int = 30
    room_type: str = "lecture"
    has_projector: bool = False
    has_computer: bool = False
    has_whiteboard: bool = True
    has_air_conditioner: bool = False
    description: Optional[str] = None

class RoomUpdate(BaseModel):
    name: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    room_type: Optional[str] = None
    has_projector: Optional[bool] = None
    has_computer: Optional[bool] = None
    has_whiteboard: Optional[bool] = None
    has_air_conditioner: Optional[bool] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class ExamCreate(BaseModel):
    group_id: int
    subject: str
    exam_type: str = "exam"
    exam_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    room: Optional[str] = None
    building: Optional[str] = None
    teacher_name: Optional[str] = None
    teacher_id: Optional[int] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    max_students: Optional[int] = None
    notes: Optional[str] = None

class ExamUpdate(BaseModel):
    subject: Optional[str] = None
    exam_type: Optional[str] = None
    exam_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    room: Optional[str] = None
    building: Optional[str] = None
    teacher_name: Optional[str] = None
    teacher_id: Optional[int] = None
    semester: Optional[int] = None
    academic_year: Optional[str] = None
    max_students: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================
# Helpers
# ============================================

def _parse_time(t_str: str) -> time:
    parts = t_str.strip().split(":")
    return time(int(parts[0]), int(parts[1]))

def _parse_date(d_str: str) -> date:
    return date.fromisoformat(d_str)


# ============================================
# ROOMS API
# ============================================

@router.get("/rooms")
async def get_rooms(
    building: Optional[str] = None,
    room_type: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get all rooms with optional filters."""
    query = select(Room).where(Room.is_active == True)
    
    if building:
        query = query.where(Room.building.ilike(f"%{building}%"))
    if room_type:
        query = query.where(Room.room_type == room_type)
    if search:
        query = query.where(Room.name.ilike(f"%{search}%"))
    
    query = query.order_by(Room.building, Room.name)
    result = await db.execute(query)
    rooms = result.scalars().all()
    
    items = []
    for r in rooms:
        items.append({
            "id": r.id,
            "name": r.name,
            "building": r.building,
            "floor": r.floor,
            "capacity": r.capacity,
            "room_type": r.room_type,
            "has_projector": r.has_projector,
            "has_computer": r.has_computer,
            "has_whiteboard": r.has_whiteboard,
            "has_air_conditioner": r.has_air_conditioner,
            "description": r.description,
            "full_name": r.full_name,
        })
    
    # Get buildings list
    buildings_result = await db.execute(
        select(distinct(Room.building))
        .where(and_(Room.is_active == True, Room.building.isnot(None)))
        .order_by(Room.building)
    )
    buildings = [row[0] for row in buildings_result.all() if row[0]]
    
    return {"items": items, "total": len(items), "buildings": buildings}


@router.get("/rooms/occupancy")
async def get_rooms_occupancy(
    day: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get room occupancy — which rooms are busy on which day/time."""
    # Get all active rooms
    rooms_result = await db.execute(
        select(Room).where(Room.is_active == True).order_by(Room.building, Room.name)
    )
    rooms = rooms_result.scalars().all()
    
    # Get schedule entries that use rooms
    schedule_query = select(Schedule).where(
        and_(Schedule.is_active == True, Schedule.room.isnot(None))
    )
    if day:
        try:
            weekday = WeekDay(day)
            schedule_query = schedule_query.where(Schedule.day_of_week == weekday)
        except ValueError:
            pass
    
    schedules_result = await db.execute(schedule_query)
    schedules = schedules_result.scalars().all()
    
    # Build occupancy map: room_name -> list of schedule slots
    from collections import defaultdict
    occupancy = defaultdict(list)
    for s in schedules:
        room_key = (s.room or "").strip().lower()
        if room_key:
            occupancy[room_key].append({
                "day": s.day_of_week.value if s.day_of_week else None,
                "lesson_number": s.lesson_number,
                "start_time": s.start_time.strftime("%H:%M") if s.start_time else None,
                "end_time": s.end_time.strftime("%H:%M") if s.end_time else None,
                "subject": s.subject,
                "group_name": s.group_name,
                "teacher_name": s.teacher_name,
            })
    
    items = []
    for r in rooms:
        room_key = r.name.strip().lower()
        slots = occupancy.get(room_key, [])
        busy_count = len(slots)
        # Max 42 slots per week (7 days * 6 paras)
        total_slots = 36  # 6 days * 6 paras
        occupancy_rate = round(busy_count / total_slots * 100, 1) if total_slots > 0 else 0
        
        items.append({
            "id": r.id,
            "name": r.name,
            "building": r.building,
            "capacity": r.capacity,
            "room_type": r.room_type,
            "full_name": r.full_name,
            "busy_slots": busy_count,
            "occupancy_rate": occupancy_rate,
            "schedule": slots,
        })
    
    return {"items": items, "total": len(items)}


@router.get("/rooms/{room_id}")
async def get_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get single room details."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Xona topilmadi")
    
    return {
        "id": room.id,
        "name": room.name,
        "building": room.building,
        "floor": room.floor,
        "capacity": room.capacity,
        "room_type": room.room_type,
        "has_projector": room.has_projector,
        "has_computer": room.has_computer,
        "has_whiteboard": room.has_whiteboard,
        "has_air_conditioner": room.has_air_conditioner,
        "description": room.description,
        "is_active": room.is_active,
    }


@router.post("/rooms")
async def create_room(
    data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Create a new room."""
    room = Room(
        name=data.name,
        building=data.building,
        floor=data.floor,
        capacity=data.capacity,
        room_type=data.room_type,
        has_projector=data.has_projector,
        has_computer=data.has_computer,
        has_whiteboard=data.has_whiteboard,
        has_air_conditioner=data.has_air_conditioner,
        description=data.description,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)
    
    return {
        "success": True,
        "message": "Xona yaratildi",
        "room": {
            "id": room.id,
            "name": room.name,
            "building": room.building,
            "full_name": room.full_name,
        }
    }


@router.put("/rooms/{room_id}")
async def update_room(
    room_id: int,
    data: RoomUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Update a room."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Xona topilmadi")
    
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    
    await db.commit()
    await db.refresh(room)
    
    return {"success": True, "message": "Xona yangilandi"}


@router.delete("/rooms/{room_id}")
async def delete_room(
    room_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Delete (deactivate) a room."""
    result = await db.execute(select(Room).where(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Xona topilmadi")
    
    room.is_active = False
    await db.commit()
    
    return {"success": True, "message": "Xona o'chirildi"}


@router.get("/rooms/stats/summary")
async def rooms_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get rooms statistics summary."""
    total = await db.execute(
        select(func.count(Room.id)).where(Room.is_active == True)
    )
    total_rooms = total.scalar() or 0
    
    total_capacity = await db.execute(
        select(func.sum(Room.capacity)).where(Room.is_active == True)
    )
    capacity = total_capacity.scalar() or 0
    
    # Room types count
    types_result = await db.execute(
        select(Room.room_type, func.count(Room.id))
        .where(Room.is_active == True)
        .group_by(Room.room_type)
    )
    types = {row[0]: row[1] for row in types_result.all()}
    
    # Buildings count
    buildings = await db.execute(
        select(func.count(distinct(Room.building)))
        .where(and_(Room.is_active == True, Room.building.isnot(None)))
    )
    total_buildings = buildings.scalar() or 0
    
    return {
        "total_rooms": total_rooms,
        "total_capacity": capacity,
        "total_buildings": total_buildings,
        "room_types": types,
    }


# ============================================
# EXAM SCHEDULE API
# ============================================

@router.get("/exams")
async def get_exam_schedules(
    group_id: Optional[int] = None,
    exam_type: Optional[str] = None,
    semester: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get exam schedules with filters."""
    query = select(ExamSchedule).where(ExamSchedule.is_active == True)
    
    if group_id:
        query = query.where(ExamSchedule.group_id == group_id)
    if exam_type:
        query = query.where(ExamSchedule.exam_type == exam_type)
    if semester:
        query = query.where(ExamSchedule.semester == semester)
    if date_from:
        query = query.where(ExamSchedule.exam_date >= _parse_date(date_from))
    if date_to:
        query = query.where(ExamSchedule.exam_date <= _parse_date(date_to))
    
    query = query.order_by(ExamSchedule.exam_date, ExamSchedule.start_time)
    result = await db.execute(query)
    exams = result.unique().scalars().all()
    
    items = []
    for e in exams:
        items.append({
            "id": e.id,
            "group_id": e.group_id,
            "group_name": e.group_name,
            "subject": e.subject,
            "exam_type": e.exam_type,
            "exam_date": str(e.exam_date),
            "start_time": e.start_time.strftime("%H:%M") if e.start_time else None,
            "end_time": e.end_time.strftime("%H:%M") if e.end_time else None,
            "time_range": e.time_range,
            "room": e.room,
            "building": e.building,
            "teacher_name": e.teacher_name,
            "teacher_id": e.teacher_id,
            "semester": e.semester,
            "academic_year": e.academic_year,
            "max_students": e.max_students,
            "notes": e.notes,
        })
    
    return {"items": items, "total": len(items)}


@router.get("/exams/stats")
async def exam_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get exam schedule statistics."""
    total = await db.execute(
        select(func.count(ExamSchedule.id)).where(ExamSchedule.is_active == True)
    )
    total_exams = total.scalar() or 0
    
    groups_count = await db.execute(
        select(func.count(distinct(ExamSchedule.group_id))).where(ExamSchedule.is_active == True)
    )
    total_groups = groups_count.scalar() or 0
    
    subjects_count = await db.execute(
        select(func.count(distinct(ExamSchedule.subject))).where(ExamSchedule.is_active == True)
    )
    total_subjects = subjects_count.scalar() or 0
    
    # Upcoming exams (next 7 days)
    from app.config import today_tashkent
    from datetime import timedelta
    today = today_tashkent()
    upcoming = await db.execute(
        select(func.count(ExamSchedule.id)).where(
            and_(
                ExamSchedule.is_active == True,
                ExamSchedule.exam_date >= today,
                ExamSchedule.exam_date <= today + timedelta(days=7)
            )
        )
    )
    upcoming_count = upcoming.scalar() or 0
    
    return {
        "total_exams": total_exams,
        "total_groups": total_groups,
        "total_subjects": total_subjects,
        "upcoming_exams": upcoming_count,
    }


@router.post("/exams")
async def create_exam(
    data: ExamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Create a new exam schedule entry."""
    # Verify group exists
    group = await db.execute(select(Group).where(Group.id == data.group_id))
    if not group.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Guruh topilmadi")
    
    exam = ExamSchedule(
        group_id=data.group_id,
        subject=data.subject,
        exam_type=data.exam_type,
        exam_date=_parse_date(data.exam_date),
        start_time=_parse_time(data.start_time),
        end_time=_parse_time(data.end_time),
        room=data.room,
        building=data.building,
        teacher_name=data.teacher_name,
        teacher_id=data.teacher_id,
        semester=data.semester,
        academic_year=data.academic_year,
        max_students=data.max_students,
        notes=data.notes,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    
    return {
        "success": True,
        "message": "Imtihon jadvali yaratildi",
        "exam": {
            "id": exam.id,
            "subject": exam.subject,
            "exam_date": str(exam.exam_date),
        }
    }


@router.post("/exams/bulk")
async def create_exams_bulk(
    data: List[ExamCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Create multiple exam schedules at once."""
    created = 0
    for item in data:
        exam = ExamSchedule(
            group_id=item.group_id,
            subject=item.subject,
            exam_type=item.exam_type,
            exam_date=_parse_date(item.exam_date),
            start_time=_parse_time(item.start_time),
            end_time=_parse_time(item.end_time),
            room=item.room,
            building=item.building,
            teacher_name=item.teacher_name,
            teacher_id=item.teacher_id,
            semester=item.semester,
            academic_year=item.academic_year,
            max_students=item.max_students,
            notes=item.notes,
        )
        db.add(exam)
        created += 1
    
    await db.commit()
    return {"success": True, "message": f"{created} ta imtihon yaratildi", "created": created}


@router.put("/exams/{exam_id}")
async def update_exam(
    exam_id: int,
    data: ExamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Update an exam schedule entry."""
    result = await db.execute(select(ExamSchedule).where(ExamSchedule.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    
    update_data = data.model_dump(exclude_unset=True)
    
    if "exam_date" in update_data and update_data["exam_date"]:
        update_data["exam_date"] = _parse_date(update_data["exam_date"])
    if "start_time" in update_data and update_data["start_time"]:
        update_data["start_time"] = _parse_time(update_data["start_time"])
    if "end_time" in update_data and update_data["end_time"]:
        update_data["end_time"] = _parse_time(update_data["end_time"])
    
    for field, value in update_data.items():
        setattr(exam, field, value)
    
    await db.commit()
    return {"success": True, "message": "Imtihon yangilandi"}


@router.delete("/exams/{exam_id}")
async def delete_exam(
    exam_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Delete an exam schedule entry."""
    result = await db.execute(select(ExamSchedule).where(ExamSchedule.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Imtihon topilmadi")
    
    await db.delete(exam)
    await db.commit()
    
    return {"success": True, "message": "Imtihon o'chirildi"}


@router.delete("/exams/group/{group_id}")
async def delete_group_exams(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Delete all exam schedules for a group."""
    await db.execute(
        delete(ExamSchedule).where(ExamSchedule.group_id == group_id)
    )
    await db.commit()
    return {"success": True, "message": "Guruh imtihonlari o'chirildi"}


@router.get("/exams/groups")
async def get_exam_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get all groups that have exams scheduled."""
    result = await db.execute(
        select(Group)
        .where(Group.is_active == True)
        .order_by(Group.name)
    )
    groups = result.scalars().all()
    
    # Get exam counts per group
    exam_counts = await db.execute(
        select(ExamSchedule.group_id, func.count(ExamSchedule.id))
        .where(ExamSchedule.is_active == True)
        .group_by(ExamSchedule.group_id)
    )
    counts_map = {row[0]: row[1] for row in exam_counts.all()}
    
    items = []
    for g in groups:
        items.append({
            "id": g.id,
            "name": g.name,
            "faculty": g.faculty,
            "course_year": g.course_year,
            "exam_count": counts_map.get(g.id, 0),
        })
    
    return {"items": items, "total": len(items)}


# ============================================
# HIERARCHY: Directions → Faculties → Groups
# ============================================

@router.get("/exams/directions")
async def get_directions_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get all directions (yo'nalishlar) for exam assignment."""
    result = await db.execute(
        select(Direction).where(Direction.is_active == True).order_by(Direction.name)
    )
    directions = result.scalars().all()
    items = [{"id": d.id, "name": d.name, "code": d.code} for d in directions]
    return {"items": items, "total": len(items)}


@router.get("/exams/faculties")
async def get_faculties_list(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get all unique faculties from groups."""
    result = await db.execute(
        select(distinct(Group.faculty))
        .where(and_(Group.is_active == True, Group.faculty.isnot(None)))
        .order_by(Group.faculty)
    )
    faculties = [row[0] for row in result.all() if row[0]]
    
    # Get group counts per faculty
    counts_result = await db.execute(
        select(Group.faculty, func.count(Group.id))
        .where(and_(Group.is_active == True, Group.faculty.isnot(None)))
        .group_by(Group.faculty)
    )
    counts = {row[0]: row[1] for row in counts_result.all()}
    
    items = [{"name": f, "group_count": counts.get(f, 0)} for f in faculties]
    return {"items": items, "total": len(items)}


@router.get("/exams/faculty-groups")
async def get_faculty_groups(
    faculty: str = Query(..., description="Faculty name"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """Get groups filtered by faculty, with exam count."""
    result = await db.execute(
        select(Group)
        .where(and_(Group.is_active == True, Group.faculty == faculty))
        .order_by(Group.course_year, Group.name)
    )
    groups = result.scalars().all()
    
    # Get exam counts per group
    group_ids = [g.id for g in groups]
    exam_counts = {}
    if group_ids:
        ec_result = await db.execute(
            select(ExamSchedule.group_id, func.count(ExamSchedule.id))
            .where(and_(ExamSchedule.is_active == True, ExamSchedule.group_id.in_(group_ids)))
            .group_by(ExamSchedule.group_id)
        )
        exam_counts = {row[0]: row[1] for row in ec_result.all()}
    
    items = [{
        "id": g.id,
        "name": g.name,
        "faculty": g.faculty,
        "course_year": g.course_year,
        "exam_count": exam_counts.get(g.id, 0),
    } for g in groups]
    
    return {"items": items, "total": len(items)}


@router.post("/exams/assign-groups")
async def assign_exams_to_groups(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_academic)
):
    """
    Assign exam to multiple groups at once.
    Body: { group_ids: [1,2,3], subject, exam_type, exam_date, start_time, end_time, room, building, teacher_name, semester, notes }
    """
    group_ids = data.get("group_ids", [])
    if not group_ids:
        raise HTTPException(status_code=400, detail="Guruhlar tanlanmagan")
    
    subject = data.get("subject", "")
    if not subject:
        raise HTTPException(status_code=400, detail="Fan nomi kiritilmagan")
    
    exam_date = data.get("exam_date", "")
    start_time = data.get("start_time", "09:00")
    end_time = data.get("end_time", "11:00")
    
    if not exam_date:
        raise HTTPException(status_code=400, detail="Sana kiritilmagan")
    
    created = 0
    for gid in group_ids:
        # Verify group exists
        g_result = await db.execute(select(Group).where(Group.id == gid))
        if not g_result.scalar_one_or_none():
            continue
        
        exam = ExamSchedule(
            group_id=gid,
            subject=subject,
            exam_type=data.get("exam_type", "exam"),
            exam_date=_parse_date(exam_date),
            start_time=_parse_time(start_time),
            end_time=_parse_time(end_time),
            room=data.get("room"),
            building=data.get("building"),
            teacher_name=data.get("teacher_name"),
            semester=data.get("semester"),
            academic_year=data.get("academic_year"),
            notes=data.get("notes"),
        )
        db.add(exam)
        created += 1
    
    await db.commit()
    return {"success": True, "message": f"{created} ta guruhga imtihon tayinlandi", "created": created}


# ============================================
# PUBLIC EXAM SCHEDULE (for students & leaders)
# ============================================

@router.get("/my-exams")
async def get_my_exam_schedule(
    exam_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get exam schedule for the currently logged-in student/leader.
    Finds the user's group automatically and returns only their exams.
    Admin/academic roles get all exams.
    """
    group_id = None
    group_name = None

    # For admin/academic roles, return all exams
    if current_user.role in [UserRole.SUPERADMIN, UserRole.ADMIN, UserRole.ACADEMIC_AFFAIRS]:
        pass  # no group filter
    else:
        # Find student record by user_id or login
        student_result = await db.execute(
            select(Student).where(
                (Student.user_id == current_user.id) |
                (Student.student_id == current_user.login)
            )
        )
        student = student_result.scalar_one_or_none()

        if student and student.group_id:
            group_id = student.group_id
        else:
            # Check if user is a leader of a group
            leader_result = await db.execute(
                select(Group).where(Group.leader_id == (student.id if student else 0))
            )
            leader_group = leader_result.scalar_one_or_none()
            if leader_group:
                group_id = leader_group.id
            else:
                return {"items": [], "total": 0, "group_name": None, "stats": {
                    "total_exams": 0, "upcoming_exams": 0, "subjects": 0
                }}

    # Build query
    query = select(ExamSchedule).where(ExamSchedule.is_active == True)
    if group_id:
        query = query.where(ExamSchedule.group_id == group_id)
    if exam_type:
        query = query.where(ExamSchedule.exam_type == exam_type)
    if date_from:
        query = query.where(ExamSchedule.exam_date >= _parse_date(date_from))
    if date_to:
        query = query.where(ExamSchedule.exam_date <= _parse_date(date_to))

    query = query.order_by(ExamSchedule.exam_date, ExamSchedule.start_time)
    result = await db.execute(query)
    exams = result.unique().scalars().all()

    items = []
    for e in exams:
        items.append({
            "id": e.id,
            "group_id": e.group_id,
            "group_name": e.group_name,
            "subject": e.subject,
            "exam_type": e.exam_type,
            "exam_date": str(e.exam_date),
            "start_time": e.start_time.strftime("%H:%M") if e.start_time else None,
            "end_time": e.end_time.strftime("%H:%M") if e.end_time else None,
            "time_range": e.time_range,
            "room": e.room,
            "building": e.building,
            "teacher_name": e.teacher_name,
            "semester": e.semester,
            "notes": e.notes,
        })

    # Get group name
    if group_id:
        grp = await db.execute(select(Group).where(Group.id == group_id))
        g = grp.scalar_one_or_none()
        group_name = g.name if g else None

    # Stats
    from datetime import timedelta
    from app.config import today_tashkent
    today = today_tashkent()
    total_exams = len(items)
    upcoming_exams = sum(1 for e in items if e["exam_date"] and _parse_date(e["exam_date"]) >= today and _parse_date(e["exam_date"]) <= today + timedelta(days=7))
    subjects = len(set(e["subject"] for e in items))

    return {
        "items": items,
        "total": total_exams,
        "group_name": group_name,
        "stats": {
            "total_exams": total_exams,
            "upcoming_exams": upcoming_exams,
            "subjects": subjects,
        }
    }
