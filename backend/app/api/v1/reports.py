"""
UniControl - Report Routes
==========================
Report management endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
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
from app.core.dependencies import get_current_active_user, require_admin, require_leader
from app.models.user import User

router = APIRouter()


@router.get("", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: Optional[ReportType] = None,
    report_status: Optional[ReportStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List reports with filters.
    """
    service = ReportService(db)
    reports, total = await service.list_reports(
        page=page,
        page_size=page_size,
        report_type=report_type,
        status=report_status,
        user_id=current_user.id if current_user.role.value == "leader" else None
    )
    
    return ReportListResponse(
        items=[ReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Create a new report.
    
    Requires leader role or higher.
    """
    service = ReportService(db)
    report = await service.create(report_data, current_user.id)
    return ReportResponse.model_validate(report)


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    data: ReportGenerate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Generate a report based on parameters.
    
    Requires leader role or higher.
    """
    service = ReportService(db)
    report = await service.generate_report(
        report_type=data.report_type,
        group_id=data.group_id,
        start_date=data.start_date,
        end_date=data.end_date,
        created_by=current_user.id
    )
    return ReportResponse.model_validate(report)


@router.get("/types")
async def get_report_types(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get available report types.
    """
    return [
        {"value": rt.value, "label": rt.value.replace("_", " ").title()}
        for rt in ReportType
    ]


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get report by ID.
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    if not report:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Report not found")
    return ReportResponse.model_validate(report)


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    report_data: ReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Update report.
    
    Requires leader role or higher.
    """
    service = ReportService(db)
    report = await service.update(report_id, report_data)
    return ReportResponse.model_validate(report)


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete report.
    
    Requires admin role.
    """
    service = ReportService(db)
    await service.delete(report_id)
    return {"message": "Report deleted"}


@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    format: str = Query("excel", enum=["excel", "pdf", "csv"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Download report in specified format.
    """
    service = ReportService(db)
    report = await service.get_by_id(report_id)
    
    if not report:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Report not found")
    
    file_data, content_type, filename = await service.download_report(report_id, format)
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.post("/{report_id}/approve", response_model=ReportResponse)
async def approve_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Approve a report.
    
    Requires admin role.
    """
    service = ReportService(db)
    report = await service.update_status(report_id, ReportStatus.APPROVED)
    return ReportResponse.model_validate(report)


@router.post("/{report_id}/reject", response_model=ReportResponse)
async def reject_report(
    report_id: int,
    reason: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reject a report.
    
    Requires admin role.
    """
    service = ReportService(db)
    report = await service.update_status(report_id, ReportStatus.REJECTED, reason)
    return ReportResponse.model_validate(report)


@router.get("/stats/summary")
async def get_report_stats(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get report statistics.
    
    Requires leader role or higher.
    """
    service = ReportService(db)
    return await service.get_report_stats(start_date, end_date)
