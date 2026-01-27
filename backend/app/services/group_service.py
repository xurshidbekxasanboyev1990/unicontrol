"""
UniControl - Group Service
==========================
Handles group management operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.models.group import Group
from app.models.student import Student
from app.models.user import User
from app.schemas.group import GroupCreate, GroupUpdate, GroupStats
from app.core.exceptions import NotFoundException, ConflictException


class GroupService:
    """Group management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, group_id: int) -> Optional[Group]:
        """Get group by ID with relationships."""
        result = await self.db.execute(
            select(Group)
            .options(joinedload(Group.leader), joinedload(Group.students))
            .where(Group.id == group_id)
        )
        return result.unique().scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Group]:
        """Get group by name."""
        result = await self.db.execute(
            select(Group).where(Group.name == name)
        )
        return result.scalar_one_or_none()
    
    async def list_groups(
        self,
        page: int = 1,
        page_size: int = 20,
        course_year: Optional[int] = None,
        faculty: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Group], int]:
        """
        List groups with pagination and filters.
        
        Returns:
            Tuple of (groups list, total count)
        """
        query = select(Group).options(joinedload(Group.leader))
        count_query = select(func.count(Group.id))
        
        # Apply filters
        if course_year:
            query = query.where(Group.course_year == course_year)
            count_query = count_query.where(Group.course_year == course_year)
        
        if faculty:
            query = query.where(Group.faculty == faculty)
            count_query = count_query.where(Group.faculty == faculty)
        
        if is_active is not None:
            query = query.where(Group.is_active == is_active)
            count_query = count_query.where(Group.is_active == is_active)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Group.name.ilike(search_filter)) |
                (Group.department.ilike(search_filter)) |
                (Group.faculty.ilike(search_filter))
            )
            count_query = count_query.where(
                (Group.name.ilike(search_filter)) |
                (Group.department.ilike(search_filter)) |
                (Group.faculty.ilike(search_filter))
            )
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Group.course_year, Group.name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        groups = result.unique().scalars().all()
        
        return list(groups), total
    
    async def create(self, group_data: GroupCreate) -> Group:
        """Create a new group."""
        # Check name uniqueness
        existing = await self.get_by_name(group_data.name)
        if existing:
            raise ConflictException("Group with this name already exists")
        
        # Create group
        group = Group(
            name=group_data.name,
            description=group_data.description,
            course_year=group_data.course_year,
            department=group_data.department,
            faculty=group_data.faculty,
            leader_id=group_data.leader_id,
            contract_amount=group_data.contract_amount,
        )
        
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        
        return group
    
    async def update(self, group_id: int, group_data: GroupUpdate) -> Group:
        """Update group."""
        group = await self.get_by_id(group_id)
        if not group:
            raise NotFoundException("Group not found")
        
        # Check name uniqueness if changing
        if group_data.name and group_data.name != group.name:
            existing = await self.get_by_name(group_data.name)
            if existing:
                raise ConflictException("Group name already in use")
        
        # Update fields
        update_data = group_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)
        
        await self.db.commit()
        await self.db.refresh(group)
        
        return group
    
    async def delete(self, group_id: int) -> bool:
        """Delete group."""
        group = await self.get_by_id(group_id)
        if not group:
            raise NotFoundException("Group not found")
        
        # Check if group has students
        result = await self.db.execute(
            select(func.count(Student.id))
            .where(Student.group_id == group_id)
        )
        student_count = result.scalar()
        
        if student_count > 0:
            raise ConflictException(
                f"Cannot delete group with {student_count} students"
            )
        
        await self.db.delete(group)
        await self.db.commit()
        
        return True
    
    async def set_leader(self, group_id: int, leader_id: Optional[int]) -> Group:
        """Set or unset group leader."""
        group = await self.get_by_id(group_id)
        if not group:
            raise NotFoundException("Group not found")
        
        if leader_id:
            # Verify leader exists and is from this group (if student)
            result = await self.db.execute(
                select(Student)
                .where(Student.id == leader_id)
                .where(Student.group_id == group_id)
            )
            student = result.scalar_one_or_none()
            
            if not student:
                raise NotFoundException("Student not found in this group")
            
            # Update student's leader status
            student.is_leader = True
        
        group.leader_id = leader_id
        await self.db.commit()
        await self.db.refresh(group)
        
        return group
    
    async def get_students_count(self, group_id: int) -> int:
        """Get number of students in a group."""
        result = await self.db.execute(
            select(func.count(Student.id))
            .where(Student.group_id == group_id)
            .where(Student.is_active == True)
        )
        return result.scalar() or 0
    
    async def get_statistics(self) -> GroupStats:
        """Get group statistics."""
        # Total groups
        total_result = await self.db.execute(select(func.count(Group.id)))
        total = total_result.scalar()
        
        # Active groups
        active_result = await self.db.execute(
            select(func.count(Group.id)).where(Group.is_active == True)
        )
        active = active_result.scalar()
        
        # Total students
        students_result = await self.db.execute(
            select(func.count(Student.id)).where(Student.is_active == True)
        )
        total_students = students_result.scalar()
        
        # Contract amounts
        contract_result = await self.db.execute(
            select(
                func.sum(Student.contract_amount),
                func.sum(Student.contract_paid)
            )
        )
        contract_data = contract_result.one()
        total_contract = contract_data[0] or Decimal(0)
        total_paid = contract_data[1] or Decimal(0)
        
        # Groups by course
        course_result = await self.db.execute(
            select(Group.course_year, func.count(Group.id))
            .group_by(Group.course_year)
        )
        groups_by_course = {row[0]: row[1] for row in course_result.all()}
        
        return GroupStats(
            total_groups=total,
            active_groups=active,
            total_students=total_students,
            total_contract_amount=total_contract,
            total_contract_paid=total_paid,
            groups_by_course=groups_by_course
        )
    
    async def get_all_active(self) -> List[Group]:
        """Get all active groups."""
        result = await self.db.execute(
            select(Group)
            .where(Group.is_active == True)
            .order_by(Group.course_year, Group.name)
        )
        return list(result.scalars().all())
    
    async def get_by_faculty(self, faculty: str) -> List[Group]:
        """Get all groups in a faculty."""
        result = await self.db.execute(
            select(Group)
            .where(Group.faculty == faculty)
            .where(Group.is_active == True)
            .order_by(Group.course_year, Group.name)
        )
        return list(result.scalars().all())
    
    async def get_by_code(self, code: str) -> Optional[Group]:
        """
        Get group by code (name).
        Code is used as unique identifier for Telegram bot.
        """
        result = await self.db.execute(
            select(Group)
            .options(joinedload(Group.leader), joinedload(Group.students))
            .where(Group.name == code)
        )
        return result.unique().scalar_one_or_none()
    
    async def search_groups(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[Group]:
        """
        Search groups by code/name.
        Used by Telegram bot for inline search.
        """
        search_filter = f"%{query}%"
        result = await self.db.execute(
            select(Group)
            .where(
                (Group.name.ilike(search_filter)) |
                (Group.faculty.ilike(search_filter))
            )
            .where(Group.is_active == True)
            .order_by(Group.name)
            .limit(limit)
        )
        return list(result.scalars().all())
