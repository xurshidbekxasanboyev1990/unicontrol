"""
Update all user passwords:
- admin role users: xur*963.
- all other users: 12345678
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User
from app.core.security import get_password_hash, verify_password


async def main():
    superadmin_hash = get_password_hash("xur*963.")
    admin_hash = get_password_hash("admin123")
    user_hash = get_password_hash("12345678")
    
    async with async_session_maker() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        superadmin_count = 0
        admin_count = 0
        other_count = 0
        
        for user in users:
            if user.role.value == 'superadmin':
                user.password_hash = superadmin_hash
                user.plain_password = 'xur*963.'
                superadmin_count += 1
            elif user.role.value == 'admin':
                user.password_hash = admin_hash
                user.plain_password = 'admin123'
                admin_count += 1
            else:
                user.password_hash = user_hash
                user.plain_password = '12345678'
                other_count += 1
        
        await db.commit()
        print(f"Superadmin parollar yangilandi: {superadmin_count} ta")
        print(f"Admin parollar yangilandi: {admin_count} ta")
        print(f"Boshqa userlar parollari yangilandi: {other_count} ta")
        
        # Verify
        r = await db.execute(select(User).where(User.login == "superadmin"))
        u = r.scalar_one_or_none()
        if u:
            print(f"Verify superadmin 'xur*963.': {verify_password('xur*963.', u.password_hash)}")
        
        r2 = await db.execute(select(User).where(User.login == "admin"))
        u2 = r2.scalar_one_or_none()
        if u2:
            print(f"Verify admin 'admin123': {verify_password('admin123', u2.password_hash)}")


if __name__ == "__main__":
    asyncio.run(main())
