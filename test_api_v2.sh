#!/bin/bash
# Full Mobile API Test - v2
BASE="http://localhost:5173"

echo "========================================="
echo "  UniControl Mobile API Test Suite v2"
echo "========================================="
echo ""

# --- Test 1: Login as admin ---
echo "=== 1. V1 Login (admin) ==="
ADMIN_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"admin","password":"admin123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
echo "Admin Token: ${ADMIN_TOKEN:0:40}..."

# --- Test 2: Login as student ---
echo ""
echo "=== 2. V1 Login (student: 519231100736) ==="
STUDENT_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"519231100736","password":"519231100736"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
if [ "$STUDENT_TOKEN" = "FAILED" ] || [ -z "$STUDENT_TOKEN" ]; then
  echo "Default password failed. Trying others..."
  STUDENT_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"login":"519231100736","password":"password123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
fi
if [ "$STUDENT_TOKEN" = "FAILED" ] || [ -z "$STUDENT_TOKEN" ]; then
  echo "Trying hemis password..."
  STUDENT_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"login":"519231100736","password":"12345678"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
fi
echo "Student Token: ${STUDENT_TOKEN:0:40}..."

# --- Test 3: Login as leader ---
echo ""
echo "=== 3. V1 Login (leader: 519251106223) ==="
LEADER_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"login":"519251106223","password":"519251106223"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
if [ "$LEADER_TOKEN" = "FAILED" ] || [ -z "$LEADER_TOKEN" ]; then
  LEADER_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"login":"519251106223","password":"password123"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
fi
if [ "$LEADER_TOKEN" = "FAILED" ] || [ -z "$LEADER_TOKEN" ]; then
  LEADER_TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"login":"519251106223","password":"12345678"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
fi
echo "Leader Token: ${LEADER_TOKEN:0:40}..."

echo ""
echo "==========================================="
echo "  ADMIN ENDPOINTS"
echo "==========================================="

AAUTH="Authorization: Bearer $ADMIN_TOKEN"

echo ""
echo "=== A1. /api/mobile/auth/me ==="
curl -s "$BASE/api/mobile/auth/me" -H "$AAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  ID:{d.get(\"id\")} Login:{d.get(\"login\")} Role:{d.get(\"role\")}')" 2>/dev/null

echo ""
echo "=== A2. /api/v1/users/me ==="
curl -s "$BASE/api/v1/users/me" -H "$AAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  ID:{d.get(\"id\")} Login:{d.get(\"login\")} Role:{d.get(\"role\")}')" 2>/dev/null

echo ""
echo "=== A3. /api/mobile/groups ==="
curl -s "$BASE/api/mobile/groups" | python3 -c "import sys,json; d=json.load(sys.stdin); items=d.get('items',[]); print(f'  Groups: {len(items)} items')" 2>/dev/null

echo ""
echo "=== A4. /api/mobile/notifications/unread-count ==="
curl -s "$BASE/api/mobile/notifications/unread-count" -H "$AAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Unread: {d.get(\"count\")}')" 2>/dev/null

echo ""
echo "=== A5. /api/v1/notifications/unread-count ==="
curl -s "$BASE/api/v1/notifications/unread-count" -H "$AAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Unread: {d.get(\"count\")}')" 2>/dev/null

echo ""
echo "=== A6. /api/v1/notifications ==="
curl -s "$BASE/api/v1/notifications?page_size=3" -H "$AAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Total: {d.get(\"total\")}, Unread: {d.get(\"unread_count\")}')" 2>/dev/null

echo ""
echo "==========================================="
echo "  STUDENT ENDPOINTS"
echo "==========================================="

