"""
SQLite to PostgreSQL Migration v5
==================================
Full migration with detailed logging
"""

import sqlite3
import asyncio
from datetime import datetime, date, time


def convert_value(val, col_name, table_name=''):
    """Convert SQLite value to PostgreSQL compatible value"""
    if val is None:
        return None
    
    # Boolean
    bool_cols = ['is_active', 'is_verified', 'is_graduated', 'is_leader', 'is_cancelled', 'is_first_login', 'is_returned', 'is_borrowed', 'is_read']
    if col_name in bool_cols:
        return bool(val)
    
    # Date only
    date_only_cols = ['birth_date', 'enrollment_date', 'graduation_date', 'specific_date', 'borrow_date', 'due_date', 'return_date']
    if col_name in date_only_cols:
        if isinstance(val, str):
            try:
                return datetime.strptime(val.split()[0], '%Y-%m-%d').date()
            except:
                return None
        return val
    
    # Time only
    time_cols = ['start_time', 'end_time', 'check_in_time', 'check_out_time']
    if col_name in time_cols:
        if isinstance(val, str):
            try:
                time_str = val.split('.')[0]
                parts = time_str.split(':')
                return time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
            except:
                return None
        return val
    
    # Date for attendances/schedules
    if col_name == 'date' and table_name in ['attendances', 'schedules']:
        if isinstance(val, str):
            try:
                return datetime.strptime(val.split()[0], '%Y-%m-%d').date()
            except:
                return None
        return val
    
    # DateTime/Timestamp
    datetime_cols = ['last_login', 'created_at', 'updated_at', 'deleted_at', 'published_at', 'start_date', 'end_date', 'synced_at', 'last_sync', 'order_date', 'reviewed_at', 'joined_at', 'registered_at']
    if col_name in datetime_cols or col_name.endswith('_at'):
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val)
            except:
                try:
                    return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    try:
                        return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                    except:
                        try:
                            return datetime.strptime(val, '%Y-%m-%d')
                        except:
                            return None
        return val
    
    return val


async def migrate():
    import asyncpg
    
    # SQLite
    sqlite_conn = sqlite3.connect('unicontrol.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'")
    all_tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    print("=" * 60)
    print("SQLite to PostgreSQL Migration v5")
    print("=" * 60)
    
    table_data = {}
    for table in all_tables:
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = sqlite_cursor.fetchone()[0]
        if count > 0:
            print(f"  {table}: {count} rows")
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            columns = [desc[0] for desc in sqlite_cursor.description]
            table_data[table] = {'columns': columns, 'rows': [dict(r) for r in rows]}
    
    sqlite_conn.close()
    
    # PostgreSQL
    print("\nConnecting to PostgreSQL...")
    pg_conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='unicontrol',
        password='unicontrol_secret_2026',
        database='unicontrol'
    )
    print("Connected!")
    
    # Disable FK
    await pg_conn.execute("SET session_replication_role = replica;")
    print("FK constraints disabled")
    
    # Migration order
    order = ['users', 'groups', 'students', 'schedules', 'attendances']
    tables_to_migrate = [t for t in order if t in table_data]
    
    total_success = 0
    total_failed = 0
    
    for table in tables_to_migrate:
        data = table_data[table]
        columns = data['columns']
        rows = data['rows']
        
        print(f"\n>>> {table} ({len(rows)} rows)")
        
        # Truncate
        await pg_conn.execute(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
        
        success = 0
        errors = []
        
        for i, row in enumerate(rows):
            try:
                values = [convert_value(row.get(c), c, table) for c in columns]
                cols = ', '.join(f'"{c}"' for c in columns)
                placeholders = ', '.join([f'${j+1}' for j in range(len(columns))])
                query = f'INSERT INTO "{table}" ({cols}) VALUES ({placeholders})'
                await pg_conn.execute(query, *values)
                success += 1
            except Exception as e:
                total_failed += 1
                if len(errors) < 3:
                    errors.append(f"Row {i}: {str(e)[:100]}")
        
        total_success += success
        print(f"    ✓ {success}/{len(rows)} migrated")
        
        if errors:
            for err in errors:
                print(f"    ✗ {err}")
        
        # Commit after each table - important for FK constraints
        # Note: asyncpg autocommits by default, but we verify the count
        count = await pg_conn.fetchval(f'SELECT COUNT(*) FROM "{table}"')
        print(f"    Verified: {count} rows in PostgreSQL")
    
    # Re-enable FK
    await pg_conn.execute("SET session_replication_role = DEFAULT;")
    
    # Reset sequences
    print("\n>>> Resetting sequences...")
    for table in tables_to_migrate:
        try:
            result = await pg_conn.fetchval(f"""
                SELECT setval(pg_get_serial_sequence('"{table}"', 'id'), 
                       COALESCE((SELECT MAX(id) FROM "{table}"), 1))
            """)
            if result and result > 1:
                print(f"    {table}: {result}")
        except:
            pass
    
    await pg_conn.close()
    
    print("\n" + "=" * 60)
    print(f"Success: {total_success}, Failed: {total_failed}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(migrate())
