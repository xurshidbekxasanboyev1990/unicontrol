"""
Create demo users for testing
Run: python create_demo_users.py
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.database import async_session_maker, init_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_demo_users():
    """Create demo users for testing."""
    
    # Initialize database
    await init_db()
    
    demo_users = [
        {
            "login": "student",
            "email": "student@uni.uz",
            "password": "123456",
            "name": "Aliyev Jasur",
            "role": UserRole.STUDENT,
            "phone": "+998901234567"
        },
        {
            "login": "sardor",
            "email": "sardor@uni.uz", 
            "password": "123456",
            "name": "Karimov Sardor",
            "role": UserRole.LEADER,
            "phone": "+998912345678"
        },
        {
            "login": "admin",
            "email": "admin@uni.uz",
            "password": "123456",
            "name": "Toshmatov Admin",
            "role": UserRole.ADMIN,
            "phone": "+998933456789"
        },
        {
            "login": "super",
            "email": "super@uni.uz",
            "password": "123456",
            "name": "Super Administrator",
            "role": UserRole.SUPERADMIN,
            "phone": "+998944567890"
        }
    ]
    
    async with async_session_maker() as session:
        for user_data in demo_users:
            # Check if user exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.login == user_data["login"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"User '{user_data['login']}' already exists, skipping...")
                continue
            
            # Create user
            user = User(
                login=user_data["login"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"],
                phone=user_data["phone"],
                is_active=True,
                is_verified=True
            )
            session.add(user)
            print(f"Created user: {user_data['login']} ({user_data['role'].value})")
        
        await session.commit()
    
    print("\n" + "="*50)
    print("Demo users created successfully!")
    print("="*50)
    print("\nLogin credentials:")
    print("-"*50)
    for user in demo_users:
        print(f"  {user['role'].value:12} -> login: {user['login']:10} password: {user['password']}")
    print("-"*50)


if __name__ == "__main__":
    asyncio.run(create_demo_users())
