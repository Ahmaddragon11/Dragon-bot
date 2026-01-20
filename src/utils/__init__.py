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
from .xp_system import (
    calculate_xp_for_level,
    check_for_level_up,
    get_level_up_message,
    get_xp_progress_bar,
    get_level_stats,
    add_xp,
    get_rank_emoji,
    get_rank_name,
    get_all_ranks,
)
from .reward_manager import reward_manager, RewardManager
from .task_manager import task_manager, TaskManager
from .message_manager import message_manager, MessageManager
from .notification_manager import notification_manager, NotificationManager, NotificationType, NotificationLevel, Notification
from .advanced_stats_manager import advanced_stats_manager, AdvancedStatsManager

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
    # xp_system
    "calculate_xp_for_level",
    "check_for_level_up",
    "get_level_up_message",
    "get_xp_progress_bar",
    "get_level_stats",
    "add_xp",
    "get_rank_emoji",
    "get_rank_name",
    "get_all_ranks",
    # managers
    "reward_manager",
    "RewardManager",
    "task_manager",
    "TaskManager",
    "message_manager",
    "MessageManager",
    "notification_manager",
    "NotificationManager",
    "NotificationType",
    "NotificationLevel",
    "Notification",
    "advanced_stats_manager",
    "AdvancedStatsManager",
]
