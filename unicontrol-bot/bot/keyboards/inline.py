from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🔍 Guruh izlash",
            callback_data="menu:search"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📋 Bugungi davomat",
            callback_data="menu:attendance"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⚙️ Sozlamalar",
            callback_data="menu:settings"
        ),
        InlineKeyboardButton(
            text="❓ Yordam",
            callback_data="menu:help"
        )
    )
    
    return builder.as_markup()


def get_subscription_keyboard(group_code: str) -> InlineKeyboardMarkup:
    """Subscription confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Obuna bo'lish",
            callback_data=f"subscribe:{group_code}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back:search"
        )
    )
    
    return builder.as_markup()


def get_search_results_keyboard(
    groups: List[Dict[str, Any]],
    page: int = 0,
    per_page: int = 5
) -> InlineKeyboardMarkup:
    """Search results with pagination"""
    builder = InlineKeyboardBuilder()
    
    # Calculate pagination
    total_pages = (len(groups) - 1) // per_page + 1
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(groups))
    
    # Group buttons
    for group in groups[start_idx:end_idx]:
        code = group.get("code", "")
        name = group.get("name", code)
        builder.row(
            InlineKeyboardButton(
                text=f"🏫 {code} - {name[:20]}",
                callback_data=f"group:{code}"
            )
        )
    
    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="◀️ Oldingi",
                callback_data=f"page:{page-1}"
            )
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Keyingi ▶️",
                callback_data=f"page:{page+1}"
            )
        )
    
    if nav_buttons:
        builder.row(*nav_buttons)
    
    # Back button
    builder.row(
        InlineKeyboardButton(
            text="🔙 Bosh menyu",
            callback_data="back:menu"
        )
    )
    
    return builder.as_markup()


def get_confirm_keyboard(
    action: str,
    data: str,
    confirm_text: str = "✅ Ha",
    cancel_text: str = "❌ Yo'q"
) -> InlineKeyboardMarkup:
    """Generic confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=confirm_text,
            callback_data=f"confirm:{action}:{data}"
        ),
        InlineKeyboardButton(
            text=cancel_text,
            callback_data=f"cancel:{action}"
        )
    )
    
    return builder.as_markup()


def get_settings_keyboard(
    subscription: Optional[Dict[str, Any]] = None
) -> InlineKeyboardMarkup:
    """Settings keyboard"""
    builder = InlineKeyboardBuilder()
    
    if subscription:
        # Notification settings
        notify_late = subscription.get("notify_late", True)
        notify_absent = subscription.get("notify_absent", True)
        notify_present = subscription.get("notify_present", False)
        
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if notify_late else '❌'} Kech qolish xabari",
                callback_data="setting:notify_late"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if notify_absent else '❌'} Kelmaslik xabari",
                callback_data="setting:notify_absent"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text=f"{'✅' if notify_present else '❌'} Kelish xabari",
                callback_data="setting:notify_present"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="🚫 Obunani bekor qilish",
                callback_data="unsubscribe"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🔍 Guruh izlash va obuna",
                callback_data="menu:search"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Bosh menyu",
            callback_data="back:menu"
        )
    )
    
    return builder.as_markup()


def get_back_keyboard(destination: str = "menu") -> InlineKeyboardMarkup:
    """Simple back button"""
    builder = InlineKeyboardBuilder()
    
    text = "🔙 Bosh menyu" if destination == "menu" else "🔙 Orqaga"
    
    builder.row(
        InlineKeyboardButton(
            text=text,
            callback_data=f"back:{destination}"
        )
    )
    
    return builder.as_markup()


def get_group_detail_keyboard(
    group_code: str,
    is_subscribed: bool = False
) -> InlineKeyboardMarkup:
    """Group detail keyboard"""
    builder = InlineKeyboardBuilder()
    
    if is_subscribed:
        builder.row(
            InlineKeyboardButton(
                text="📋 Bugungi davomat",
                callback_data=f"attendance:{group_code}"
            )
        )
        builder.row(
            InlineKeyboardButton(
                text="📊 Haftalik statistika",
                callback_data=f"stats:{group_code}"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="✅ Obuna bo'lish",
                callback_data=f"subscribe:{group_code}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back:search"
        )
    )
    
    return builder.as_markup()


def get_unsubscribe_confirm_keyboard() -> InlineKeyboardMarkup:
    """Unsubscribe confirmation"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Ha, bekor qilish",
            callback_data="confirm:unsubscribe"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Yo'q, qaytish",
            callback_data="back:settings"
        )
    )
    
    return builder.as_markup()
