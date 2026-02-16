"""
UniControl - Global Search API
===============================
Search across students, users, and groups.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group
from app.core.dependencies import get_current_active_user
from pydantic import BaseModel

router = APIRouter()


class SearchResultItem(BaseModel):
    id: int
    type: str  # 'student', 'user', 'group'
    title: str
    subtitle: Optional[str] = None
    avatar: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total: int


@router.get("", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Global search across students, users, and groups.
    Available to admin and superadmin roles.
    """
    results = []
    search_pattern = f"%{q}%"
    
    # Search Students
    try:
        student_query = (
            select(Student)
            .options(selectinload(Student.group))
            .where(
                or_(
                    Student.name.ilike(search_pattern),
                    Student.student_id.ilike(search_pattern),
                    Student.phone.ilike(search_pattern),
                )
            )
            .limit(limit)
        )
        student_result = await db.execute(student_query)
        students = student_result.scalars().all()
        
        for s in students:
            group_name = s.group.name if s.group else ""
            results.append(SearchResultItem(
                id=s.id,
                type="student",
                title=s.name or s.student_id,
                subtitle=f"ID: {s.student_id}" + (f" • {group_name}" if group_name else ""),
                url=f"/student/{s.id}"
            ))
    except Exception as e:
        pass
    
    # Search Users (only for admin+)
    if current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        try:
            user_query = (
                select(User)
                .where(
                    User.role.notin_([UserRole.STUDENT]),
                    or_(
                        User.name.ilike(search_pattern),
                        User.email.ilike(search_pattern),
                        User.login.ilike(search_pattern),
                        User.phone.ilike(search_pattern),
                    )
                )
                .limit(limit)
            )
            user_result = await db.execute(user_query)
            users = user_result.scalars().all()
            
            for u in users:
                role_label = {
                    UserRole.SUPERADMIN: "Super Admin",
                    UserRole.ADMIN: "Admin",
                    UserRole.LEADER: "Sardor",
                    UserRole.STUDENT: "Talaba",
                }.get(u.role, str(u.role))
                
                results.append(SearchResultItem(
                    id=u.id,
                    type="user",
                    title=u.name or u.login,
                    subtitle=f"{role_label}" + (f" • {u.email}" if u.email else ""),
                    avatar=u.avatar,
                ))
        except Exception as e:
            pass
    
    # Search Groups
    try:
        group_query = (
            select(Group)
            .where(
                Group.name.ilike(search_pattern)
            )
            .limit(limit)
        )
        group_result = await db.execute(group_query)
        groups = group_result.scalars().all()
        
        for g in groups:
            results.append(SearchResultItem(
                id=g.id,
                type="group",
                title=g.name,
                subtitle=f"Guruh",
            ))
    except Exception as e:
        pass
    
    # Sort: exact matches first, then partial
    q_lower = q.lower()
    results.sort(key=lambda r: (
        0 if q_lower in (r.title or "").lower()[:len(q_lower)] else 1,
        r.type,
        (r.title or "").lower()
    ))
    
    # Limit total results
    results = results[:limit]
    
    return SearchResponse(
        query=q,
        results=results,
        total=len(results)
    )
