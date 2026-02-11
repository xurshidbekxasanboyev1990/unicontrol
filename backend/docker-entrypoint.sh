#!/bin/bash
# ========================================
# UniControl Backend Entrypoint
# ========================================
# Bu skript Docker konteyner ishga tushganda bajariladi
# 1. Database ga ulanishni tekshiradi
# 2. Alembic migratsiyalarni ishga tushiradi
# 3. Userlarni yaratadi (agar mavjud bo'lmasa)
# 4. Uvicorn serverni ishga tushiradi

set -e

echo "=================================="
echo " UniControl Backend Starting..."
echo "=================================="

# Database ga ulanishni kutish
echo "[1/4] Waiting for database to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if python -c "
import asyncio
import asyncpg
import os

async def check_db():
    try:
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST', 'db'),
            port=int(os.getenv('DB_PORT', '5432')),
            user=os.getenv('DB_USER', 'unicontrol'),
            password=os.getenv('DB_PASSWORD', 'unicontrol_secret_2026'),
            database=os.getenv('DB_NAME', 'unicontrol')
        )
        await conn.close()
        return True
    except:
        return False

result = asyncio.run(check_db())
exit(0 if result else 1)
" 2>/dev/null; then
        echo "  ✓ Database is ready!"
        break
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Waiting for database... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "  ✗ Could not connect to database after $MAX_RETRIES attempts"
    exit 1
fi

# Database jadvallarini yaratish (Alembic o'rniga init_db ishlatamiz)
echo "[2/4] Creating database tables..."
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
print('  ✓ Database tables created!')
" || echo "  ⚠ Table creation had issues (may already exist)"

# Userlarni yaratish
echo "[3/4] Creating initial users..."
if [ -f "scripts/create_users.py" ]; then
    python scripts/create_users.py || echo "  ⚠ User creation skipped"
else
    echo "  ⚠ create_users.py not found, skipping"
fi

# Uvicorn serverni ishga tushirish
echo "[4/4] Starting Uvicorn server..."
echo "=================================="
echo " Server ready at http://0.0.0.0:8000"
echo "=================================="

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
