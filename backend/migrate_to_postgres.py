"""
SQLite to PostgreSQL Migration Script
=====================================
Migrates all data from SQLite to PostgreSQL
"""

import sqlite3
import asyncio
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, '.')

async def migrate():
    """Migrate all data from SQLite to PostgreSQL"""
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('unicontrol.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all tables
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version'")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    print("=" * 50)
    print("SQLite Tables Found:")
    print("=" * 50)
    
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
    
    print("\n" + "=" * 50)
    print("Connecting to PostgreSQL...")
    print("=" * 50)
    
    # Now connect to PostgreSQL
    try:
        import asyncpg
        
        # PostgreSQL connection
        pg_conn = await asyncpg.connect(
            host='localhost',
            port=5432,
            user='unicontrol',
            password='unicontrol_secret_2026',
            database='unicontrol'
        )
        
        print("Connected to PostgreSQL!")
        
        # Check existing tables
        existing_tables = await pg_conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        existing_table_names = [t['tablename'] for t in existing_tables]
        print(f"Existing PostgreSQL tables: {existing_table_names}")
        
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
        
        print(f"\nTables to migrate: {tables_to_migrate}")
        
        for table in tables_to_migrate:
            if table not in table_data:
                continue
                
            data = table_data[table]
            columns = data['columns']
            rows = data['rows']
            
            if not rows:
                continue
            
            print(f"\nMigrating {table} ({len(rows)} rows)...")
            
            # Clear existing data
            try:
                await pg_conn.execute(f"TRUNCATE TABLE {table} CASCADE")
            except Exception as e:
                print(f"  Warning: Could not truncate {table}: {e}")
            
            # Insert data
            success_count = 0
            for row in rows:
                try:
                    # Build INSERT query
                    cols = ', '.join(columns)
                    placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
                    values = [row.get(col) for col in columns]
                    
                    # Convert datetime strings to datetime objects
                    for i, (col, val) in enumerate(zip(columns, values)):
                        if val and isinstance(val, str) and ('_at' in col or '_date' in col):
                            try:
                                values[i] = datetime.fromisoformat(val.replace('Z', '+00:00'))
                            except:
                                pass
                    
                    query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                    await pg_conn.execute(query, *values)
                    success_count += 1
                except Exception as e:
                    print(f"  Error inserting row: {e}")
                    print(f"  Row data: {row}")
            
            print(f"  Migrated {success_count}/{len(rows)} rows")
        
        # Reset sequences
        print("\nResetting sequences...")
        for table in tables_to_migrate:
            try:
                await pg_conn.execute(f"""
                    SELECT setval(pg_get_serial_sequence('{table}', 'id'), 
                           COALESCE((SELECT MAX(id) FROM {table}), 1))
                """)
            except:
                pass
        
        await pg_conn.close()
        print("\n" + "=" * 50)
        print("Migration completed successfully!")
        print("=" * 50)
        
    except ImportError:
        print("asyncpg not installed. Installing...")
        import subprocess
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'asyncpg'])
        print("Please run the script again.")
    except Exception as e:
        print(f"PostgreSQL Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(migrate())
