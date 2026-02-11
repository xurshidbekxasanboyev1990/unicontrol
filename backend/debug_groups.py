"""
Debug groups migration
"""
import sqlite3
import asyncio
from datetime import datetime

async def debug_groups():
    # SQLite
    sqlite_conn = sqlite3.connect('unicontrol.db')
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()
    
    cur.execute("SELECT * FROM groups LIMIT 3")
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    
    print("SQLite columns:", columns)
    print("\nFirst 3 rows:")
    for row in rows:
        print(dict(row))
    
    sqlite_conn.close()
    
    # PostgreSQL
    import asyncpg
    pg_conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='unicontrol',
        password='unicontrol_secret_2026',
        database='unicontrol'
    )
    
    # Delete test row
    await pg_conn.execute("DELETE FROM groups WHERE name = 'Test-01'")
    
    # Check current count
    count = await pg_conn.fetchval("SELECT COUNT(*) FROM groups")
    print(f"\nPostgreSQL groups count: {count}")
    
    # Try inserting one row manually
    sqlite_conn = sqlite3.connect('unicontrol.db')
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()
    cur.execute("SELECT * FROM groups LIMIT 1")
    row = dict(cur.fetchone())
    sqlite_conn.close()
    
    print(f"\nTrying to insert row: {row}")
    
    # Convert values
    def convert(val, col):
        if val is None:
            return None
        if col in ['is_active']:
            return bool(val)
        if col in ['created_at', 'updated_at'] and isinstance(val, str):
            try:
                return datetime.fromisoformat(val)
            except:
                return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
        return val
    
    values = [convert(row.get(col), col) for col in columns]
    print(f"\nConverted values:")
    for i, col in enumerate(columns):
        print(f"  {col}: {type(values[i]).__name__} = {values[i]}")
    
    cols_str = ', '.join(f'"{c}"' for c in columns)
    placeholders = ', '.join([f'${i+1}' for i in range(len(columns))])
    query = f'INSERT INTO groups ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
    
    print(f"\nQuery: {query}")
    
    try:
        await pg_conn.execute(query, *values)
        print("\n✓ Insert successful!")
        
        new_count = await pg_conn.fetchval("SELECT COUNT(*) FROM groups")
        print(f"New count: {new_count}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    
    await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(debug_groups())
