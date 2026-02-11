"""
UniControl - Google Sheets Schedule Routes
===========================================
API endpoints for managing schedules via Google Sheets.
Super admin only.

Author: UniControl Team
Version: 1.0.0
"""

import logging
from typing import Optional, List
from datetime import time as dt_time

from fastapi import APIRouter, Depends, Query, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from app.database import get_db
from app.core.dependencies import require_superadmin
from app.models.user import User
from app.models.schedule import Schedule, WeekDay, ScheduleType
from app.models.group import Group

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Pydantic Models ==========

class CellUpdate(BaseModel):
    row: int
    col: int
    value: str


class BatchCellUpdate(BaseModel):
    sheet_name: str
    updates: List[CellUpdate]


class SyncRequest(BaseModel):
    sheet_name: str
    clear_existing: bool = True
    academic_year: str = "2025-2026"
    semester: int = 2


# ========== Endpoints ==========

@router.get("/summary")
async def get_sheets_summary(
    current_user: User = Depends(require_superadmin),
):
    """Get summary of all sheets in the spreadsheet."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.get_all_sheets_summary()
    except Exception as e:
        logger.error(f"Error getting sheets summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_sheets(
    current_user: User = Depends(require_superadmin),
):
    """List all sheet names."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.get_sheet_names()
    except Exception as e:
        logger.error(f"Error listing sheets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sheet/{sheet_name}")
async def get_sheet_data(
    sheet_name: str,
    current_user: User = Depends(require_superadmin),
):
    """Get parsed schedule data from a specific sheet."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.get_sheet_data(sheet_name)
    except Exception as e:
        logger.error(f"Error getting sheet data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sheet/{sheet_name}/raw")
async def get_sheet_raw(
    sheet_name: str,
    max_rows: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_superadmin),
):
    """Get raw sheet data as 2D array."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.get_sheet_raw(sheet_name, max_rows)
    except Exception as e:
        logger.error(f"Error getting raw sheet data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sheet/{sheet_name}/group/{group_name}")
async def get_group_schedule_from_sheet(
    sheet_name: str,
    group_name: str,
    current_user: User = Depends(require_superadmin),
):
    """Get schedule for a specific group from a sheet."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.get_group_schedule(sheet_name, group_name)
    except Exception as e:
        logger.error(f"Error getting group schedule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sheet/{sheet_name}/cell")
async def update_sheet_cell(
    sheet_name: str,
    row: int = Query(..., ge=1),
    col: int = Query(..., ge=1),
    value: str = Body(..., embed=True),
    current_user: User = Depends(require_superadmin),
):
    """Update a single cell in the sheet."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.update_cell(sheet_name, row, col, value)
    except Exception as e:
        logger.error(f"Error updating cell: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/sheet/batch-update")
