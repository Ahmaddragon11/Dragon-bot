"""
وحدة المساعدات العامة للبوت Dragon-bot.

تحتوي هذه الوحدة على وظائف مساعدة عامة تُستخدم في جميع أنحاء المشروع
مثل توليد الأكواد والتحقق من الصلاحيات والعمليات الشائعة.
"""

import string
import random
import logging
from typing import List
from src.core.config import ADMIN_IDS

logger: logging.Logger = logging.getLogger(__name__)


def generate_referral_code(length: int = 8) -> str:
    """
    إنشاء رمز إحالة فريد عشوائي.
    
    يستخدم الحروف الكبيرة والصغيرة والأرقام لإنشاء كود فريد.
    
    Args:
        length (int): طول الكود المراد إنشاؤه (افتراضي: 8)
        
    Returns:
        str: رمز إحالة عشوائي
        
    Example:
        >>> code = generate_referral_code()
        >>> len(code)
        8
        >>> code = generate_referral_code(10)
        >>> len(code)
        10
    """
    return ''.join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )


def is_admin(user_id: int) -> bool:
    """
    التحقق مما إذا كان المستخدم مسؤولاً.
    
    Args:
        user_id (int): معرّف المستخدم المراد التحقق منه
        
    Returns:
        bool: True إذا كان المستخدم مسؤولاً، False وإلا
        
    Example:
        >>> is_admin(12345)
        False
        >>> is_admin(ADMIN_IDS[0])
        True
    """
    return user_id in ADMIN_IDS


def get_admin_ids() -> List[int]:
    """
    الحصول على قائمة معرّفات جميع المسؤولين.
    
    Returns:
        List[int]: قائمة بمعرّفات المسؤولين
        
    Example:
        >>> admins = get_admin_ids()
        >>> len(admins) > 0
        True
    """
    return ADMIN_IDS.copy()


def format_number(number: int, thousands_separator: str = ",") -> str:
    """
    تنسيق الأرقام بإضافة فاصل للآلاف.
    
    Args:
        number (int): الرقم المراد تنسيقه
        thousands_separator (str): الفاصل المستخدم (افتراضي: ",")
        
    Returns:
        str: الرقم المنسق
        
    Example:
        >>> format_number(1000000)
        '1,000,000'
        >>> format_number(1000000, '.')
        '1.000.000'
    """
    return f"{number:,}".replace(",", thousands_separator)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    اختصار النص إذا تجاوز الحد الأقصى.
    
    Args:
        text (str): النص المراد اختصاره
        max_length (int): الحد الأقصى لطول النص (افتراضي: 100)
        suffix (str): اللاحقة المستخدمة (افتراضي: "...")
        
    Returns:
        str: النص المختصر
        
    Example:
        >>> truncate_text("Hello World", 5)
        'Hel...'
        >>> truncate_text("Hi", 5)
        'Hi'
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """
    تفادي أحرف Markdown الخاصة في النص.
    
    يستخدم للنصوص التي قد تحتوي على رموز Markdown
    لتجنب تنسيقها بشكل غير مقصود.
    
    Args:
        text (str): النص الذي يحتوي على أحرف Markdown
        
    Returns:
        str: النص مع تفادي الأحرف الخاصة
        
    Example:
        >>> escape_markdown("*bold* and _italic_")
        '\\*bold\\* and \\_italic\\_'
    """
    special_chars = ["*", "_", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    
    result = text
    for char in special_chars:
        result = result.replace(char, f"\\{char}")
    
    return result


def calculate_level_from_xp(experience: int, xp_per_level: int) -> int:
    """
    حساب المستوى بناءً على نقاط الخبرة.
    
    Args:
        experience (int): نقاط الخبرة الإجمالية
        xp_per_level (int): نقاط الخبرة المطلوبة لكل مستوى
        
    Returns:
        int: المستوى المحسوب (الحد الأدنى: 1)
        
    Example:
        >>> calculate_level_from_xp(50, 10)
        6
        >>> calculate_level_from_xp(5, 10)
        1
    """
    return max(1, (experience // xp_per_level) + 1)


def calculate_xp_to_next_level(current_xp: int, xp_per_level: int) -> int:
    """
    حساب نقاط الخبرة المتبقية للوصول إلى المستوى التالي.
    
    Args:
        current_xp (int): نقاط الخبرة الحالية
        xp_per_level (int): نقاط الخبرة المطلوبة لكل مستوى
        
    Returns:
        int: عدد نقاط الخبرة المتبقية
        
    Example:
        >>> calculate_xp_to_next_level(25, 100)
        75
        >>> calculate_xp_to_next_level(150, 100)
        50
    """
    current_level = calculate_level_from_xp(current_xp, xp_per_level)
    xp_needed_for_level = (current_level - 1) * xp_per_level
    xp_in_level = current_xp - xp_needed_for_level
    
    return max(0, xp_per_level - xp_in_level)
