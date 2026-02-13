"""Create contracts table."""
import asyncio
from app.database import engine
from app.models.contract import Contract
from sqlalchemy import text

async def create_table():
    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'contracts')")
        )
        exists = result.scalar()
        if exists:
            print('Table contracts already exists')
        else:
            await conn.run_sync(Contract.metadata.create_all)
            print('Table contracts created successfully')

asyncio.run(create_table())
