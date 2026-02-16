#!/bin/bash
echo "=== Student record for 519231100736 ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "
SELECT s.id, s.student_id, s.user_id, s.name, s.group_id, s.is_active
FROM students s 
JOIN users u ON s.user_id = u.id 
WHERE u.login = '519231100736';
"

echo ""
echo "=== User 519231100736 ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "
SELECT id, login, name, role FROM users WHERE login = '519231100736';
"

echo ""
echo "=== User 12940 who we actually logged in as ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "
SELECT id, login, name, role FROM users WHERE login = '519251106135';
"

echo ""
echo "=== What does student profile endpoint actually return? ==="
TOKEN=$(curl -s -X POST 'http://localhost:5173/api/v1/auth/login' -H 'Content-Type: application/json' -d '{"login":"519231100736","password":"519231100736"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','FAILED'))" 2>/dev/null)
echo "Token user ID:"
echo "$TOKEN" | python3 -c "import sys,json,base64; t=sys.stdin.read().strip(); payload=t.split('.')[1]; payload+='='*(4-len(payload)%4); d=json.loads(base64.urlsafe_b64decode(payload)); print(json.dumps(d, indent=2))" 2>/dev/null

echo ""
echo "Full profile response:"
curl -s 'http://localhost:5173/api/mobile/student/profile' -H "Authorization: Bearer $TOKEN" | python3 -m json.tool 2>/dev/null

echo ""
echo "=== Is there a student linked to user 3? ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "
SELECT s.id, s.student_id, s.user_id, s.name, s.group_id 
FROM students s WHERE s.user_id = 3;
"
