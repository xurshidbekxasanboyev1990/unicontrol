"""Fix all user passwords with proper bcrypt hashes"""
import asyncio
import asyncpg
import bcrypt

async def update_passwords():
    conn = await asyncpg.connect(
        host="db", port=5432,
        user="unicontrol", password="unicontrol_secret_2026",
        database="unicontrol"
    )
    
    # Admin - password: admin123
    pwd_admin = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
    await conn.execute("UPDATE users SET password_hash = $1 WHERE login = $2", pwd_admin, "admin")
    print(f"Updated admin password")
    
    # SuperAdmin - password: superadmin123
    pwd_super = bcrypt.hashpw(b"superadmin123", bcrypt.gensalt()).decode()
    await conn.execute("UPDATE users SET password_hash = $1 WHERE login = $2", pwd_super, "superadmin")
    print(f"Updated superadmin password")
    
    # Super - password: super123
    pwd_s = bcrypt.hashpw(b"super123", bcrypt.gensalt()).decode()
    await conn.execute("UPDATE users SET password_hash = $1 WHERE login = $2", pwd_s, "super")
    print(f"Updated super password")
    
    # Show all users
    users = await conn.fetch("SELECT login, role, password_hash FROM users")
    print("\n=== ALL USERS ===")
    for u in users:
        print(f"  {u[0]} ({u[1]}): {u[2][:50]}...")
    
    await conn.close()
    print("\n✓ All passwords updated!")

if __name__ == "__main__":
    asyncio.run(update_passwords())
