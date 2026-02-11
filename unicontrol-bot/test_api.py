import asyncio
import aiohttp

async def test():
    headers = {
        'X-Bot-Token': '8054399827:AAGaRNC5qu4QdrFxzokTCBPnMXWKBJtAS9I',
        'Content-Type': 'application/json'
    }
    async with aiohttp.ClientSession(headers=headers) as s:
        # Test 1: Get group by code
        print("=== Test 1: get_group_by_code('BT_25-07') ===")
        async with s.get('http://localhost:8000/api/v1/telegram/groups/code/BT_25-07') as r:
            print(f"Status: {r.status}")
            text = await r.text()
            print(f"Response: {text}")
        
        # Test 2: Check bot subscription for group (need group_id from Test 1)
        import json
        if r.status == 200:
            data = json.loads(text)
            group_id = data.get("id")
            print(f"\n=== Test 2: check_bot_subscription(group_id={group_id}) ===")
            async with s.get(f'http://localhost:8000/api/v1/telegram/bot-check-subscription/{group_id}') as r2:
                print(f"Status: {r2.status}")
                text2 = await r2.text()
                print(f"Response: {text2}")

asyncio.run(test())
