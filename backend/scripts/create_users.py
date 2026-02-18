#!/usr/bin/env python3
"""
UniControl - Create Initial Users
==================================
Creates superadmin and admin users if they don't exist.
Run this at startup or manually to initialize users.
Uses current model schema: login, password_hash, name columns.
"""
import asyncio
import asyncpg
import bcrypt
import os


async def create_users():
    """Create initial users in the database."""
    # Connect to database
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=int(os.getenv('DB_PORT', '5432')),
        user=os.getenv('DB_USER', 'unicontrol'),
        password=os.getenv('DB_PASSWORD', 'unicontrol_secret_2026'),
        database=os.getenv('DB_NAME', 'unicontrol')
    )
    
    # Check if users table exists
    table_check = await conn.fetchrow("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        )
    """)
    
    if not table_check['exists']:
        print("  ⚠ Users table does not exist yet, skipping user creation")
        await conn.close()
        return
    
    print("  Using schema: login, password_hash, name")
    
    # Users to create
    users = [
        {
            'login': os.getenv('SUPERADMIN_LOGIN', 'superadmin'),
            'password': os.getenv('SUPERADMIN_PASSWORD', 'superadmin123'),
            'email': os.getenv('SUPERADMIN_EMAIL', 'superadmin@unicontrol.uz'),
            'role': 'SUPERADMIN',
            'name': os.getenv('SUPERADMIN_NAME', 'Super Admin'),
            'phone': '+998901234567'
        },
        {
            'login': os.getenv('ADMIN_LOGIN', 'admin'),
            'password': os.getenv('ADMIN_PASSWORD', 'admin123'),
            'email': os.getenv('ADMIN_EMAIL', 'admin@unicontrol.uz'),
            'role': 'ADMIN',
            'name': os.getenv('ADMIN_NAME', 'Administrator'),
            'phone': '+998901111111'
        }
    ]
    
    for user_data in users:
        # Check if user exists
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE login = $1", user_data['login']
        )
        
        # Generate password hash
        password_hash = bcrypt.hashpw(
            user_data['password'].encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        if existing:
            # User already exists — DO NOT overwrite password!
            # Parolni faqat admin panel orqali o'zgartirish kerak
            print(f"  ✓ {user_data['login']} already exists (password NOT changed)")
        else:
            # Create new user
            await conn.execute("""
                INSERT INTO users (login, email, password_hash, role, name, phone, is_active, is_verified, is_first_login, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, TRUE, TRUE, FALSE, NOW(), NOW())
            """,
                user_data['login'], 
                user_data['email'], 
                password_hash, 
                user_data['role'], 
                user_data['name'], 
                user_data['phone']
            )
            print(f"  ✓ Created {user_data['login']}")
    
    await conn.close()
    print("  ✓ Users initialization complete!")


if __name__ == "__main__":
    asyncio.run(create_users())
