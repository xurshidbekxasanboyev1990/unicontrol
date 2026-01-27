"""
UniControl - Student Service
============================
Handles student management operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import joinedload

from app.models.student import Student
from app.models.user import User, UserRole
from app.models.group import Group
from app.schemas.student import StudentCreate, StudentUpdate, StudentStats
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException


class StudentService:
    """Student management service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, student_id: int) -> Optional[Student]:
        """Get student by ID with relationships."""
        result = await self.db.execute(
            select(Student)
            .options(joinedload(Student.group), joinedload(Student.user))
            .where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """Get student by student_id code."""
        result = await self.db.execute(
            select(Student)
            .options(joinedload(Student.group))
            .where(Student.student_id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_jshshir(self, jshshir: str) -> Optional[Student]:
        """Get student by JSHSHIR."""
        result = await self.db.execute(
            select(Student).where(Student.jshshir == jshshir)
        )
        return result.scalar_one_or_none()
    
    async def list_students(
        self,
        page: int = 1,
        page_size: int = 20,
        group_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_graduated: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Student], int]:
        """
        List students with pagination and filters.
        
        Returns:
            Tuple of (students list, total count)
        """
        query = select(Student).options(joinedload(Student.group))
        count_query = select(func.count(Student.id))
        
        # Apply filters
        if group_id:
            query = query.where(Student.group_id == group_id)
            count_query = count_query.where(Student.group_id == group_id)
        
        if is_active is not None:
            query = query.where(Student.is_active == is_active)
            count_query = count_query.where(Student.is_active == is_active)
        
        if is_graduated is not None:
            query = query.where(Student.is_graduated == is_graduated)
            count_query = count_query.where(Student.is_graduated == is_graduated)
        
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (Student.name.ilike(search_filter)) |
                (Student.student_id.ilike(search_filter)) |
                (Student.phone.ilike(search_filter)) |
                (Student.email.ilike(search_filter))
            )
            count_query = count_query.where(
                (Student.name.ilike(search_filter)) |
                (Student.student_id.ilike(search_filter)) |
                (Student.phone.ilike(search_filter)) |
                (Student.email.ilike(search_filter))
            )
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Student.name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        students = result.unique().scalars().all()
        
        return list(students), total
    
    async def _generate_student_id(self) -> str:
        """Generate unique student ID."""
        year = datetime.now().year
        prefix = f"ST-{year}-"
        
        # Find max existing student_id for this year
        result = await self.db.execute(
            select(func.max(Student.student_id))
            .where(Student.student_id.like(f"{prefix}%"))
        )
        max_id = result.scalar()
        
        if max_id:
            # Extract number and increment
            num = int(max_id.split("-")[-1]) + 1
        else:
            num = 1
        
        return f"{prefix}{num:04d}"
    
    async def create(self, student_data: StudentCreate) -> Student:
        """Create a new student."""
        # Check JSHSHIR uniqueness
        if student_data.jshshir:
            existing = await self.get_by_jshshir(student_data.jshshir)
            if existing:
                raise ConflictException("Student with this JSHSHIR already exists")
        
        # Generate student_id if not provided
        student_id = student_data.student_id or await self._generate_student_id()
        
        # Check student_id uniqueness
        existing = await self.get_by_student_id(student_id)
        if existing:
            raise ConflictException("Student ID already exists")
        
        # Create student
        student = Student(
            student_id=student_id,
            name=student_data.name,
            group_id=student_data.group_id,
            phone=student_data.phone,
            email=student_data.email,
            address=student_data.address,
            commute=student_data.commute,
            passport=student_data.passport,
            jshshir=student_data.jshshir,
            birth_date=student_data.birth_date,
            gender=student_data.gender,
            contract_amount=student_data.contract_amount,
            contract_paid=student_data.contract_paid,
            enrollment_date=student_data.enrollment_date or date.today(),
            graduation_date=student_data.graduation_date,
        )
        
        # Create linked user account if requested
        if student_data.create_user_account and student_data.email:
            user = User(
                email=student_data.email,
                name=student_data.name,
                password_hash=get_password_hash(
                    student_data.password or student_data.jshshir or "12345678"
                ),
                role=UserRole.STUDENT,
                phone=student_data.phone,
            )
            self.db.add(user)
            await self.db.flush()
            student.user_id = user.id
        
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        
        return student
    
    async def update(self, student_id: int, student_data: StudentUpdate) -> Student:
        """Update student."""
        student = await self.get_by_id(student_id)
        if not student:
            raise NotFoundException("Student not found")
        
        # Check JSHSHIR uniqueness if changing
        if student_data.jshshir and student_data.jshshir != student.jshshir:
            existing = await self.get_by_jshshir(student_data.jshshir)
            if existing:
                raise ConflictException("JSHSHIR already in use")
        
        # Update fields
        update_data = student_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        
        await self.db.commit()
        await self.db.refresh(student)
        
        return student
    
    async def delete(self, student_id: int) -> bool:
        """Delete student."""
        student = await self.get_by_id(student_id)
        if not student:
            raise NotFoundException("Student not found")
        
        # Delete linked user account if exists
        if student.user_id:
            user_result = await self.db.execute(
                select(User).where(User.id == student.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                await self.db.delete(user)
        
        await self.db.delete(student)
        await self.db.commit()
        
        return True
    
    async def add_payment(
        self,
        student_id: int,
        amount: Decimal,
        note: Optional[str] = None
    ) -> Student:
        """Add payment to student's contract."""
        student = await self.get_by_id(student_id)
        if not student:
            raise NotFoundException("Student not found")
        
        if amount <= 0:
            raise BadRequestException("Payment amount must be positive")
        
        student.contract_paid += amount
        await self.db.commit()
        await self.db.refresh(student)
        
        return student
    
    async def get_group_students(self, group_id: int) -> List[Student]:
        """Get all students in a group."""
        result = await self.db.execute(
            select(Student)
            .where(Student.group_id == group_id)
            .where(Student.is_active == True)
            .order_by(Student.name)
        )
        return list(result.scalars().all())
    
    async def get_statistics(self, group_id: Optional[int] = None) -> StudentStats:
        """Get student statistics."""
        query = select(Student)
        
        if group_id:
            query = query.where(Student.group_id == group_id)
        
        result = await self.db.execute(query)
        students = result.scalars().all()
        
        total = len(students)
        active = sum(1 for s in students if s.is_active and not s.is_graduated)
        graduated = sum(1 for s in students if s.is_graduated)
        leaders = sum(1 for s in students if s.is_leader)
        
        total_contract = sum(s.contract_amount for s in students)
        total_paid = sum(s.contract_paid for s in students)
        
        return StudentStats(
            total_students=total,
            active_students=active,
            graduated_students=graduated,
            leaders_count=leaders,
            total_contract_amount=total_contract,
            total_contract_paid=total_paid,
            payment_percentage=float(total_paid / total_contract * 100) if total_contract > 0 else 0
        )
    
    async def set_leader(self, student_id: int, is_leader: bool = True) -> Student:
        """Set or unset student as group leader."""
        student = await self.get_by_id(student_id)
        if not student:
            raise NotFoundException("Student not found")
        
        if is_leader and student.group_id:
            # Unset other leaders in the group
            await self.db.execute(
                update(Student)
                .where(Student.group_id == student.group_id)
                .where(Student.id != student_id)
                .values(is_leader=False)
            )
        
        student.is_leader = is_leader
        await self.db.commit()
        await self.db.refresh(student)
        
        return student
    
    async def graduate(self, student_id: int) -> Student:
        """Mark student as graduated."""
        student = await self.get_by_id(student_id)
        if not student:
            raise NotFoundException("Student not found")
        
        student.is_graduated = True
        student.graduation_date = date.today()
        await self.db.commit()
        
        return student
    
    async def bulk_create(self, students_data: List[StudentCreate]) -> Tuple[int, int, List[str]]:
        """
        Bulk create students.
        
        Returns:
            Tuple of (created count, skipped count, error messages)
        """
        created = 0
        skipped = 0
        errors = []
        
        for data in students_data:
            try:
                await self.create(data)
                created += 1
            except Exception as e:
                skipped += 1
                errors.append(f"{data.name}: {str(e)}")
        
        return created, skipped, errors
