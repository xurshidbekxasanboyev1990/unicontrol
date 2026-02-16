#!/bin/bash
# Check DB users and backend issues

echo "=== Users in DB ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "SELECT id, login, role, name FROM users LIMIT 20;"

echo ""
echo "=== Students in DB ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "SELECT s.id, s.user_id, u.login, u.name, s.group_id FROM students s JOIN users u ON s.user_id = u.id LIMIT 10;"

echo ""
echo "=== Leaders in DB ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "SELECT l.id, l.user_id, u.login, u.name FROM leaders l JOIN users u ON l.user_id = u.id LIMIT 10;"

echo ""
echo "=== Backend logs (last 30 lines) ==="
docker logs unicontrol_backend --tail 30 2>&1
