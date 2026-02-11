"""
Reproduce the exact subscribe flow to find the bug.
"""
import asyncio
import aiosqlite

async def test():
    db_path = r'c:\Users\user\Desktop\unicontrol\unicontrol-bot\bot.db'
    
    async with aiosqlite.connect(db_path) as db:
        # Check existing subs
        cursor = await db.execute("SELECT id, chat_id, group_code, is_active FROM subscriptions")
        rows = await cursor.fetchall()
        print("Current subscriptions:")
        for row in rows:
            print(f"  id={row[0]}, chat_id={row[1]}, group_code={row[2]}, is_active={row[3]}")
        
        # Try to INSERT another subscription for the same chat_id (simulating resubscribe)
        print("\nTrying to INSERT a new subscription with same chat_id...")
        try:
            await db.execute(
                "INSERT INTO subscriptions (chat_id, chat_title, chat_type, group_code, group_id, group_name, is_active, notify_late, notify_absent, notify_present, subscribed_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (7157341901, 'Test', 'private', 'BT_25-07', 166, 'BT_25-07', 1, 1, 1, 0, 7157341901)
            )
            print("SUCCESS - no error")
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {e}")

asyncio.run(test())
