"""
SQLite to PostgreSQL Migration Script v2
=========================================
Properly handles data type conversions
"""

import sqlite3
import asyncio
import sys
from datetime import datetime, date, time

sys.path.insert(0, '.')

def convert_value(val, col_name):
    """Convert SQLite value to PostgreSQL compatible value"""
    if val is None:
        return None
    
    # Boolean conversion (SQLite uses 0/1)
    bool_cols = ['is_active', 'is_verified', 'is_graduated', 'is_leader', 'is_cancelled']
    if col_name in bool_cols:
        return bool(val)
    
    # Date conversion
    if col_name in ['date', 'birth_date', 'enrollment_date', 'graduation_date', 'specific_date']:
        if isinstance(val, str):
            try:
                return datetime.strptime(val.split()[0], '%Y-%m-%d').date()
            except:
                return None
        return val
    
    # Time conversion
    if col_name in ['start_time', 'end_time', 'check_in_time', 'check_out_time']:
        if isinstance(val, str):
            try:
                time_str = val.split('.')[0]  # Remove microseconds
                parts = time_str.split(':')
                return time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
            except:
                return None
        return val
    
    # DateTime conversion
    if '_at' in col_name and isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace('Z', '+00:00').replace(' ', 'T'))
        except:
            try:
                return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
            except:
                try:
                    return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                except:
                    return None
    
    return val


async def migrate():
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('unicontrol.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    print("=" * 60)
    print("SQLite to PostgreSQL Migration v2")
    print("=" * 60)
    
    table_data = {}
    for table in tables:
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = sqlite_cursor.fetchone()[0]
        print(f"  {table}: {count} rows")
        
        if count > 0:
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            columns = [description[0] for description in sqlite_cursor.description]
            table_data[table] = {
                'columns': columns,
                'rows': [dict(row) for row in rows]
            }
    
    sqlite_conn.close()
    
    print("\n" + "=" * 60)
    print("Connecting to PostgreSQL...")
    print("=" * 60)
    
    try:
        import asyncpg
        
        pg_conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='unicontrol',
            password='unicontrol_secret_2026',
            database='unicontrol'
        )
        
        print("Connected to PostgreSQL!")
        
        # Migration order (respecting foreign keys)
        migration_order = [
            'users',
            'groups', 
            'students',
            'subjects',
            'directions',
            'direction_subjects',
            'schedules',
            'attendance',
            'attendances',
            'clubs',
            'club_members',
            'tournaments',
            'tournament_participants',
            'notifications',
            'activity_logs',
            'system_settings',
            'ai_analysis_results',
            'ai_recommendations',
            'reports',
            'files'
        ]
        
        # Filter to only tables that exist in SQLite
        tables_to_migrate = [t for t in migration_order if t in table_data]
        
        # Add any tables not in the order
        for t in table_data:
            if t not in tables_to_migrate:
                tables_to_migrate.append(t)
        
        print(f"\nMigrating tables: {tables_to_migrate}")
        
        total_success = 0
        total_failed = 0
        
        for table in tables_to_migrate:
            if table not in table_data:
                continue
                
            data = table_data[table]
            columns = data['columns']
            rows = data['rows']
            
            if not rows:
                continue
            
            print(f"\n>>> Migrating {table} ({len(rows)} rows)...")
            
            # Disable foreign key checks and truncate
            try:
                await pg_conn.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                print(f"    Truncated {table}")
            except Exception as e:
                print(f"    Warning: Could not truncate {table}: {e}")
            
            # Insert data in batches
            success_count = 0
            batch_size = 100
            
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                
                for row in batch:
                    try:
                        # Convert values
                        values = []
                        for col in columns:
                            val = convert_value(row.get(col), col)
                            values.append(val)
                        
                        # Build INSERT query
                        cols = ', '.join(f'"{c}"' for c in columns)
                        placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
                        
                        query = f'INSERT INTO "{table}" ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
                        await pg_conn.execute(query, *values)
                        success_count += 1
                    except Exception as e:
                        if success_count == 0:  # Only print first error per table
                            print(f"    Error: {e}")
                            print(f"    Sample row: {list(row.keys())[:5]}...")
                        total_failed += 1
            
            total_success += success_count
            print(f"    ✓ Migrated {success_count}/{len(rows)} rows")
        
        # Reset all sequences
        print("\n>>> Resetting sequences...")
        for table in tables_to_migrate:
            try:
                result = await pg_conn.fetchval(f"""
                    SELECT setval(pg_get_serial_sequence('"{table}"', 'id'), 
                           COALESCE((SELECT MAX(id) FROM "{table}"), 1))
                """)
                if result:
                    print(f"    {table}: sequence set to {result}")
            except:
                pass
        
        await pg_conn.close()
        
        print("\n" + "=" * 60)
        print(f"Migration Summary:")
        print(f"  Total Success: {total_success}")
        print(f"  Total Failed: {total_failed}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(migrate())
