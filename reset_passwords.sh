#!/bin/bash
# Reset passwords for test users
docker exec unicontrol_backend python3 -c "
import bcrypt

users = {
    '519231100736': '519231100736',
    '519251106223': '519251106223',
}

for login, password in users.items():
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f\"UPDATE users SET password_hash='{hashed}', plain_password='{password}' WHERE login='{login}';\")
" | docker exec -i unicontrol_db psql -U unicontrol -d unicontrol

echo "Passwords reset done."

# Verify by trying login
echo ""
echo "=== Verify student login ==="
curl -s -X POST 'http://localhost:5173/api/v1/auth/login' -H 'Content-Type: application/json' -d '{"login":"519231100736","password":"519231100736"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Token: {str(d.get(\"access_token\",\"FAILED\"))[:40]}')" 2>/dev/null

echo ""
echo "=== Verify leader login ==="
curl -s -X POST 'http://localhost:5173/api/v1/auth/login' -H 'Content-Type: application/json' -d '{"login":"519251106223","password":"519251106223"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Token: {str(d.get(\"access_token\",\"FAILED\"))[:40]}')" 2>/dev/null
