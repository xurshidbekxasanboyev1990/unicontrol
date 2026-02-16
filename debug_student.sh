#!/bin/bash
echo "=== Student record for user 519231100736 ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "
SELECT s.id, s.user_id, s.full_name, s.hemis_id, s.email, s.phone, s.group_id, s.is_active, s.contract_number
FROM students s 
JOIN users u ON s.user_id = u.id 
WHERE u.login = '519231100736';
"

echo ""
echo "=== Student table columns ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "\d students" | head -30

echo ""
echo "=== Leader's group assignment ==="
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "
SELECT g.id, g.name, g.leader_id, u.login as leader_login 
FROM groups g 
JOIN users u ON g.leader_id = u.id 
WHERE u.login = '519251106223';
"

echo ""
echo "=== Backend error logs ==="
docker logs unicontrol_backend --tail 15 2>&1 | grep -i "error\|traceback\|attribute"
