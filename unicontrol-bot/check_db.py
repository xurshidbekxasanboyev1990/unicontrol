import sqlite3
conn = sqlite3.connect(r'c:\Users\user\Desktop\unicontrol\unicontrol-bot\bot.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)
for table in tables:
    tname = table[0]
    cursor2 = conn.execute(f"PRAGMA table_info({tname})")
    cols = cursor2.fetchall()
    print(f"\n--- {tname} ---")
    for col in cols:
        print(f"  {col}")
conn.close()
