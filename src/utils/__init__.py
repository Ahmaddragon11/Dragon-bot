"""
وحدة المساعدات والأدوات للبوت Dragon-bot.

تصدر جميع وظائف المساعدة والأدوات المستخدمة عبر المشروع.
"""

from .helpers import (
    generate_referral_code,
    is_admin,
    get_admin_ids,
    format_number,
    truncate_text,
    escape_markdown,
    calculate_level_from_xp,
    calculate_xp_to_next_level,
)
from .exceptions import (
    DragonBotException,
    UserNotFound,
    UserAlreadyExists,
    UserBanned,
    InvalidReferralCode,
    InsufficientPoints,
    DatabaseError,
    ConfigurationError,
    RewardNotFound,
    TaskNotFound,
    InvalidOperation,
    PermissionDenied,
)

__all__ = [
    # helpers
    "generate_referral_code",
    "is_admin",
    "get_admin_ids",
    "format_number",
    "truncate_text",
    "escape_markdown",
    "calculate_level_from_xp",
    "calculate_xp_to_next_level",
    # exceptions
    "DragonBotException",
    "UserNotFound",
    "UserAlreadyExists",
    "UserBanned",
    "InvalidReferralCode",
    "InsufficientPoints",
    "DatabaseError",
    "ConfigurationError",
    "RewardNotFound",
    "TaskNotFound",
    "InvalidOperation",
    "PermissionDenied",
]
