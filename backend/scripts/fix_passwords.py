#!/usr/bin/env python3
"""
Fix user passwords in database with correct bcrypt hashes.
Run this inside the backend container.
"""
import asyncio
import asyncpg
import bcrypt
import os

async def fix_passwords():
    """Fix passwords for all users."""
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=int(os.getenv('DB_PORT', '5432')),
        user=os.getenv('DB_USER', 'unicontrol'),
        password=os.getenv('DB_PASSWORD', 'unicontrol_secret_2026'),
        database=os.getenv('DB_NAME', 'unicontrol')
    )
    
    # Define users and their passwords
    users = [
        ('superadmin', 'superadmin123'),
        ('admin', 'admin123'),
    ]
    
    for login, password in users:
        # Generate correct bcrypt hash
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Update user
        await conn.execute(
            'UPDATE users SET password_hash = $1 WHERE login = $2',
            password_hash, 
            login
        )
        print(f"Updated {login} with hash: {password_hash[:40]}...")
    
    # Verify
    print("\n--- Verification ---")
    rows = await conn.fetch('SELECT login, password_hash FROM users')
    for row in rows:
        print(f"{row['login']}: {row['password_hash'][:50]}...")
    
    await conn.close()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(fix_passwords())
