"""
UniControl - Database Seeder
============================
Creates initial superadmin user.

Usage: python -m scripts.seed_db
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import async_session_maker, init_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_superadmin(
    username: str = "superadmin",
    email: str = "superadmin@unicontrol.uz",
    password: str = "SuperAdmin123!",
    full_name: str = "Super Administrator"
) -> User:
    """
    Create superadmin user if not exists.
    """
    async with async_session_maker() as session:
        # Check if superadmin exists
        result = await session.execute(
            select(User).where(User.role == UserRole.SUPERADMIN)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"Superadmin already exists: {existing.login}")
            return existing
        
        # Create superadmin
        superadmin = User(
            login=username,
            email=email,
            password_hash=get_password_hash(password),
            name=full_name,
            role=UserRole.SUPERADMIN,
            is_active=True,
            is_verified=True
        )
        
        session.add(superadmin)
        await session.commit()
        await session.refresh(superadmin)
        
        print(f"✅ Superadmin created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"\n⚠️  Please change the password after first login!")
        
        return superadmin


async def seed_demo_data(session: AsyncSession):
    """
    Seed demo data for development (optional).
    """
    from app.models.group import Group
    from app.models.student import Student
    
    # Create demo group
    demo_group = Group(
        name="Demo Group",
        code="DEMO-001",
        faculty="Information Technology",
        course=1,
        academic_year="2025-2026",
        is_active=True
    )
    session.add(demo_group)
    await session.flush()
    
    # Create demo leader
    leader_user = User(
        login="leader",
        email="leader@unicontrol.uz",
        password_hash=get_password_hash("Leader123!"),
        name="Demo Leader",
        role=UserRole.LEADER,
        is_active=True,
        is_verified=True
    )
    session.add(leader_user)
    await session.flush()
    
    # Assign leader to group
    demo_group.leader_id = leader_user.id
    
    # Create demo admin
    admin_user = User(
        login="admin",
        email="admin@unicontrol.uz",
        password_hash=get_password_hash("Admin123!"),
        name="Demo Admin",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    session.add(admin_user)
    await session.flush()
    
    # Create demo students
    student_names = [
        "Alisher Karimov",
        "Malika Rahimova",
        "Bobur Toshmatov",
        "Dilnoza Ergasheva",
        "Jasur Normatov"
    ]
    
    for i, name in enumerate(student_names, 1):
        student_user = User(
            login=f"student{i}",
            email=f"student{i}@unicontrol.uz",
            password_hash=get_password_hash(f"Student{i}23!"),
            name=name,
            role=UserRole.STUDENT,
            is_active=True,
            is_verified=True
        )
        session.add(student_user)
        await session.flush()
        
        student = Student(
            user_id=student_user.id,
            group_id=demo_group.id,
            hemis_id=f"HEMIS{100000 + i}",
            student_id=f"STU{100000 + i}",
            full_name=name,
            email=f"student{i}@unicontrol.uz",
            is_active=True
        )
        session.add(student)
    
    await session.commit()
    print("✅ Demo data seeded successfully!")


async def main():
    """Main function."""
    print("=" * 50)
    print("UniControl Database Seeder")
    print("=" * 50)
    
    # Initialize database tables
    print("\n📦 Initializing database...")
    await init_db()
    print("✅ Database initialized!")
    
    # Create superadmin
    print("\n👤 Creating superadmin user...")
    await create_superadmin()
    
    # Ask for demo data
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("\n📊 Seeding demo data...")
        async with async_session_maker() as session:
            await seed_demo_data(session)
    
    print("\n" + "=" * 50)
    print("Seeding completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
