"""
UniControl - Contract Routes
=============================
Contract data management endpoints with Excel import/export.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io

from app.database import get_db
from app.services.contract_service import ContractService
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractStats,
    ContractImportResult,
)
from app.core.dependencies import get_current_active_user, require_admin, require_superadmin, require_leader
from app.models.user import User, UserRole
from app.models.student import Student

router = APIRouter()


@router.get("/my")
async def get_my_contract(
    academic_year: Optional[str] = "2025-2026",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current student's contract data.
    Available for students and leaders.
    """
    from sqlalchemy import select as sa_select
    
    # Find student linked to this user
    result = await db.execute(
        sa_select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        return {"contract": None, "message": "Talaba topilmadi"}
    
    service = ContractService(db)
    contract = await service.get_by_student_and_year(student.id, academic_year)
    if not contract:
        return {
            "contract": None,
            "student_name": student.name,
            "message": "Kontrakt ma'lumotlari topilmadi"
        }
    
    # Reload with relationships
    contract = await service.get_by_id(contract.id)
    return {
        "contract": ContractResponse.model_validate(contract),
        "student_name": student.name
    }


@router.get("/group/{group_id}")
async def get_group_contracts(
    group_id: int,
    academic_year: Optional[str] = "2025-2026",
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=5000),
    search: Optional[str] = None,
    has_debt: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader),
):
    """
    Get contracts for a specific group. Available for leaders, admin, superadmin.
    Leaders can only see their own group.
    """
    # Leaders can only see their own group
    if current_user.role == UserRole.LEADER:
        from sqlalchemy import select as sa_select
        result = await db.execute(
            sa_select(Student).where(Student.user_id == current_user.id)
        )
        student = result.scalar_one_or_none()
        if not student or student.group_id != group_id:
            from app.core.exceptions import ForbiddenException
            raise ForbiddenException("Siz faqat o'z guruhingiz ma'lumotlarini ko'rishingiz mumkin")
    
    service = ContractService(db)
    contracts, total = await service.list_contracts(
        page=page,
        page_size=page_size,
        academic_year=academic_year,
        group_id=group_id,
        has_debt=has_debt,
        search=search,
    )
    
    # Also get group stats
    stats = await service.get_statistics(academic_year, group_id)
    
    return {
        "items": [ContractResponse.model_validate(c) for c in contracts],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "stats": stats,
    }


@router.get("", response_model=ContractListResponse)
async def list_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=5000),
    academic_year: Optional[str] = None,
    group_id: Optional[int] = None,
    education_form: Optional[str] = None,
    student_status: Optional[str] = None,
    has_debt: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    List contracts with pagination and filters.
    Requires admin role.
    """
    service = ContractService(db)
    contracts, total = await service.list_contracts(
        page=page,
        page_size=page_size,
        academic_year=academic_year,
        group_id=group_id,
        education_form=education_form,
        student_status=student_status,
        has_debt=has_debt,
        search=search,
    )
    
    return ContractListResponse(
        items=[ContractResponse.model_validate(c) for c in contracts],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/statistics", response_model=ContractStats)
async def get_statistics(
    academic_year: Optional[str] = None,
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get contract statistics."""
    service = ContractService(db)
    return await service.get_statistics(academic_year, group_id)


@router.get("/academic-years")
async def get_academic_years(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get list of available academic years."""
    service = ContractService(db)
    years = await service.get_academic_years()
    return {"years": years}


@router.get("/filters")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get available filter options (education forms, statuses)."""
    service = ContractService(db)
    education_forms = await service.get_education_forms()
    statuses = await service.get_student_statuses()
    years = await service.get_academic_years()
    return {
        "education_forms": education_forms,
        "student_statuses": statuses,
        "academic_years": years,
    }


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get contract by ID."""
    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Contract not found")
    return ContractResponse.model_validate(contract)


@router.post("", response_model=ContractResponse)
async def create_contract(
    data: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Create a new contract. Requires superadmin."""
    service = ContractService(db)
    contract = await service.create(data)
    return ContractResponse.model_validate(contract)


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(
    contract_id: int,
    data: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Update a contract. Requires superadmin."""
    service = ContractService(db)
    contract = await service.update(contract_id, data)
    return ContractResponse.model_validate(contract)


@router.delete("/{contract_id}")
async def delete_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Delete a contract. Requires superadmin."""
    service = ContractService(db)
    await service.delete(contract_id)
    return {"message": "Contract deleted successfully"}


@router.post("/import", response_model=ContractImportResult)
async def import_contracts(
    file: UploadFile = File(...),
    academic_year: str = Form("2025-2026"),
    update_existing: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """
    Import contracts from Excel file.
    
    Requires superadmin role.
    
    Excel format (kontraktmalumotlari.xlsx):
    - Column 2: To'liq ismi (Full name)
    - Column 3: JSHSHIR-kod
    - Column 4: Pasport seriya va raqami
    - Column 5: Telefon raqami
    - Column 6: Kurs
    - Column 7: Talaba xolati
    - Column 8: Guruh
    - Column 9: Yo'nalishi
    - Column 10: Ta'lim shakli
    - Column 11: Kontrakt summasi
    - Column 12: Grand (Foizda)
    - Column 13: Grand (Summada)
    - Column 14: Qarzdorlik summasi
    - Column 15: Foizda (Jami)
    - Column 16: To'lov summasi
    - Column 17: Qaytarilgan summa
    - Column 18: Yil boshiga qoldiq
    - Column 19: Yil yakuniga qoldiq
    """
    from app.core.exceptions import BadRequestException
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise BadRequestException("Noto'g'ri fayl turi. Faqat Excel (.xlsx) fayl yuklang.")
    
    contents = await file.read()
    service = ContractService(db)
    
    result = await service.import_from_excel(
        file_data=contents,
        academic_year=academic_year,
        update_existing=update_existing,
    )
    
    return result


@router.get("/export/excel")
async def export_contracts(
    academic_year: Optional[str] = None,
    group_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Export contracts to Excel file."""
    service = ContractService(db)
    file_data = await service.export_to_excel(academic_year, group_id)
    
    filename = f"kontrakt_malumotlari"
    if academic_year:
        filename += f"_{academic_year}"
    filename += ".xlsx"
    
    return StreamingResponse(
        io.BytesIO(file_data),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/year/{academic_year}")
async def delete_year_contracts(
    academic_year: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Delete all contracts for an academic year. Requires superadmin."""
    service = ContractService(db)
    count = await service.delete_by_year(academic_year)
    return {"message": f"{count} ta kontrakt o'chirildi", "deleted_count": count}
