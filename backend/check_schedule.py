import asyncio
from sqlalchemy import select, func
from app.database import async_session_maker
from app.models.schedule import Schedule
from app.models.group import Group

async def main():
    async with async_session_maker() as db:
        # Find the group
        r = await db.execute(select(Group).where(Group.name == "FTO'(rus)_24-04"))
        g = r.scalar_one_or_none()
        if not g:
            print("Group FTO'(rus)_24-04 not found!")
            return
        print(f"Group: {g.name}, ID: {g.id}")

        # Check schedules
        r2 = await db.execute(select(Schedule).where(Schedule.group_id == g.id))
        schedules = r2.scalars().all()
        print(f"Schedules count: {len(schedules)}")
        for s in schedules[:10]:
            print(f"  {s.day_of_week.value} | lesson={s.lesson_number} | {s.subject} | {s.teacher_name} | {s.start_time}-{s.end_time}")

        # Total schedules in DB
        r3 = await db.execute(select(func.count(Schedule.id)))
        total = r3.scalar()
        print(f"\nTotal schedules in DB: {total}")

        # Groups with schedules
        r4 = await db.execute(select(func.count(func.distinct(Schedule.group_id))))
        gws = r4.scalar()
        print(f"Groups with schedules: {gws}")

asyncio.run(main())
