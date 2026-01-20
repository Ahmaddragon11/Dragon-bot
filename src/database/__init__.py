"""
وحدة قاعدة البيانات للبوت Dragon-bot.

تصدر جميع وظائف التفاعل مع قاعدة البيانات.
"""

from .manager import (
    init_db,
    get_user,
    get_user_by_referral_code,
    save_user,
    get_all_users,
    get_top_users_by_points,
    get_top_users_by_level,
    get_total_users_count,
    get_banned_users_count,
    get_active_users_count,
    get_referral_count,
    get_top_users_by_referrals,
    find_user_by_username,
    delete_user,
)

__all__ = [
    "init_db",
    "get_user",
    "get_user_by_referral_code",
    "save_user",
    "get_all_users",
    "get_top_users_by_points",
    "get_top_users_by_level",
    "get_total_users_count",
    "get_banned_users_count",
    "get_active_users_count",
    "get_referral_count",
    "get_top_users_by_referrals",
    "find_user_by_username",
    "delete_user",
]
