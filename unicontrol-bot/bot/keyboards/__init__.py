"""Keyboards module"""

from .inline import (
    get_main_menu_keyboard,
    get_subscription_keyboard,
    get_search_results_keyboard,
    get_confirm_keyboard,
    get_settings_keyboard,
    get_back_keyboard,
    get_group_detail_keyboard,
    get_unsubscribe_confirm_keyboard
)

from .admin import (
    get_admin_main_menu,
    get_admin_stats_keyboard,
    get_admin_broadcast_keyboard,
    get_admin_channels_keyboard,
    get_channel_detail_keyboard,
    get_admin_settings_keyboard,
    get_admin_users_keyboard,
    get_user_detail_keyboard,
    get_broadcast_confirm_keyboard,
    get_broadcast_progress_keyboard,
    get_force_subscribe_keyboard,
    get_admin_logs_keyboard
)

__all__ = [
    "get_main_menu_keyboard",
    "get_subscription_keyboard", 
    "get_search_results_keyboard",
    "get_confirm_keyboard",
    "get_settings_keyboard",
    "get_back_keyboard",
    "get_group_detail_keyboard",
    "get_unsubscribe_confirm_keyboard",
    # Admin keyboards
    "get_admin_main_menu",
    "get_admin_stats_keyboard",
    "get_admin_broadcast_keyboard",
    "get_admin_channels_keyboard",
    "get_channel_detail_keyboard",
    "get_admin_settings_keyboard",
    "get_admin_users_keyboard",
    "get_user_detail_keyboard",
    "get_broadcast_confirm_keyboard",
    "get_broadcast_progress_keyboard",
    "get_force_subscribe_keyboard",
    "get_admin_logs_keyboard"
]
