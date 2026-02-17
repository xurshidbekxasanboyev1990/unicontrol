"""
Update all user passwords:
- admin role users: xur*963.
- all other users: 12345678
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy import select, update
from app.database import async_session
from app.models.user import User
from app.core.security import get_password_hash


async def main():
    admin_hash = get_password_hash("xur*963.")
    user_hash = get_password_hash("12345678")
    
    async with async_session() as db:
        # Update admin passwords
        result = await db.execute(
            update(User)
            .where(User.role == 'admin')
            .values(password=admin_hash)
        )
        print(f"Admin parollar yangilandi: {result.rowcount} ta")
        
        # Update all non-admin passwords (student, leader, superadmin - all get 12345678)
        result2 = await db.execute(
            update(User)
            .where(User.role != 'admin')
            .values(password=user_hash)
        )
        print(f"Boshqa userlar parollari yangilandi: {result2.rowcount} ta")
        
        await db.commit()
        print("Barcha parollar muvaffaqiyatli yangilandi!")


if __name__ == "__main__":
    asyncio.run(main())
