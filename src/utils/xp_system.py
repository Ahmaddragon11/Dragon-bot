"""
وحدة منطق نظام المستويات والخبرة.

تحتوي على وظائف لحساب المستويات والخبرة والرتب
والتحقق من الترقيات والإحصائيات المتعلقة بها.
"""

import logging
from typing import Tuple, Dict, Any
from src.core.config import XP_PER_LEVEL, MAX_LEVEL
from src.utils.exceptions import InvalidOperation

logger: logging.Logger = logging.getLogger(__name__)


# تعريفات الرتب حسب المستوى
RANKS = {
    1: "🥚 مبتدئ",
    5: "🐣 ناشئ",
    10: "🦅 فارس",
    15: "🐉 محارب",
    20: "👑 فارس التنين",
    25: "⭐ نجم",
    30: "🌟 لاعب محترف",
    50: "🏆 بطل",
    100: "👑 إمبراطور",
}


def calculate_rank_for_level(level: int) -> str:
    """
    حساب الرتبة بناءً على المستوى.
    
    Args:
        level (int): المستوى الحالي
        
    Returns:
        str: اسم الرتبة مع رمزها
    """
    current_rank = "🥚 مبتدئ"
    
    for level_threshold in sorted(RANKS.keys(), reverse=True):
        if level >= level_threshold:
            current_rank = RANKS[level_threshold]
            break
    
    return current_rank


def calculate_level_from_xp(experience: int) -> int:
    """
    حساب المستوى بناءً على نقاط الخبرة الإجمالية.
    
    Args:
        experience (int): إجمالي نقاط الخبرة
        
    Returns:
        int: المستوى الحالي (الحد الأدنى: 1، الحد الأقصى: MAX_LEVEL)
    """
    if experience < 0:
        return 1
    
    level = (experience // XP_PER_LEVEL) + 1
    return min(level, MAX_LEVEL)


def calculate_xp_for_level(level: int) -> int:
    """
    حساب إجمالي نقاط الخبرة المطلوبة للوصول إلى مستوى معين.
    
    Args:
        level (int): المستوى المطلوب
        
    Returns:
        int: إجمالي نقاط الخبرة المطلوبة
    """
    if level <= 1:
        return 0
    
    # معادلة: كل مستوى يحتاج XP_PER_LEVEL نقطة
    return (level - 1) * XP_PER_LEVEL


def calculate_xp_progress(current_xp: int) -> Tuple[int, int, int]:
    """
    حساب تقدم الخبرة في المستوى الحالي.
    
    Args:
        current_xp (int): نقاط الخبرة الحالية
        
    Returns:
        Tuple[int, int, int]: (المستوى الحالي، نقاط الخبرة في المستوى، نقاط الخبرة المتبقية)
    """
    current_level = calculate_level_from_xp(current_xp)
    xp_needed_for_level = calculate_xp_for_level(current_level)
    xp_in_current_level = current_xp - xp_needed_for_level
    xp_remaining = XP_PER_LEVEL - xp_in_current_level
    
    return current_level, xp_in_current_level, max(0, xp_remaining)


def check_for_level_up(old_xp: int, new_xp: int) -> Tuple[bool, int]:
    """
    التحقق من حدوث ارتقاء مستوى بين نقطتي خبرة.
    
    Args:
        old_xp (int): نقاط الخبرة القديمة
        new_xp (int): نقاط الخبرة الجديدة
        
    Returns:
        Tuple[bool, int]: (هل حدث ارتقاء؟، المستوى الجديد)
    """
    old_level = calculate_level_from_xp(old_xp)
    new_level = calculate_level_from_xp(new_xp)
    
    level_up = new_level > old_level
    return level_up, new_level


def get_level_up_message(old_level: int, new_level: int) -> str:
    """
    الحصول على رسالة تهنئة بالارتقاء إلى مستوى جديد.
    
    Args:
        old_level (int): المستوى القديم
        new_level (int): المستوى الجديد
        
    Returns:
        str: رسالة التهنئة
    """
    levels_gained = new_level - old_level
    new_rank = calculate_rank_for_level(new_level)
    
    if levels_gained == 1:
        message = (
            f"🎉 **تهانينا! لقد ارتقيت مستوى!**\n\n"
            f"المستوى الجديد: {new_level}\n"
            f"الرتبة: {new_rank}"
        )
    else:
        message = (
            f"🎉 **تهانينا! لقد ارتقيت {levels_gained} مستويات!**\n\n"
            f"المستوى الجديد: {new_level}\n"
            f"الرتبة: {new_rank}"
        )
    
    return message


def get_xp_progress_bar(current_xp: int, bar_length: int = 10) -> str:
    """
    إنشاء شريط تقدم الخبرة.
    
    Args:
        current_xp (int): نقاط الخبرة الحالية
        bar_length (int): طول الشريط
        
    Returns:
        str: شريط التقدم مع النسبة المئوية
    """
    _, xp_in_level, xp_remaining = calculate_xp_progress(current_xp)
    
    total_xp_in_level = XP_PER_LEVEL
    filled = int((xp_in_level / total_xp_in_level) * bar_length)
    empty = bar_length - filled
    
    bar = "█" * filled + "░" * empty
    percentage = int((xp_in_level / total_xp_in_level) * 100)
    
    return f"{bar} {percentage}%"


def get_level_stats(level: int, experience: int) -> Dict[str, Any]:
    """
    الحصول على إحصائيات شاملة عن المستوى والخبرة.
    
    Args:
        level (int): المستوى الحالي
        experience (int): نقاط الخبرة الحالية
        
    Returns:
        Dict[str, Any]: قاموس يحتوي على الإحصائيات
    """
    current_level, xp_in_level, xp_remaining = calculate_xp_progress(experience)
    rank = calculate_rank_for_level(level)
    
    # حساب النسبة المئوية للمستوى التالي
    progress_percentage = (xp_in_level / XP_PER_LEVEL) * 100
    
    return {
        "level": level,
        "experience": experience,
        "rank": rank,
        "xp_in_level": xp_in_level,
        "xp_remaining": xp_remaining,
        "progress_percentage": progress_percentage,
        "xp_per_level": XP_PER_LEVEL,
        "max_level": MAX_LEVEL,
        "is_max_level": level >= MAX_LEVEL,
    }


def add_xp(current_xp: int, xp_to_add: int) -> Tuple[int, bool, int]:
    """
    إضافة نقاط خبرة والتحقق من الارتقاء.
    
    Args:
        current_xp (int): نقاط الخبرة الحالية
        xp_to_add (int): نقاط الخبرة المراد إضافتها
        
    Returns:
        Tuple[int, bool, int]: (الخبرة الجديدة، هل حدث ارتقاء؟، المستوى الجديد)
    """
    if xp_to_add < 0:
        raise InvalidOperation("لا يمكن إضافة نقاط خبرة سالبة")
    
    old_level = calculate_level_from_xp(current_xp)
    new_xp = current_xp + xp_to_add
    
    # الحد الأقصى للخبرة (حسب الحد الأقصى للمستويات)
    max_xp = calculate_xp_for_level(MAX_LEVEL + 1)
    new_xp = min(new_xp, max_xp)
    
    new_level = calculate_level_from_xp(new_xp)
    level_up = new_level > old_level
    
    logger.debug(
        f"تمت إضافة {xp_to_add} XP | "
        f"المستوى: {old_level} -> {new_level} | "
        f"الارتقاء: {level_up}"
    )
    
    return new_xp, level_up, new_level