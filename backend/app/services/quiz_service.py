"""
UniControl - Quiz Service
==========================
Business logic for quiz/flashcard operations.
"""

import logging
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.quiz import QuizSet, QuizCard, QuizResult
from app.models.student import Student
from app.schemas.quiz import (
    QuizSetCreate, QuizSetUpdate,
    QuizCardCreate, QuizCardUpdate,
    QuizResultCreate,
)

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ============ QuizSet CRUD ============

    async def create_set(self, data: QuizSetCreate, creator_id: int, group_id: Optional[int] = None) -> QuizSet:
        """Create a quiz set with cards."""
        quiz_set = QuizSet(
            title=data.title,
            description=data.description,
            subject=data.subject,
            is_public=data.is_public,
            color=data.color,
            creator_id=creator_id,
            group_id=group_id,
            cards_count=len(data.cards) if data.cards else 0,
        )
        self.db.add(quiz_set)
        await self.db.flush()

        # Add cards
        if data.cards:
            for i, card_data in enumerate(data.cards):
                card = QuizCard(
                    quiz_set_id=quiz_set.id,
                    question=card_data.question,
                    answer=card_data.answer,
                    answer_type=card_data.answer_type,
                    options=card_data.options,
                    correct_option=card_data.correct_option,
                    hint=card_data.hint,
                    order=card_data.order or i,
                )
                self.db.add(card)

        await self.db.commit()
        await self.db.refresh(quiz_set)
        return await self.get_set_by_id(quiz_set.id)

    async def get_set_by_id(self, set_id: int) -> Optional[QuizSet]:
        """Get quiz set with all cards."""
        result = await self.db.execute(
            select(QuizSet).where(QuizSet.id == set_id)
        )
        return result.unique().scalar_one_or_none()

    async def list_sets(
        self,
        page: int = 1,
        page_size: int = 20,
        group_id: Optional[int] = None,
        creator_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[QuizSet], int]:
        """List quiz sets with filters."""
        query = select(QuizSet)

        filters = []
        if group_id:
            # Show sets from this group OR public sets
            filters.append(
                or_(QuizSet.group_id == group_id, QuizSet.is_public == True)
            )
        if creator_id:
            filters.append(QuizSet.creator_id == creator_id)
        if search:
            filters.append(
                or_(
                    QuizSet.title.ilike(f"%{search}%"),
                    QuizSet.subject.ilike(f"%{search}%"),
                    QuizSet.description.ilike(f"%{search}%"),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Count
        count_q = select(func.count(QuizSet.id))
        if filters:
            count_q = count_q.where(and_(*filters))
        count_result = await self.db.execute(count_q)
        total = count_result.scalar() or 0

        # Paginate
        query = query.order_by(QuizSet.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        sets = result.unique().scalars().all()

        return sets, total

    async def update_set(self, set_id: int, data: QuizSetUpdate) -> Optional[QuizSet]:
        """Update quiz set."""
        quiz_set = await self.get_set_by_id(set_id)
        if not quiz_set:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(quiz_set, key, value)

        await self.db.commit()
        return await self.get_set_by_id(set_id)

    async def delete_set(self, set_id: int) -> bool:
        """Delete quiz set and all its cards."""
        quiz_set = await self.get_set_by_id(set_id)
        if not quiz_set:
            return False

        await self.db.delete(quiz_set)
        await self.db.commit()
        return True

    # ============ QuizCard CRUD ============

    async def add_card(self, set_id: int, data: QuizCardCreate) -> Optional[QuizCard]:
        """Add a card to a quiz set."""
        quiz_set = await self.get_set_by_id(set_id)
        if not quiz_set:
            return None

        card = QuizCard(
            quiz_set_id=set_id,
            question=data.question,
            answer=data.answer,
            answer_type=data.answer_type,
            options=data.options,
            correct_option=data.correct_option,
            hint=data.hint,
            order=data.order or len(quiz_set.cards),
        )
        self.db.add(card)

        # Update count
        quiz_set.cards_count = len(quiz_set.cards) + 1
        
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def update_card(self, card_id: int, data: QuizCardUpdate) -> Optional[QuizCard]:
        """Update a quiz card."""
        result = await self.db.execute(
            select(QuizCard).where(QuizCard.id == card_id)
        )
        card = result.scalar_one_or_none()
        if not card:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(card, key, value)

        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def delete_card(self, card_id: int) -> bool:
        """Delete a quiz card."""
        result = await self.db.execute(
            select(QuizCard).where(QuizCard.id == card_id)
        )
        card = result.scalar_one_or_none()
        if not card:
            return False

        set_id = card.quiz_set_id
        await self.db.delete(card)
        
        # Update count
        quiz_set = await self.get_set_by_id(set_id)
        if quiz_set:
            quiz_set.cards_count = len(quiz_set.cards) - 1
        
        await self.db.commit()
        return True

    # ============ QuizResult ============

    async def save_result(self, data: QuizResultCreate, user_id: int) -> QuizResult:
        """Save a quiz result."""
        result = QuizResult(
            quiz_set_id=data.quiz_set_id,
            user_id=user_id,
            total_questions=data.total_questions,
            correct_answers=data.correct_answers,
            score_percentage=data.score_percentage,
            time_spent_seconds=data.time_spent_seconds,
            mode=data.mode,
        )
        self.db.add(result)

        # Increment play count
        quiz_set = await self.get_set_by_id(data.quiz_set_id)
        if quiz_set:
            quiz_set.play_count = (quiz_set.play_count or 0) + 1

        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def get_results(
        self,
        quiz_set_id: Optional[int] = None,
        user_id: Optional[int] = None,
        limit: int = 20,
    ) -> List[QuizResult]:
        """Get quiz results."""
        query = select(QuizResult)
        if quiz_set_id:
            query = query.where(QuizResult.quiz_set_id == quiz_set_id)
        if user_id:
            query = query.where(QuizResult.user_id == user_id)
        
        query = query.order_by(QuizResult.completed_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return result.unique().scalars().all()

    async def get_user_group_id(self, user_id: int) -> Optional[int]:
        """Get the group_id for a user (through student table)."""
        result = await self.db.execute(
            select(Student.group_id).where(Student.user_id == user_id)
        )
        row = result.first()
        return row[0] if row else None
