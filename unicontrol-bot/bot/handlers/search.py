from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from bot.services import UniControlAPI, AttendanceFormatter
from bot.keyboards import get_search_results_keyboard, get_group_detail_keyboard
from bot.database import async_session, GroupCache
from sqlalchemy import select

router = Router(name="search")
logger = logging.getLogger(__name__)

api = UniControlAPI()


class SearchStates(StatesGroup):
    """Search FSM states"""
    waiting_for_query = State()


@router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext):
    """
    Handle /search command.
    Usage: /search KI_25-09 or /search
    """
    # Extract query from command
    args = message.text.split(maxsplit=1)
    
    if len(args) > 1:
        # Query provided in command
        query = args[1].strip()
        await perform_search(message, query, state)
    else:
        # Ask for query
        await state.set_state(SearchStates.waiting_for_query)
        await message.answer(
            "🔍 <b>Guruh qidirish</b>\n\n"
            "Guruh kodini yoki nomini kiriting:\n"
            "<i>Masalan: KI_25-09 yoki Kompyuter</i>",
            parse_mode="HTML"
        )


@router.message(SearchStates.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    """Process search query from user"""
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer(
            "⚠️ Kamida 2 ta belgi kiriting",
            parse_mode="HTML"
        )
        return
    
    await perform_search(message, query, state)


async def perform_search(message: Message, query: str, state: FSMContext):
    """Perform group search"""
    await state.clear()
    
    # Show searching message
    searching_msg = await message.answer(
        f"🔍 <b>\"{query}\"</b> qidirilmoqda...",
        parse_mode="HTML"
    )
    
    try:
        # Search via API
        groups = await api.search_groups(query)
        
        if not groups:
            # Try exact code match
            group = await api.get_group_by_code(query.upper())
            if group:
                groups = [group]
        
        # Delete searching message
        await searching_msg.delete()
        
        if not groups:
            await message.answer(
                f"❌ <b>\"{query}\"</b> bo'yicha guruh topilmadi.\n\n"
                "💡 <i>To'g'ri kod kiritganingizni tekshiring.\n"
                "Masalan: KI_25-09, ATM_24-01</i>",
                parse_mode="HTML"
            )
            return
        
        # Cache groups
        await cache_groups(groups)
        
        # Store search results in state for pagination
        await state.update_data(
            search_results=groups,
            search_query=query,
            current_page=0
        )
        
        # Format and send results
        result_text = AttendanceFormatter.format_search_results(groups, query)
        keyboard = get_search_results_keyboard(groups, page=0)
        
        await message.answer(
            result_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await searching_msg.delete()
        await message.answer(
            "❌ Qidirishda xatolik yuz berdi.\n"
            "Iltimos, keyinroq qayta urinib ko'ring.",
            parse_mode="HTML"
        )


async def cache_groups(groups: list):
    """Cache groups in database"""
    async with async_session() as session:
        for group in groups:
            try:
                # Check if exists
                result = await session.execute(
                    select(GroupCache).where(
                        GroupCache.api_group_id == group.get("id")
                    )
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    cache_entry = GroupCache(
                        api_group_id=group.get("id"),
                        code=group.get("code", ""),
                        name=group.get("name", ""),
                        faculty=group.get("faculty", ""),
                        course=group.get("course"),
                        student_count=group.get("student_count", 0)
                    )
                    session.add(cache_entry)
            except Exception as e:
                logger.error(f"Cache error: {e}")
                continue
        
        await session.commit()


@router.callback_query(F.data.startswith("group:"))
async def callback_group_detail(callback: CallbackQuery, state: FSMContext):
    """Show group details"""
    group_code = callback.data.split(":")[1]
    
    try:
        # Get group info
        group = await api.get_group_by_code(group_code)
        
        if not group:
            await callback.answer("Guruh topilmadi", show_alert=True)
            return
        
        # Check if already subscribed
        from bot.database import Subscription
        async with async_session() as session:
            result = await session.execute(
                select(Subscription).where(
                    Subscription.chat_id == callback.message.chat.id,
                    Subscription.group_code == group_code,
                    Subscription.is_active == True
                )
            )
            is_subscribed = result.scalar_one_or_none() is not None
        
        # Format group info
        text = AttendanceFormatter.format_group_info(group)
        keyboard = get_group_detail_keyboard(group_code, is_subscribed)
        
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Group detail error: {e}")
        await callback.answer("Xatolik yuz berdi", show_alert=True)


@router.callback_query(F.data.startswith("page:"))
async def callback_pagination(callback: CallbackQuery, state: FSMContext):
    """Handle pagination"""
    page = int(callback.data.split(":")[1])
    
    # Get stored search results
    data = await state.get_data()
    groups = data.get("search_results", [])
    query = data.get("search_query", "")
    
    if not groups:
        await callback.answer("Qidiruv natijalari topilmadi", show_alert=True)
        return
    
    # Update current page
    await state.update_data(current_page=page)
    
    # Update message
    result_text = AttendanceFormatter.format_search_results(groups, query)
    keyboard = get_search_results_keyboard(groups, page=page)
    
    await callback.message.edit_text(
        result_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()
