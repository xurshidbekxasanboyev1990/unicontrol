"""
UniControl - Excel Routes
=========================
Excel import/export endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from datetime import date
import secrets
import string
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database import get_db
from app.services.excel_service import ExcelService
from app.core.dependencies import get_current_active_user, require_admin, require_leader, require_superadmin
from app.models.user import User

router = APIRouter()


# General Import Endpoint
@router.post("/import")
async def import_excel(
    file: UploadFile = File(...),
    type: str = Form("auto"),
    group_id: Optional[int] = Form(None),
    update_existing: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    General Excel import endpoint.
    
    Args:
        file: Excel file to import
        type: Type of data to import (auto, kontingent, groups, students)
        group_id: Group ID for student import
        update_existing: Whether to update existing records
    
    Returns:
        Import results with counts and errors
    """
    from app.core.exceptions import BadRequestException
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise BadRequestException("Invalid file type. Please upload an Excel file.")
    
    service = ExcelService(db)
    contents = await file.read()
    
    # Auto-detect kontingent format
    if type == "auto":
        import pandas as pd
        try:
            df = pd.read_excel(io.BytesIO(contents), engine='openpyxl', nrows=5)
            columns = [str(c).lower() for c in df.columns]
            
            # Check for kontingent format markers
            if any('talaba id' in c or 'full name' in c or 'passport' in c for c in columns):
                type = "kontingent"
            elif any('guruh' in c or 'fakultet' in c for c in columns):
                type = "groups"
            else:
                type = "kontingent"  # Default to kontingent
        except:
            type = "kontingent"
    
    if type == "kontingent":
        # Generate secure default password if not provided
        secure_default = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        result = await service.import_kontingent(
            file_data=contents,
            update_existing=update_existing,
            create_users=True,
            default_password=secure_default
        )
        return {
            "success": True,
            "imported_count": result.get("imported", 0),
            "updated_count": result.get("updated", 0),
            "failed_count": result.get("failed", 0),
            "skipped_count": result.get("skipped", 0),
            "groups_created": result.get("groups_created", 0),
            "users_created": result.get("users_created", 0),
            "errors": result.get("errors", [])[:20]  # Limit errors
        }
    elif type == "students":
        result = await service.import_students(
            file_data=contents,
            group_id=group_id,
            update_existing=update_existing
        )
    elif type == "groups":
        result = await service.import_groups(
            file_data=contents,
            update_existing=update_existing
        )
    else:
        raise BadRequestException(f"Unknown import type: {type}")
    
    return {
        "success": result.get("success", True),
        "imported_count": result.get("imported", 0),
        "updated_count": result.get("updated", 0),
        "failed_count": result.get("failed", 0),
        "errors": result.get("errors", [])
    }


