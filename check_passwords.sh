#!/bin/bash
docker exec unicontrol_db psql -U unicontrol -d unicontrol -c "SELECT id, login, role, plain_password FROM users WHERE login IN ('519231100736', '519251106223', 'admin') ORDER BY id;"
