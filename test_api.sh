#!/bin/bash
# Test Mobile API endpoints

BASE="http://localhost:5173"

echo "=== 1. V1 Login ==="
TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"admin123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
echo "Token: ${TOKEN:0:50}..."

if [ "$TOKEN" = "FAILED" ] || [ -z "$TOKEN" ]; then
  echo "Login failed, trying superadmin..."
  TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"login":"superadmin","password":"superadmin123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
  echo "Token: ${TOKEN:0:50}..."
fi

if [ "$TOKEN" = "FAILED" ] || [ -z "$TOKEN" ]; then
  echo "=== Trying mobile auth ==="
  TOKEN=$(curl -s -X POST "$BASE/api/mobile/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123","device_token":"test","device_type":"android"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
  echo "Token: ${TOKEN:0:50}..."
fi

if [ "$TOKEN" = "FAILED" ] || [ -z "$TOKEN" ]; then
  echo ""
  echo "=== All login attempts failed. Checking available users ==="
  curl -s -X POST "$BASE/api/v1/auth/login" -H "Content-Type: application/json" -d '{"login":"admin","password":"admin123"}' | python3 -m json.tool 2>/dev/null
  echo ""
  curl -s -X POST "$BASE/api/v1/auth/login" -H "Content-Type: application/json" -d '{"login":"superadmin","password":"superadmin123"}' | python3 -m json.tool 2>/dev/null
  echo ""
  curl -s -X POST "$BASE/api/mobile/auth/login" -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123","device_token":"test","device_type":"android"}' | python3 -m json.tool 2>/dev/null
  exit 1
fi

AUTH="Authorization: Bearer $TOKEN"

echo ""
echo "=== 2. Mobile /groups (no auth) ==="
curl -s "$BASE/api/mobile/groups" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Groups: {len(d)} items')" 2>/dev/null

echo ""
echo "=== 3. Mobile /schedule (auth) ==="
curl -s "$BASE/api/mobile/schedule" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 4. Mobile /attendance (auth) ==="
curl -s "$BASE/api/mobile/attendance" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 5. Mobile /notifications/unread-count (auth) ==="
curl -s "$BASE/api/mobile/notifications/unread-count" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:300])" 2>/dev/null

echo ""
echo "=== 6. V1 /users/me ==="
curl -s "$BASE/api/v1/users/me" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 7. Mobile /auth/me ==="
curl -s "$BASE/api/mobile/auth/me" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 8. Mobile /student/profile ==="
curl -s "$BASE/api/mobile/student/profile" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 9. Mobile /student/dashboard ==="
curl -s "$BASE/api/mobile/student/dashboard" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 10. Mobile /student/schedule/today ==="
curl -s "$BASE/api/mobile/student/schedule/today" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 11. Mobile /student/schedule/week ==="
curl -s "$BASE/api/mobile/student/schedule/week" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 12. Mobile /student/attendance ==="
curl -s "$BASE/api/mobile/student/attendance" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 13. Mobile /student/notifications ==="
curl -s "$BASE/api/mobile/student/notifications" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:500])" 2>/dev/null

echo ""
echo "=== 14. V1 /notifications/unread-count ==="
curl -s "$BASE/api/v1/notifications/unread-count" -H "$AUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:300])" 2>/dev/null

echo ""
echo "=== DONE ==="
