"""
Fix stale leaders - reset role to 'student' for users who are no longer group leaders.

Usage: python fix_stale_leaders.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select, text
from app.database import async_engine, AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.group import Group


async def fix_stale_leaders():
    """Find users with role=leader who are NOT actually leading any group, reset to student."""
    async with AsyncSessionLocal() as db:
        # Get all users with role=leader
        result = await db.execute(
            select(User).where(User.role == UserRole.LEADER)
        )
        leader_users = result.scalars().all()
        
        print(f"Found {len(leader_users)} users with role=leader")
        
        fixed = 0
        for user in leader_users:
            # Check if this user is actually a leader of any group
            # Method 1: Check by user_id in students table -> student.is_leader
            student_res = await db.execute(
                select(Student).where(Student.user_id == user.id)
            )
            student = student_res.scalar_one_or_none()
            
            is_actual_leader = False
            
            if student and student.group_id:
                # Check if their group's leader_id points to this student
                grp_res = await db.execute(
                    select(Group).where(
                        Group.id == student.group_id,
                        Group.leader_id == student.id
                    )
                )
                grp = grp_res.scalar_one_or_none()
                if grp:
                    is_actual_leader = True
            
            if not is_actual_leader:
                print(f"  FIXING: user_id={user.id}, login={user.login}, name={user.name} -> student")
                user.role = UserRole.STUDENT
                if student:
                    student.is_leader = False
                fixed += 1
            else:
                print(f"  OK: user_id={user.id}, login={user.login}, name={user.name} (actual leader of group {student.group_id})")
        
        if fixed > 0:
            await db.commit()
            print(f"\n✅ Fixed {fixed} stale leader(s) -> set to student")
        else:
            print(f"\n✅ No stale leaders found, all {len(leader_users)} are actual group leaders")


if __name__ == "__main__":
    asyncio.run(fix_stale_leaders())
