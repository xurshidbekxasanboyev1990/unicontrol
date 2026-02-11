import sqlite3
conn = sqlite3.connect(r'c:\Users\user\Desktop\unicontrol\unicontrol-bot\bot.db')
cursor = conn.execute("SELECT * FROM subscriptions")
rows = cursor.fetchall()
print(f"Subscriptions ({len(rows)}):")
for row in rows:
    print(f"  {row}")
conn.close()