# Import Endpoints
@router.post("/import/students")
async def import_students(
    file: UploadFile = File(...),
    group_id: Optional[int] = Form(None),
    update_existing: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Import students from Excel file.
    
    Requires admin role.
    
    Excel format:
    - Column A: Full Name
    - Column B: Student ID (HEMIS ID)
    - Column C: Email
    - Column D: Phone
    - Column E: Group Code (optional if group_id provided)
    - Column F: Contract Number (optional)
    """
    service = ExcelService(db)
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Invalid file type. Please upload an Excel file.")
    
    contents = await file.read()
    result = await service.import_students(
        file_data=contents,
        group_id=group_id,
        update_existing=update_existing
    )
    
    return {
        "success": result["success"],
        "imported_count": result["imported"],
        "updated_count": result["updated"],
        "failed_count": result["failed"],
        "errors": result["errors"]
    }


@router.post("/import/groups")
async def import_groups(
    file: UploadFile = File(...),
    update_existing: bool = Form(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Import groups from Excel file.
    
    Requires admin role.
    
    Excel format:
    - Column A: Group Code
    - Column B: Group Name
    - Column C: Faculty
    - Column D: Course
    - Column E: Leader Email (optional)
    """
    service = ExcelService(db)
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Invalid file type. Please upload an Excel file.")
    
    contents = await file.read()
    result = await service.import_groups(
        file_data=contents,
        update_existing=update_existing
    )
    
    return result


@router.post("/import/attendance")
async def import_attendance(
    file: UploadFile = File(...),
    group_id: int = Form(...),
    attendance_date: date = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Import attendance from Excel file.
    
    Requires leader role or higher.
    
    Excel format:
    - Column A: Student ID or Name
    - Column B: Status (present/absent/late/excused)
    - Column C: Notes (optional)
    """
    service = ExcelService(db)
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Invalid file type. Please upload an Excel file.")
    
    contents = await file.read()
    result = await service.import_attendance(
        file_data=contents,
        group_id=group_id,
        attendance_date=attendance_date
    )
    
    return result


@router.post("/import/schedules")
async def import_schedules(
    file: UploadFile = File(...),
    group_id: int = Form(...),
    semester: int = Form(...),
    academic_year: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Import schedules from Excel file.
    
    Requires admin role.
    
    Excel format:
    - Column A: Subject Name
    - Column B: Day of Week (1-7)
    - Column C: Start Time (HH:MM)
    - Column D: End Time (HH:MM)
    - Column E: Room
    - Column F: Teacher Name (optional)
    """
    service = ExcelService(db)
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Invalid file type. Please upload an Excel file.")
    
    contents = await file.read()
    result = await service.import_schedules(
        file_data=contents,
        group_id=group_id,
        semester=semester,
        academic_year=academic_year
    )
    
    return result


@router.post("/import/kontingent")
async def import_kontingent(
    file: UploadFile = File(...),
    update_existing: bool = Form(False),
    create_users: bool = Form(True),
    default_password: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    """
    Import students from Kontingent Excel file.
    
    Requires superadmin role.
    
    This endpoint handles the special format of Kontingent export files
    which have merged cells and specific column structure:
    - Row 1-2: Headers with merged cells
    - Row 3+: Student data
    
    Features:
    - Auto-creates Group if not exists
    - Auto-creates User account for each student (login = student_id)
    - Sets is_first_login=True for password change prompt
    - Handles merged cells and complex structure
    
    Args:
        file: Excel file (.xlsx)
        update_existing: If True, update existing students
        create_users: If True, create user accounts (default: True)
        default_password: Default password for new accounts (auto-generated if not set)
    
    Returns:
        Import statistics and errors
    """
    service = ExcelService(db)
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        from app.core.exceptions import BadRequestException
        raise BadRequestException("Faqat Excel fayl (.xlsx, .xls) yuklay olasiz.")
    
    # Generate secure password if not provided
    if not default_password:
        default_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    contents = await file.read()
    result = await service.import_kontingent(
        file_data=contents,
        update_existing=update_existing,
        create_users=create_users,
        default_password=default_password
    )
    
    return result


# Export Endpoints
@router.get("/export/students")
async def export_students(
    group_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Export students to Excel file.
    
    Requires leader role or higher.
    """
    service = ExcelService(db)
    file_data = await service.export_students(
        group_id=group_id,
        is_active=is_active
    )
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=students.xlsx"
        }
    )


@router.get("/export/groups")
async def export_groups(
    faculty: Optional[str] = None,
    course: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Export groups to Excel file.
    
    Requires admin role.
    """
    service = ExcelService(db)
    file_data = await service.export_groups(
        faculty=faculty,
        course=course
    )
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=groups.xlsx"
        }
    )


@router.get("/export/attendance")
async def export_attendance(
    group_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Export attendance to Excel file.
    
    Requires leader role or higher.
    """
    service = ExcelService(db)
    file_data = await service.export_attendance(
        group_id=group_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=attendance_{start_date}_{end_date}.xlsx"
        }
    )


@router.get("/export/schedules")
async def export_schedules(
    group_id: int = Query(...),
    semester: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Export schedules to Excel file.
    
    Requires leader role or higher.
    """
    service = ExcelService(db)
    file_data = await service.export_schedules(
        group_id=group_id,
        semester=semester
    )
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=schedule.xlsx"
        }
    )


@router.get("/export/report/{report_id}")
async def export_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Export report to Excel file.
    
    Requires leader role or higher.
    """
    service = ExcelService(db)
    file_data, filename = await service.export_report(report_id)
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


# Template Downloads
@router.get("/templates/students")
async def download_students_template(
    current_user: User = Depends(require_admin)
):
    """
    Download students import template.
    """
    service = ExcelService(None)
    file_data = service.generate_students_template()
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=students_template.xlsx"
        }
    )


@router.get("/templates/groups")
async def download_groups_template(
    current_user: User = Depends(require_admin)
):
    """
    Download groups import template.
    """
    service = ExcelService(None)
    file_data = service.generate_groups_template()
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=groups_template.xlsx"
        }
    )


@router.get("/templates/attendance")
async def download_attendance_template(
    group_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Download attendance import template pre-filled with students.
    """
    service = ExcelService(db)
    file_data = await service.generate_attendance_template(group_id)
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=attendance_template.xlsx"
        }
    )


@router.get("/templates/schedules")
async def download_schedules_template(
    current_user: User = Depends(require_admin)
):
    """
    Download schedules import template.
    """
    service = ExcelService(None)
    file_data = service.generate_schedules_template()
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=schedules_template.xlsx"
        }
    )
