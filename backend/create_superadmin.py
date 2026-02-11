"""Create SuperAdmin only"""
import asyncio
from passlib.context import CryptContext
import asyncpg

async def create_superadmin():
    ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
    password_hash = ctx.hash('super123')
    
    conn = await asyncpg.connect(
        host='db', port=5432,
        user='unicontrol', password='unicontrol_secret_2026',
        database='unicontrol'
    )
    
    # Create superadmin
    await conn.execute('''
        INSERT INTO users (login, email, password_hash, role, name, phone, is_active, is_verified, is_first_login, created_at, updated_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, NOW(), NOW())
        ON CONFLICT (login) DO NOTHING
    ''', 'super', 'super@unicontrol.uz', password_hash, 'SUPERADMIN', 'Super Admin', '+998901234567', True, True, False)
    
    result = await conn.fetchrow('SELECT id, login, email, role, name FROM users WHERE login = $1', 'super')
    print(f'SuperAdmin created!')
    print(f'  Login: {result["login"]}')
    print(f'  Password: super123')
    print(f'  Email: {result["email"]}')
    print(f'  Role: {result["role"]}')
    
    await conn.close()

if __name__ == '__main__':
    asyncio.run(create_superadmin())
