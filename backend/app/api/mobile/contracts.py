"""
UniControl - Mobile Contract Routes
=====================================
Mobile endpoints for student contracts/payments.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.contract import Contract
from app.models.group import Group
from app.core.dependencies import get_current_active_user

router = APIRouter()


@router.get("/my")
async def get_my_contract(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's contract info."""
    # Find student
    student = (await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )).scalar_one_or_none()

    if not student:
        return {
            "has_contract": False,
            "student": None,
            "contracts": [],
        }

    # Get group name
    group_name = None
    if student.group_id:
        group = (await db.execute(select(Group).where(Group.id == student.group_id))).scalar_one_or_none()
        group_name = group.name if group else None

    # Get detailed contracts
    contracts_res = await db.execute(
        select(Contract).where(Contract.student_id == student.id).order_by(Contract.academic_year.desc())
    )
    contracts = contracts_res.scalars().all()

    contract_list = []
    for c in contracts:
        contract_list.append({
            "id": c.id,
            "academic_year": c.academic_year,
            "course": c.course,
            "direction": c.direction,
            "education_form": c.education_form,
            "student_status": c.student_status,
            "contract_amount": float(c.contract_amount or 0),
            "grant_percentage": float(c.grant_percentage or 0),
            "grant_amount": float(c.grant_amount or 0),
            "total_paid": float(c.total_paid or 0),
            "debt_amount": float(c.debt_amount or 0),
            "payment_percentage": float(c.payment_percentage or 0),
            "refund_amount": float(c.refund_amount or 0),
        })

    # Basic info from student model
    basic = {
        "contract_amount": float(student.contract_amount or 0),
        "contract_paid": float(student.contract_paid or 0),
        "contract_remaining": float((student.contract_amount or 0) - (student.contract_paid or 0)),
        "contract_percentage": round(
            float(student.contract_paid or 0) / float(student.contract_amount or 1) * 100, 1
        ) if student.contract_amount else 0,
    }

    return {
        "has_contract": True,
        "student": {
            "id": student.id,
            "name": student.name,
            "student_id": student.student_id,
            "group_name": group_name,
        },
        "basic": basic,
        "contracts": contract_list,
    }


@router.get("/group")
async def get_group_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get contracts for leader's group."""
    # Find leader's student profile first, then their group
    student = (await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )).scalar_one_or_none()

    group = None
    if student and student.group_id:
        group = (await db.execute(
            select(Group).where(Group.id == student.group_id)
        )).scalar_one_or_none()

    if not group:
        return {"items": [], "total": 0, "group_name": None, "summary": {}}

    # Get students in group
    students_res = await db.execute(
        select(Student).where(Student.group_id == group.id, Student.is_active == True)
    )
    students = students_res.scalars().all()

    items = []
    total_contract = 0
    total_paid = 0
    total_debt = 0

    for s in students:
        amount = float(s.contract_amount or 0)
        paid = float(s.contract_paid or 0)
        debt = amount - paid

        total_contract += amount
        total_paid += paid
        total_debt += debt

        items.append({
            "student_id": s.id,
            "name": s.name,
            "hemis_id": s.student_id,
            "contract_amount": amount,
            "contract_paid": paid,
            "debt": debt,
            "percentage": round(paid / amount * 100, 1) if amount > 0 else 0,
            "is_paid": debt <= 0,
        })

    return {
        "items": items,
        "total": len(items),
        "group_name": group.name,
        "summary": {
            "total_students": len(items),
            "total_contract": total_contract,
            "total_paid": total_paid,
            "total_debt": total_debt,
            "payment_rate": round(total_paid / total_contract * 100, 1) if total_contract > 0 else 0,
            "fully_paid": sum(1 for i in items if i["is_paid"]),
            "with_debt": sum(1 for i in items if not i["is_paid"]),
        },
    }
