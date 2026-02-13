"""
UniControl - Report Routes
==========================
Report management endpoints.

Role-based permissions:
- Leader: CRUD own reports only, view own group stats
- Admin: View/approve/reject all reports, delete, faculty-wide stats
- Superadmin: Full access, system-wide stats, all report types

Author: UniControl Team
Version: 2.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import io

from app.database import get_db
from app.services.report_service import ReportService
from app.schemas.report import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportListResponse,
    ReportGenerate,
)
from app.models.report import ReportType, ReportStatus
from app.models.user import User, UserRole
from app.core.dependencies import (
    get_current_active_user,
    require_admin,
    require_leader,
    require_superadmin,
)
from app.core.exceptions import ForbiddenException, NotFoundException

router = APIRouter()


# ──────────────────────────────────────────────
# Helper: build ReportResponse with related names
# ──────────────────────────────────────────────
def _build_response(report) -> ReportResponse:
    """Build ReportResponse with computed fields from relationships."""
    # Safe access to relationships (may not be loaded in async context)
    try:
        group_name = report.group.name if report.group else None
    except Exception as e:
        logger.debug(f"Could not access report.group: {e}")
        group_name = None
    try:
        created_by_name = report.created_by_user.full_name if report.created_by_user else None
    except Exception as e:
        logger.debug(f"Could not access report.created_by_user: {e}")
        created_by_name = None
    try:
        approved_by_name = report.approved_by_user.full_name if report.approved_by_user else None
    except Exception as e:
        logger.debug(f"Could not access report.approved_by_user: {e}")
        approved_by_name = None

    data = {
        "id": report.id,
        "name": report.name,
        "description": report.description,
        "report_type": report.report_type,
        "format": report.format,
        "status": report.status,
        "date_from": report.date_from,
        "date_to": report.date_to,
        "group_id": report.group_id,
        "group_name": group_name,
        "filters": report.filters,
        "created_by": report.created_by,
        "created_by_name": created_by_name,
        "file_path": report.file_path,
        "file_size": report.file_size,
        "download_url": report.download_url,
        "started_at": report.started_at,
        "completed_at": report.completed_at,
        "processing_time": report.processing_time,
        "error_message": report.error_message,
        "ai_result": report.ai_result,
        "download_count": report.download_count,
        "approved_by": report.approved_by,
        "approved_by_name": approved_by_name,
        "approved_at": report.approved_at,
        "rejection_reason": report.rejection_reason,
        "expires_at": report.expires_at,
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }
    return ReportResponse(**data)


# ──────────────────────────────────────────────
# Helper: ownership check
# ──────────────────────────────────────────────
def _check_report_access(report, user: User, *, write: bool = False):
    """
    Check whether *user* can access *report*.
    
    Read access:
      - leader  → only own reports (created_by == user.id)
      - admin / superadmin → all reports
    Write (update) access:
      - leader  → only own + status must be draft/pending
      - admin   → any report
      - superadmin → any report
    """
    if user.role == UserRole.LEADER:
        if report.created_by != user.id:
            raise ForbiddenException("Bu hisobotga kirishga ruxsat yo'q")
        if write and report.status not in (
            ReportStatus.PENDING,
            ReportStatus.FAILED,
        ):
            # Leader faqat pending/failed statusdagi o'z hisobotlarini tahrirlash mumkin
            raise ForbiddenException(
                "Faqat kutilayotgan yoki xato hisobotlarni tahrirlash mumkin"
            )


# ──────────────────────────────────────────────
# LIST
# ──────────────────────────────────────────────
@router.get("", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: Optional[ReportType] = None,
    report_status: Optional[ReportStatus] = None,
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    List reports.

    - **Leader**: only own reports
    - **Admin**: all reports (optionally filtered by group)
    - **Superadmin**: all reports (no restrictions)
    """
    service = ReportService(db)

    # Leader faqat o'zining hisobotlarini ko'radi
    created_by_filter = (
        current_user.id if current_user.role == UserRole.LEADER else None
    )

    reports, total = await service.list_reports(
        page=page,
        page_size=page_size,
        report_type=report_type,
        status=report_status,
        created_by=created_by_filter,
        group_id=group_id,
    )

    return ReportListResponse(
        items=[_build_response(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


# ──────────────────────────────────────────────
# CREATE
# ──────────────────────────────────────────────
@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Create a new report.
    
    - **Leader**: can create for own group only
    - **Admin/Superadmin**: can create for any group
    """
    service = ReportService(db)

    # Leader uchun hisobot turini cheklash
    leader_allowed_types = {
        ReportType.ATTENDANCE,
        ReportType.PAYMENT,
        ReportType.STUDENTS,
        ReportType.CUSTOM,
    }
    if (
        current_user.role == UserRole.LEADER
        and report_data.report_type not in leader_allowed_types
    ):
        raise ForbiddenException(
            f"Leader faqat {[t.value for t in leader_allowed_types]} turidagi hisobotlarni yarata oladi"
        )

    report = await service.create(report_data, current_user.id)
    logger.info(
        f"Report created: id={report.id} by user={current_user.id} ({current_user.role.value})"
    )
    return _build_response(report)


# ──────────────────────────────────────────────
# GENERATE (server-side report generation)
# ──────────────────────────────────────────────
@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    data: ReportGenerate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Generate a report.
    
    - Leader can generate attendance/payment/students/custom
    - Admin can generate any type
    - Superadmin can generate any type (analytics, ai_analysis, etc.)
    """
    # Leader uchun tur cheklash
    leader_allowed_types = {
        ReportType.ATTENDANCE,
        ReportType.PAYMENT,
        ReportType.STUDENTS,
        ReportType.CUSTOM,
    }
    if (
        current_user.role == UserRole.LEADER
        and data.report_type not in leader_allowed_types
    ):
        raise ForbiddenException("Bu hisobot turini generatsiya qilish uchun ruxsat yo'q")

    service = ReportService(db)
    report = await service.generate_report(
        report_type=data.report_type,
        group_id=data.group_id,
        start_date=data.date_from,
        end_date=data.date_to,
        created_by=current_user.id,
    )
    logger.info(
        f"Report generated: id={report.id}, type={data.report_type.value} by user={current_user.id}"
    )
    return _build_response(report)


# ──────────────────────────────────────────────
# STATISTICS (must be before /{report_id} to avoid route shadowing)
# ──────────────────────────────────────────────
@router.get("/stats/summary")
async def get_report_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Get report statistics.
    
    - Leader: own group stats only
    - Admin: faculty-wide stats (with optional group filter)
    - Superadmin: system-wide stats
    """
    service = ReportService(db)

    # Leader faqat o'z guruhi statistikasini ko'radi
    if current_user.role == UserRole.LEADER:
        stats = await service.get_report_stats(
            start_date, end_date, created_by=current_user.id
        )
    else:
        stats = await service.get_report_stats(
            start_date, end_date, group_id=group_id
        )

    return stats


# ──────────────────────────────────────────────
# REPORT TYPES (available for current role)
# ──────────────────────────────────────────────
@router.get("/types")
async def get_report_types(
    current_user: User = Depends(require_leader),
):
    """
    Get available report types for current user role.
    
    - Leader: attendance, payment, students, custom
    - Admin: attendance, payment, students, groups, custom
    - Superadmin: ALL types (including analytics, ai_analysis)
    """
    if current_user.role == UserRole.LEADER:
        allowed = [
            ReportType.ATTENDANCE,
            ReportType.PAYMENT,
            ReportType.STUDENTS,
            ReportType.CUSTOM,
        ]
    elif current_user.role == UserRole.ADMIN:
        allowed = [
            ReportType.ATTENDANCE,
            ReportType.PAYMENT,
            ReportType.STUDENTS,
            ReportType.GROUPS,
            ReportType.CUSTOM,
        ]
    else:
        # Superadmin — barcha turlar
        allowed = list(ReportType)

    return [
        {"value": rt.value, "label": rt.value.replace("_", " ").title()}
        for rt in allowed
    ]


# ──────────────────────────────────────────────
# GET SINGLE REPORT
# ──────────────────────────────────────────────
@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Get report by ID.
    
    - Leader: only own reports
    - Admin/Superadmin: any report
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise NotFoundException("Report not found")

    _check_report_access(report, current_user)
    return _build_response(report)


# ──────────────────────────────────────────────
# UPDATE
# ──────────────────────────────────────────────
@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Update report.
    
    - Leader: only own reports with pending/failed status
    - Admin/Superadmin: any report
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise NotFoundException("Report not found")

    _check_report_access(report, current_user, write=True)

    # Leader status o'zgartira olmaydi
    if current_user.role == UserRole.LEADER and report_data.status is not None:
        raise ForbiddenException("Leader hisobot statusini o'zgartira olmaydi")

    report = await service.update(report_id, report_data)
    logger.info(
        f"Report updated: id={report_id} by user={current_user.id} ({current_user.role.value})"
    )
    return _build_response(report)


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────
@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Delete report.
    
    - Leader: only own reports with draft/failed status
    - Admin: any report
    - Superadmin: any report
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise NotFoundException("Report not found")

    if current_user.role == UserRole.LEADER:
        if report.created_by != current_user.id:
            raise ForbiddenException("Faqat o'z hisobotingizni o'chirishingiz mumkin")
        if report.status not in (ReportStatus.PENDING, ReportStatus.FAILED):
            raise ForbiddenException(
                "Faqat kutilayotgan yoki xato hisobotlarni o'chirish mumkin"
            )
    elif current_user.role == UserRole.ADMIN:
        # Admin o'chirish mumkin, lekin approved hisobotlarni faqat superadmin
        if report.status == ReportStatus.APPROVED:
            raise ForbiddenException(
                "Tasdiqlangan hisobotlarni faqat superadmin o'chirishi mumkin"
            )

    await service.delete(report_id)
    logger.info(
        f"Report deleted: id={report_id} by user={current_user.id} ({current_user.role.value})"
    )
    return {"message": "Report deleted"}


# ──────────────────────────────────────────────
# DOWNLOAD
# ──────────────────────────────────────────────
@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query("excel", enum=["excel", "pdf", "csv"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Download report file.
    
    - Leader: only own reports
    - Admin/Superadmin: any report
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise NotFoundException("Report not found")

    _check_report_access(report, current_user)

    file_data, content_type, filename = await service.download_report(
        report_id, format
    )

    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ──────────────────────────────────────────────
# APPROVE / REJECT (admin & superadmin only)
# ──────────────────────────────────────────────
@router.post("/{report_id}/approve", response_model=ReportResponse)
async def approve_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Approve a report. Requires admin or superadmin role.
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise NotFoundException("Report not found")

    report = await service.update_status(report_id, ReportStatus.APPROVED, current_user.id)
    logger.info(
        f"Report approved: id={report_id} by admin={current_user.id}"
    )
    return _build_response(report)


@router.post("/{report_id}/reject", response_model=ReportResponse)
async def reject_report(
    report_id: int,
    reason: str = Query(..., min_length=5),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Reject a report with reason. Requires admin or superadmin role.
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise NotFoundException("Report not found")

    report = await service.update_status(report_id, ReportStatus.REJECTED, current_user.id, reason)
    logger.info(
        f"Report rejected: id={report_id} reason='{reason}' by admin={current_user.id}"
    )
    return _build_response(report)
