"""Update passwords for super and admin users"""
import asyncio
from passlib.context import CryptContext
import asyncpg

async def update_passwords():
    ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
    new_hash = ctx.hash('super123')
    print(f'Generated hash: {new_hash}')
    
    conn = await asyncpg.connect(
        host='db',
        port=5432, 
        user='unicontrol', 
        password='unicontrol_secret_2026', 
        database='unicontrol'
    )
    
    await conn.execute('UPDATE users SET password_hash = $1 WHERE login = $2', new_hash, 'super')
    await conn.execute('UPDATE users SET password_hash = $1 WHERE login = $2', new_hash, 'admin')
    
    result = await conn.fetchrow('SELECT login, password_hash FROM users WHERE login = $1', 'super')
    print(f'Updated super: {result["login"]} -> {result["password_hash"][:30]}...')
    
    await conn.close()
    print('Done!')

if __name__ == '__main__':
    asyncio.run(update_passwords())