if [ "$STUDENT_TOKEN" != "FAILED" ] && [ -n "$STUDENT_TOKEN" ]; then
  SAUTH="Authorization: Bearer $STUDENT_TOKEN"

  echo ""
  echo "=== S1. /api/mobile/student/profile ==="
  curl -s "$BASE/api/mobile/student/profile" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Name:{d.get(\"full_name\")} Group:{d.get(\"group_id\")}')" 2>/dev/null

  echo ""
  echo "=== S2. /api/mobile/student/dashboard ==="
  curl -s "$BASE/api/mobile/student/dashboard" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:400])" 2>/dev/null

  echo ""
  echo "=== S3. /api/mobile/student/schedule/today ==="
  curl -s "$BASE/api/mobile/student/schedule/today" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); classes=d.get('classes',[]); print(f'  Day:{d.get(\"day\")} Classes:{len(classes)}'); [print(f'    {c[\"start_time\"]}-{c[\"end_time\"]} {c[\"subject\"]}') for c in classes[:5]]" 2>/dev/null

  echo ""
  echo "=== S4. /api/mobile/student/schedule/week ==="
  curl -s "$BASE/api/mobile/student/schedule/week" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {k}: {len(v)} classes') for k,v in d.items() if isinstance(v, list)]" 2>/dev/null

  echo ""
  echo "=== S5. /api/mobile/student/attendance ==="
  curl -s "$BASE/api/mobile/student/attendance?days=7" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); recs=d.get('records',[]); stats=d.get('stats',{}); print(f'  Records:{len(recs)} Stats:{stats}')" 2>/dev/null

  echo ""
  echo "=== S6. /api/mobile/student/notifications ==="
  curl -s "$BASE/api/mobile/student/notifications" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); n=d.get('notifications',[]); print(f'  Total:{d.get(\"total\")} Notifications:{len(n)}')" 2>/dev/null

  echo ""
  echo "=== S7. /api/mobile/schedule (generic) ==="
  curl -s "$BASE/api/mobile/schedule" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  {k}: {len(v)} classes') for k,v in d.items() if isinstance(v, list)]" 2>/dev/null

  echo ""
  echo "=== S8. /api/mobile/attendance (generic) ==="
  curl -s "$BASE/api/mobile/attendance?days=7" -H "$SAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); recs=d.get('records',[]); print(f'  Records: {len(recs)}')" 2>/dev/null

else
  echo "  *** SKIPPED: Student login failed ***"
fi

echo ""
echo "==========================================="
echo "  LEADER ENDPOINTS"
echo "==========================================="

if [ "$LEADER_TOKEN" != "FAILED" ] && [ -n "$LEADER_TOKEN" ]; then
  LAUTH="Authorization: Bearer $LEADER_TOKEN"

  echo ""
  echo "=== L1. /api/mobile/auth/me ==="
  curl -s "$BASE/api/mobile/auth/me" -H "$LAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  ID:{d.get(\"id\")} Login:{d.get(\"login\")} Role:{d.get(\"role\")}')" 2>/dev/null

  echo ""
  echo "=== L2. /api/mobile/leader/dashboard ==="
  curl -s "$BASE/api/mobile/leader/dashboard" -H "$LAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:400])" 2>/dev/null

  echo ""
  echo "=== L3. /api/mobile/leader/students ==="
  curl -s "$BASE/api/mobile/leader/students" -H "$LAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); items=d.get('students',d.get('items',[])); print(f'  Students: {len(items)}')" 2>/dev/null

  echo ""
  echo "=== L4. /api/mobile/leader/schedule/today ==="
  curl -s "$BASE/api/mobile/leader/schedule/today" -H "$LAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); classes=d.get('classes',[]); print(f'  Day:{d.get(\"day\")} Classes:{len(classes)}')" 2>/dev/null

  echo ""
  echo "=== L5. /api/mobile/leader/attendance/today ==="
  curl -s "$BASE/api/mobile/leader/attendance/today" -H "$LAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); items=d.get('attendance',d.get('items',[])); print(f'  Records: {len(items)}')" 2>/dev/null

  echo ""
  echo "=== L6. /api/mobile/leader/stats/week ==="
  curl -s "$BASE/api/mobile/leader/stats/week" -H "$LAUTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False)[:400])" 2>/dev/null

else
  echo "  *** SKIPPED: Leader login failed ***"
fi

echo ""
echo "==========================================="
echo "  V1 ENDPOINTS (used by mobile)"
echo "==========================================="

echo ""
echo "=== V1. PUT /notifications/{id}/read ==="
curl -s -X PUT "$BASE/api/v1/notifications/1/read" -H "$AAUTH" -o /dev/null -w "  HTTP Status: %{http_code}" 2>/dev/null
echo ""

echo ""
echo "=== V2. PUT /notifications/read-all ==="
curl -s -X PUT "$BASE/api/v1/notifications/read-all" -H "$AAUTH" -o /dev/null -w "  HTTP Status: %{http_code}" 2>/dev/null
echo ""

echo ""
echo "=== V3. Mobile auth /login ==="
curl -s -X POST "$BASE/api/mobile/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123","device_token":"test","device_type":"android"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'  Token: {str(d.get(\"access_token\",\"FAILED\"))[:40]}')" 2>/dev/null

echo ""
echo "==========================================="
echo "  TEST COMPLETE"
echo "==========================================="
