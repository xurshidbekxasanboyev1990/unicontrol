"""Admin panel keyboards"""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_main_menu() -> InlineKeyboardMarkup:
    """Main admin panel menu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📊 Statistika",
            callback_data="admin:stats"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📢 E'lon yuborish",
            callback_data="admin:broadcast"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📺 Majburiy obuna",
            callback_data="admin:channels"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="⚙️ Bot sozlamalari",
            callback_data="admin:settings"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="👥 Foydalanuvchilar",
            callback_data="admin:users"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📋 Loglar",
            callback_data="admin:logs"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Yopish",
            callback_data="admin:close"
        )
    )
    
    return builder.as_markup()


def get_admin_stats_keyboard() -> InlineKeyboardMarkup:
    """Statistics submenu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📈 Bugungi statistika",
            callback_data="admin:stats:today"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📊 Haftalik statistika",
            callback_data="admin:stats:week"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📉 Oylik statistika",
            callback_data="admin:stats:month"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:back:main"
        )
    )
    
    return builder.as_markup()


def get_admin_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Broadcast submenu"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✏️ Yangi e'lon",
            callback_data="admin:broadcast:new"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📋 Faol e'lonlar",
            callback_data="admin:broadcast:active"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📜 E'lonlar tarixi",
            callback_data="admin:broadcast:history"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:back:main"
        )
    )
    
    return builder.as_markup()


def get_admin_channels_keyboard(
    channels: List[Dict[str, Any]]
) -> InlineKeyboardMarkup:
    """Mandatory channels list"""
    builder = InlineKeyboardBuilder()
    
    # List existing channels
    for channel in channels:
        status = "✅" if channel.get("is_active") else "❌"
        title = channel.get("channel_title", "Channel")[:25]
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {title}",
                callback_data=f"admin:channel:{channel.get('id')}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="➕ Kanal qo'shish",
            callback_data="admin:channel:add"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:back:main"
        )
    )
    
    return builder.as_markup()


def get_channel_detail_keyboard(
    channel_id: int,
    is_active: bool
) -> InlineKeyboardMarkup:
    """Channel detail/edit keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Toggle active status
    if is_active:
        builder.row(
            InlineKeyboardButton(
                text="❌ O'chirish",
                callback_data=f"admin:channel:toggle:{channel_id}"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="✅ Yoqish",
                callback_data=f"admin:channel:toggle:{channel_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="🗑 O'chirib tashlash",
            callback_data=f"admin:channel:delete:{channel_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:channels"
        )
    )
    
    return builder.as_markup()


def get_admin_settings_keyboard(settings: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Bot settings keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Bot status
    bot_status = "✅ Faol" if settings.get("is_active", True) else "❌ O'chirilgan"
    builder.row(
        InlineKeyboardButton(
            text=f"🤖 Bot: {bot_status}",
            callback_data="admin:settings:toggle:is_active"
        )
    )
    
    # Maintenance mode
    maint_status = "✅ Yoqilgan" if settings.get("maintenance_mode") else "❌ O'chirilgan"
    builder.row(
        InlineKeyboardButton(
            text=f"🔧 Ta'mirlash: {maint_status}",
            callback_data="admin:settings:toggle:maintenance_mode"
        )
    )
    
    # Force subscribe
    sub_status = "✅ Yoqilgan" if settings.get("force_subscribe") else "❌ O'chirilgan"
    builder.row(
        InlineKeyboardButton(
            text=f"📺 Majburiy obuna: {sub_status}",
            callback_data="admin:settings:toggle:force_subscribe"
        )
    )
    
    # Notifications
    notif_status = "✅ Yoqilgan" if settings.get("notifications_enabled", True) else "❌ O'chirilgan"
    builder.row(
        InlineKeyboardButton(
            text=f"🔔 Bildirishnomalar: {notif_status}",
            callback_data="admin:settings:toggle:notifications_enabled"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="✏️ Xush kelibsiz xabari",
            callback_data="admin:settings:edit:welcome"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="✏️ Ta'mirlash xabari",
            callback_data="admin:settings:edit:maintenance"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="✏️ Obuna xabari",
            callback_data="admin:settings:edit:subscribe"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:back:main"
        )
    )
    
    return builder.as_markup()


def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Users management keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🔍 Foydalanuvchi izlash",
            callback_data="admin:users:search"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🚫 Bloklangan foydalanuvchilar",
            callback_data="admin:users:banned"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📊 Top faol foydalanuvchilar",
            callback_data="admin:users:top"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:back:main"
        )
    )
    
    return builder.as_markup()


def get_user_detail_keyboard(
    user_id: int,
    is_banned: bool
) -> InlineKeyboardMarkup:
    """User detail/management keyboard"""
    builder = InlineKeyboardBuilder()
    
    if is_banned:
        builder.row(
            InlineKeyboardButton(
                text="✅ Blokdan chiqarish",
                callback_data=f"admin:user:unban:{user_id}"
            )
        )
    else:
        builder.row(
            InlineKeyboardButton(
                text="🚫 Bloklash",
                callback_data=f"admin:user:ban:{user_id}"
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="💬 Xabar yuborish",
            callback_data=f"admin:user:message:{user_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:users"
        )
    )
    
    return builder.as_markup()


def get_broadcast_confirm_keyboard(broadcast_id: int) -> InlineKeyboardMarkup:
    """Broadcast confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Yuborish",
            callback_data=f"admin:broadcast:confirm:{broadcast_id}"
        ),
        InlineKeyboardButton(
            text="❌ Bekor qilish",
            callback_data=f"admin:broadcast:cancel:{broadcast_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="👁 Ko'rib chiqish",
            callback_data=f"admin:broadcast:preview:{broadcast_id}"
        )
    )
    
    return builder.as_markup()


def get_broadcast_progress_keyboard(broadcast_id: int) -> InlineKeyboardMarkup:
    """Broadcast progress keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="⏹ To'xtatish",
            callback_data=f"admin:broadcast:stop:{broadcast_id}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔄 Yangilash",
            callback_data=f"admin:broadcast:refresh:{broadcast_id}"
        )
    )
    
    return builder.as_markup()


def get_confirm_keyboard(
    action: str,
    data: str
) -> InlineKeyboardMarkup:
    """Generic confirmation keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Ha",
            callback_data=f"admin:confirm:{action}:{data}"
        ),
        InlineKeyboardButton(
            text="❌ Yo'q",
            callback_data=f"admin:cancel:{action}"
        )
    )
    
    return builder.as_markup()


def get_force_subscribe_keyboard(
    channels: List[Dict[str, Any]]
) -> InlineKeyboardMarkup:
    """Keyboard for users to subscribe to mandatory channels"""
    builder = InlineKeyboardBuilder()
    
    for channel in channels:
        url = channel.get("channel_url") or f"https://t.me/{channel.get('channel_username', '').lstrip('@')}"
        builder.row(
            InlineKeyboardButton(
                text=f"📺 {channel.get('channel_title', 'Kanal')}",
                url=url
            )
        )
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Tekshirish",
            callback_data="check_subscription"
        )
    )
    
    return builder.as_markup()


def get_admin_logs_keyboard() -> InlineKeyboardMarkup:
    """Logs menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📋 So'nggi loglar",
            callback_data="admin:logs:recent"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔍 Log izlash",
            callback_data="admin:logs:search"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="admin:back:main"
        )
    )
    
    return builder.as_markup()
