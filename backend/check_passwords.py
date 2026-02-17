"""Check superadmin password"""
import asyncio
import sys
sys.path.insert(0, '/app')

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User
from app.core.security import verify_password, get_password_hash


async def main():
    async with async_session_maker() as db:
        # Check superadmin
        r = await db.execute(select(User).where(User.login == "superadmin"))
        u = r.scalar_one_or_none()
        if u:
            print(f"Login: {u.login}, Role: {u.role}")
            print(f"Hash prefix: {u.password_hash[:30]}...")
            print(f"Plain password: {u.plain_password}")
            print(f"Verify '12345678': {verify_password('12345678', u.password_hash)}")
            print(f"Verify 'superadmin123': {verify_password('superadmin123', u.password_hash)}")
        else:
            print("superadmin user topilmadi!")
        
        # Check admin
        r2 = await db.execute(select(User).where(User.login == "admin"))
        u2 = r2.scalar_one_or_none()
        if u2:
            print(f"\nLogin: {u2.login}, Role: {u2.role}")
            print(f"Hash prefix: {u2.password_hash[:30]}...")
            print(f"Plain password: {u2.plain_password}")
            print(f"Verify 'xur*963.': {verify_password('xur*963.', u2.password_hash)}")
        else:
            print("admin user topilmadi!")


if __name__ == "__main__":
    asyncio.run(main())
