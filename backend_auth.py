"""
UniControl - Authentication Routes
==================================
Login, logout, token refresh endpoints.

Author: UniControl Team
Version: 1.0.0
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth_service import AuthService
from app.schemas.user import (
    UserLogin,
    Token,
    UserResponse,
    UserCreate,
    PasswordUpdate,
    RefreshToken,
)
from app.core.dependencies import get_current_active_user
from app.models.user import User, UserRole

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns access and refresh tokens.
    """
    service = AuthService(db)
    return await service.login(credentials)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: RefreshToken,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    return await service.refresh_tokens(token_data.refresh_token)


@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's profile with extended student info if applicable.
    """
    from sqlalchemy import select
    from app.models.student import Student
    from app.models.group import Group
    
    response_data = {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role,
        "phone": current_user.phone,
        "avatar": current_user.avatar,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
        "login": current_user.login,
    }
    
    # Agar talaba yoki sardor bo'lsa, student ma'lumotlarini ham qaytarish
    if current_user.role in [UserRole.STUDENT, UserRole.LEADER]:
        # Student ma'lumotlarini topish
        result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        student = result.scalar_one_or_none()
        
        if student:
            response_data["student_id"] = student.student_id
            response_data["group_id"] = student.group_id
            response_data["full_name"] = student.full_name or student.name
            response_data["address"] = student.address
            response_data["commute"] = student.commute
            response_data["passport"] = student.passport
            response_data["jshshir"] = student.jshshir
            response_data["birth_date"] = student.birth_date.isoformat() if student.birth_date else None
            response_data["gender"] = student.gender
            response_data["contract_amount"] = float(student.contract_amount) if student.contract_amount else 0
            response_data["contract_paid"] = float(student.contract_paid) if student.contract_paid else 0
            response_data["student_phone"] = student.phone
            response_data["student_email"] = student.email
            
            # Guruh nomini olish
            if student.group_id:
                group_result = await db.execute(
                    select(Group).where(Group.id == student.group_id)
                )
                group = group_result.scalar_one_or_none()
                if group:
                    response_data["group_name"] = group.name
                    response_data["faculty"] = group.faculty
                    response_data["year"] = group.year
    
    return response_data


@router.put("/me/password")
async def change_password(
    password_data: PasswordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.
    """
    service = AuthService(db)
    await service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password updated successfully"}


@router.post("/logout")
async def logout():
    """
    Logout current user.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint is for API completeness.
    """
    return {"message": "Logged out successfully"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Note: In production, this should be restricted or require admin approval.
    """
    service = AuthService(db)
    user = await service.register(user_data)
    return UserResponse.model_validate(user)