async def batch_update_cells(
    data: BatchCellUpdate,
    current_user: User = Depends(require_superadmin),
):
    """Batch update multiple cells in a sheet."""
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()
        return service.update_cells_batch(
            data.sheet_name,
            [u.model_dump() for u in data.updates]
        )
    except Exception as e:
        logger.error(f"Error batch updating: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_sheet_to_db(
    data: SyncRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """
    Sync a sheet's schedule data to the database.
    Uses smart group name normalization to map sheet names → DB names.
    E.g. KI-25-09 (sheet) → KI_25-09 (DB)
    """
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()

        # Get all groups from DB
        groups_result = await db.execute(select(Group))
        db_groups_list = groups_result.scalars().all()
        db_groups = {g.name: g for g in db_groups_list}
        db_group_names = list(db_groups.keys())

        # Get parsed records WITH smart group name mapping
        sync_data = service.sync_to_database_with_mapping(data.sheet_name, db_group_names)
        records = sync_data["records"]
        group_name_map = sync_data.get("group_name_map", {})

        if not records:
            return {
                "success": True,
                "message": "No records to sync",
                "synced": 0,
                "skipped": 0,
            }

        # Map weekday strings to enum
        weekday_map = {
            "monday": WeekDay.MONDAY,
            "tuesday": WeekDay.TUESDAY,
            "wednesday": WeekDay.WEDNESDAY,
            "thursday": WeekDay.THURSDAY,
            "friday": WeekDay.FRIDAY,
            "saturday": WeekDay.SATURDAY,
            "sunday": WeekDay.SUNDAY,
        }

        type_map = {
            "lecture": ScheduleType.LECTURE,
            "practice": ScheduleType.PRACTICE,
            "seminar": ScheduleType.SEMINAR,
            "lab": ScheduleType.LAB,
        }

        synced = 0
        skipped = 0
        errors = []
        matched_groups = set()

        # Collect matched DB group names for clear_existing
        for sheet_gn, db_gn in group_name_map.items():
            matched_groups.add(db_gn)

        if data.clear_existing and matched_groups:
            group_ids = [db_groups[gn].id for gn in matched_groups if gn in db_groups]
            if group_ids:
                await db.execute(
                    delete(Schedule).where(
                        Schedule.group_id.in_(group_ids),
                        Schedule.academic_year == data.academic_year,
                        Schedule.semester == data.semester,
                    )
                )

        # Insert new records
        for rec in records:
            # Use the resolved DB group name from smart mapping
            db_group_name = rec.get("db_group_name")
            if not db_group_name or db_group_name not in db_groups:
                skipped += 1
                continue

            group = db_groups[db_group_name]
            day = weekday_map.get(rec["day_of_week"])
            stype = type_map.get(rec["schedule_type"], ScheduleType.LECTURE)

            if not day:
                skipped += 1
                continue

            try:
                start_time = None
                end_time = None
                if rec["start_time"]:
                    parts = rec["start_time"].split(":")
                    start_time = dt_time(int(parts[0]), int(parts[1]))
                if rec["end_time"]:
                    parts = rec["end_time"].split(":")
                    end_time = dt_time(int(parts[0]), int(parts[1]))

                if not start_time or not end_time:
                    ln = rec.get("lesson_number", 1)
                    from app.services.sheets_service import TIME_SLOTS
                    if ln in TIME_SLOTS:
                        st, et = TIME_SLOTS[ln]
                        start_time = dt_time(*[int(x) for x in st.split(":")])
                        end_time = dt_time(*[int(x) for x in et.split(":")])
                    else:
                        skipped += 1
                        continue

                schedule = Schedule(
                    group_id=group.id,
                    subject=rec["subject"],
                    schedule_type=stype,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time,
                    lesson_number=rec.get("lesson_number"),
                    room=rec.get("room"),
                    building=rec.get("building"),
                    teacher_name=rec.get("teacher_name"),
                    semester=data.semester,
                    academic_year=data.academic_year,
                    is_active=True,
                )
                db.add(schedule)
                synced += 1

            except Exception as e:
                errors.append(f"{rec.get('sheet_group_name', '?')}: {str(e)}")
                skipped += 1

        await db.commit()

        # Build human-readable mapping info
        sheet_groups_in_records = set(r.get("sheet_group_name", r["group_name"]) for r in records)
        unmatched = [sg for sg in sheet_groups_in_records if sg not in group_name_map]

        return {
            "success": True,
            "sheet_name": data.sheet_name,
            "faculty": sync_data["faculty"],
            "total_records": sync_data["total_records"],
            "synced": synced,
            "skipped": skipped,
            "matched_groups": list(matched_groups),
            "unmatched_groups": unmatched,
            "group_name_map": group_name_map,
            "errors": errors[:10],
        }

    except Exception as e:
        logger.error(f"Error syncing sheet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync-preview/{sheet_name}")
async def preview_sync(
    sheet_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """
    Preview what would be synced without actually writing to DB.
    Uses smart group name normalization to show matching status.
    E.g. KI-25-09 (sheet) → KI_25-09 (DB)
    """
    try:
        from app.services.sheets_service import SheetsService
        service = SheetsService()

        # Get all groups from DB
        groups_result = await db.execute(select(Group))
        db_groups_list = groups_result.scalars().all()
        db_groups = {g.name: g for g in db_groups_list}
        db_group_names = list(db_groups.keys())

        # Get parsed records WITH smart group name mapping
        sync_data = service.sync_to_database_with_mapping(sheet_name, db_group_names)
        group_name_map = sync_data.get("group_name_map", {})

        sheet_group_names = set(r.get("sheet_group_name", r["group_name"]) for r in sync_data["records"])
        matched = []
        unmatched = []

        for sheet_gn in sheet_group_names:
            db_gn = group_name_map.get(sheet_gn)
            if db_gn and db_gn in db_groups:
                g = db_groups[db_gn]
                matched.append({
                    "sheet_name": sheet_gn,
                    "db_name": db_gn,
                    "name": db_gn,
                    "id": g.id,
                    "renamed": sheet_gn != db_gn,
                })
            else:
                unmatched.append(sheet_gn)

        # Count per group (use sheet group names)
        per_group = {}
        for r in sync_data["records"]:
            gn = r.get("sheet_group_name", r["group_name"])
            per_group[gn] = per_group.get(gn, 0) + 1

        return {
            "sheet_name": sheet_name,
            "faculty": sync_data["faculty"],
            "total_records": sync_data["total_records"],
            "matched_groups": matched,
            "unmatched_groups": unmatched,
            "group_name_map": group_name_map,
            "records_per_group": per_group,
        }

    except Exception as e:
        logger.error(f"Error previewing sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/db-stats")
async def get_schedule_db_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Get schedule statistics from the database."""
    try:
        total_result = await db.execute(select(func.count(Schedule.id)))
        total = total_result.scalar() or 0

        active_result = await db.execute(
            select(func.count(Schedule.id)).where(Schedule.is_active == True)
        )
        active = active_result.scalar() or 0

        groups_result = await db.execute(
            select(func.count(func.distinct(Schedule.group_id)))
        )
        groups_with_schedule = groups_result.scalar() or 0

        return {
            "total_schedules": total,
            "active_schedules": active,
            "groups_with_schedule": groups_with_schedule,
        }

    except Exception as e:
        logger.error(f"Error getting DB stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
