"""
UniControl - Mobile Reports Routes
====================================
Report endpoints for mobile app.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from app.database import get_db
from app.models.report import Report, ReportType, ReportStatus
from app.models.user import User, UserRole
from app.models.group import Group
from app.core.dependencies import get_current_active_user, require_leader
from app.services.report_service import ReportService

router = APIRouter()


class MobileReportCreate(BaseModel):
    """Mobile report creation request."""
    name: str
    description: Optional[str] = None
    report_type: str = "attendance"
    group_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    content: Optional[str] = None


@router.get("")
async def get_reports(
    status_filter: Optional[str] = Query(None, alias="status"),
    group_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List reports for mobile."""
    service = ReportService(db)

    # Leader sees only own reports
    created_by_filter = (
        current_user.id if current_user.role == UserRole.LEADER else None
    )

    try:
        status_enum = ReportStatus(status_filter) if status_filter else None
    except (ValueError, KeyError):
        status_enum = None

    reports, total = await service.list_reports(
        page=page,
        page_size=page_size,
        status=status_enum,
        created_by=created_by_filter,
        group_id=group_id,
    )

    items = []
    for r in reports:
        try:
            group_name = r.group.name if r.group else None
        except Exception:
            group_name = None
        try:
            submitted_by_name = r.created_by_user.full_name if r.created_by_user else None
        except Exception:
            submitted_by_name = None

        items.append({
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "report_type": r.report_type.value if r.report_type else None,
            "status": r.status.value if r.status else "pending",
            "group_id": r.group_id,
            "group_name": group_name,
            "submitted_by": r.created_by,
            "submitted_by_name": submitted_by_name,
            "date": r.date_from.isoformat() if r.date_from else (r.created_at.date().isoformat() if r.created_at else None),
            "content": r.description,
            "present_count": 0,
            "absent_count": 0,
            "late_count": 0,
            "excused_count": 0,
            "total_count": 0,
            "approved_by": r.approved_by,
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "rejection_reason": r.rejection_reason,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("")
async def create_report(
    data: MobileReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """Create a report from mobile."""
    service = ReportService(db)

    try:
        report_type = ReportType(data.report_type)
    except (ValueError, KeyError):
        report_type = ReportType.ATTENDANCE

    # For leader, auto-assign their group
    group_id = data.group_id
    if current_user.role == UserRole.LEADER and not group_id:
        group_res = await db.execute(
            select(Group).where(Group.leader_id == current_user.id)
        )
        group = group_res.scalar_one_or_none()
        if group:
            group_id = group.id

    from app.schemas.report import ReportCreate as SchemaReportCreate
    report = await service.create_report(
        SchemaReportCreate(
            name=data.name,
            description=data.description,
            report_type=report_type,
            group_id=group_id,
            date_from=data.date_from,
            date_to=data.date_to,
        ),
        user_id=current_user.id,
    )

    return {
        "id": report.id,
        "name": report.name,
        "status": report.status.value if report.status else "pending",
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "message": "Hisobot yaratildi",
    }


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get report detail."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Hisobot topilmadi")

    # Leader can only see own reports
    if current_user.role == UserRole.LEADER and report.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    try:
        group_name = report.group.name if report.group else None
    except Exception:
        group_name = None

    return {
        "id": report.id,
        "name": report.name,
        "description": report.description,
        "report_type": report.report_type.value if report.report_type else None,
        "status": report.status.value if report.status else "pending",
        "group_id": report.group_id,
        "group_name": group_name,
        "date_from": report.date_from.isoformat() if report.date_from else None,
        "date_to": report.date_to.isoformat() if report.date_to else None,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }
