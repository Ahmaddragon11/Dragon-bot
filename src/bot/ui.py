"""
وحدة واجهة المستخدم (UI) للبوت Dragon-bot.

تحتوي هذه الوحدة على جميع القوائم وأزرار InlineKeyboard
المستخدمة في واجهة البوت.
"""

from typing import Optional
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def create_main_menu() -> InlineKeyboardMarkup:
    """
    إنشاء القائمة الرئيسية للمستخدم العادي.
    
    Returns:
        InlineKeyboardMarkup: لوحة الأزرار الرئيسية
        
    Example:
        >>> menu = create_main_menu()
        >>> len(menu.inline_keyboard)
        4
    """
    keyboard = [
        [InlineKeyboardButton("💰 نقاطي", callback_data="user_points")],
        [InlineKeyboardButton("🔗 رابط الإحالة", callback_data="user_referral")],
        [InlineKeyboardButton("🏪 المتجر", callback_data="store_menu")],
        [InlineKeyboardButton("ℹ️ حول البوت", callback_data="user_about")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_about_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة معلومات البوت.
    
    Returns:
        InlineKeyboardMarkup: أزرار قائمة المعلومات
        
    Example:
        >>> menu = create_about_menu()
        >>> len(menu.inline_keyboard)
        3
    """
    keyboard = [
        [InlineKeyboardButton("📱 تواصل مع المطور", url="https://t.me/ahmaddragon")],
        [InlineKeyboardButton("💬 إرسال ملاحظة", callback_data="user_feedback")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_menu_button() -> InlineKeyboardMarkup:
    """
    إنشاء زر واحد فقط للعودة إلى القائمة الرئيسية.
    
    Returns:
        InlineKeyboardMarkup: زر العودة
        
    Example:
        >>> menu = back_to_main_menu_button()
        >>> len(menu.inline_keyboard)
        1
    """
    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)


def create_admin_menu() -> InlineKeyboardMarkup:
    """
    إنشاء لوحة تحكم المدير.
    
    يتضمن خيارات الإحصائيات والإذاعة وإدارة المستخدمين والترتيبات.
    
    Returns:
        InlineKeyboardMarkup: أزرار لوحة التحكم
        
    Example:
        >>> menu = create_admin_menu()
        >>> len(menu.inline_keyboard) > 0
        True
    """
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📣 إذاعة", callback_data="admin_broadcast")],
        [
            InlineKeyboardButton("🏆 أفضل النقاط", callback_data="admin_top_points"),
            InlineKeyboardButton("📈 أفضل الإحالات", callback_data="admin_top_referrals")
        ],
        [
            InlineKeyboardButton("📬 الإشعارات", callback_data="show_notifications_menu"),
            InlineKeyboardButton("👤 إدارة مستخدم", callback_data="admin_manage_user")
        ],
        [InlineKeyboardButton("🎁 إدارة المكافآت", callback_data="admin_manage_rewards")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_manage_user_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة البحث عن مستخدم.
    
    تتيح للمدير البحث بالمعرف أو اسم المستخدم.
    
    Returns:
        InlineKeyboardMarkup: أزرار البحث
        
    Example:
        >>> menu = create_manage_user_menu()
        >>> len(menu.inline_keyboard)
        3
    """
    keyboard = [
        [InlineKeyboardButton("🔍 بحث بالمعرف", callback_data="admin_find_user_by_id")],
        [InlineKeyboardButton("🔎 بحث باسم المستخدم", callback_data="admin_find_user_by_username")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_user_control_panel(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    """
    إنشاء لوحة التحكم في مستخدم معين.
    
    يتيح للمدير حظر/فك الحظر عن المستخدم وإضافة نقاط.
    
    Args:
        user_id (int): معرّف المستخدم المراد إدارته
        is_banned (bool): هل المستخدم محظور حاليًا؟
        
    Returns:
        InlineKeyboardMarkup: أزرار التحكم
        
    Example:
        >>> menu = create_user_control_panel(123, False)
        >>> len(menu.inline_keyboard)
        2
    """
    ban_button_text: str = "✅ رفع الحظر" if is_banned else "🚫 حظر"
    ban_button_callback: str = f"admin_unban_{user_id}" if is_banned else f"admin_ban_{user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton(ban_button_text, callback_data=ban_button_callback),
            InlineKeyboardButton("➕ إضافة نقاط", callback_data=f"admin_add_points_{user_id}")
        ],
        [InlineKeyboardButton("🔙 رجوع لقائمة الإدارة", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_leaderboard_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة الترتيبات.
    
    يتيح للمستخدم اختيار نوع الترتيب (نقاط، مستوى، إحالات).
    
    Returns:
        InlineKeyboardMarkup: أزرار الترتيبات
        
    Example:
        >>> menu = create_leaderboard_menu()
        >>> len(menu.inline_keyboard) > 0
        True
    """
    keyboard = [
        [InlineKeyboardButton("🏆 أفضل النقاط", callback_data="leaderboard_points")],
        [InlineKeyboardButton("📈 أفضل الإحالات", callback_data="leaderboard_referrals")],
        [InlineKeyboardButton("⭐ أعلى المستويات", callback_data="leaderboard_levels")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_confirmation_menu(action: str) -> InlineKeyboardMarkup:
    """
    إنشاء قائمة تأكيد إجراء ما.
    
    Args:
        action (str): نوع الإجراء (مثل: "delete", "ban", "reset")
        
    Returns:
        InlineKeyboardMarkup: أزرار التأكيد والإلغاء
        
    Example:
        >>> menu = create_confirmation_menu("delete")
        >>> len(menu.inline_keyboard)
        1
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، متأكد", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_notifications_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة الإشعارات للمسؤولين.
    
    تتيح للمسؤول عرض وإدارة الإشعارات.
    
    Returns:
        InlineKeyboardMarkup: أزرار قائمة الإشعارات
        
    Example:
        >>> menu = create_notifications_menu()
        >>> len(menu.inline_keyboard)
        3
    """
    keyboard = [
        [InlineKeyboardButton("🔄 تحديث", callback_data="notifications_refresh")],
        [InlineKeyboardButton("✅ وضع علامة مقروء", callback_data="notifications_mark_read")],
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="notifications_settings")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_store_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة المتجر.
    
    يتيح للمستخدم اختيار ما يريد من المتجر.
    
    Returns:
        InlineKeyboardMarkup: أزرار المتجر
        
    Example:
        >>> menu = create_store_menu()
        >>> len(menu.inline_keyboard) > 0
        True
    """
    keyboard = [
        [InlineKeyboardButton("🎁 المكافآت", callback_data="store_rewards")],
        [InlineKeyboardButton("⚡ الميزات الخاصة", callback_data="store_features")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_reward_purchase_menu(reward_id: int) -> InlineKeyboardMarkup:
    """
    إنشاء قائمة التأكيد لشراء مكافأة.
    
    Args:
        reward_id (int): معرّف المكافأة
        
    Returns:
        InlineKeyboardMarkup: أزرار التأكيد
        
    Example:
        >>> menu = create_reward_purchase_menu(1)
        >>> len(menu.inline_keyboard)
        1
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ تأكيد الشراء", callback_data=f"confirm_reward_{reward_id}"),
            InlineKeyboardButton("❌ إلغاء", callback_data="store_rewards")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_about_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة معلومات البوت.
    
    Returns:
        InlineKeyboardMarkup: أزرار قائمة المعلومات
        
    Example:
        >>> menu = create_about_menu()
        >>> len(menu.inline_keyboard)
        3
    """
    keyboard = [
        [InlineKeyboardButton("📱 تواصل مع المطور", url="https://t.me/ahmaddragon")],
        [InlineKeyboardButton("💬 إرسال ملاحظة", callback_data="user_feedback")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_menu_button() -> InlineKeyboardMarkup:
    """
    إنشاء زر واحد فقط للعودة إلى القائمة الرئيسية.
    
    Returns:
        InlineKeyboardMarkup: زر العودة
        
    Example:
        >>> menu = back_to_main_menu_button()
        >>> len(menu.inline_keyboard)
        1
    """
    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)


def create_admin_menu() -> InlineKeyboardMarkup:
    """
    إنشاء لوحة تحكم المدير.
    
    يتضمن خيارات الإحصائيات والإذاعة وإدارة المستخدمين والترتيبات.
    
    Returns:
        InlineKeyboardMarkup: أزرار لوحة التحكم
        
    Example:
        >>> menu = create_admin_menu()
        >>> len(menu.inline_keyboard) > 0
        True
    """
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("📣 إذاعة", callback_data="admin_broadcast")],
        [
            InlineKeyboardButton("🏆 أفضل النقاط", callback_data="admin_top_points"),
            InlineKeyboardButton("📈 أفضل الإحالات", callback_data="admin_top_referrals")
        ],
        [InlineKeyboardButton("👤 إدارة مستخدم", callback_data="admin_manage_user")],
        [InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_manage_user_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة البحث عن مستخدم.
    
    تتيح للمدير البحث بالمعرف أو اسم المستخدم.
    
    Returns:
        InlineKeyboardMarkup: أزرار البحث
        
    Example:
        >>> menu = create_manage_user_menu()
        >>> len(menu.inline_keyboard)
        3
    """
    keyboard = [
        [InlineKeyboardButton("🔍 بحث بالمعرف", callback_data="admin_find_user_by_id")],
        [InlineKeyboardButton("🔎 بحث باسم المستخدم", callback_data="admin_find_user_by_username")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_user_control_panel(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    """
    إنشاء لوحة التحكم في مستخدم معين.
    
    يتيح للمدير حظر/فك الحظر عن المستخدم وإضافة نقاط.
    
    Args:
        user_id (int): معرّف المستخدم المراد إدارته
        is_banned (bool): هل المستخدم محظور حاليًا؟
        
    Returns:
        InlineKeyboardMarkup: أزرار التحكم
        
    Example:
        >>> menu = create_user_control_panel(123, False)
        >>> len(menu.inline_keyboard)
        2
    """
    ban_button_text: str = "✅ رفع الحظر" if is_banned else "🚫 حظر"
    ban_button_callback: str = f"admin_unban_{user_id}" if is_banned else f"admin_ban_{user_id}"
    
    keyboard = [
        [
            InlineKeyboardButton(ban_button_text, callback_data=ban_button_callback),
            InlineKeyboardButton("➕ إضافة نقاط", callback_data=f"admin_add_points_{user_id}")
        ],
        [InlineKeyboardButton("🔙 رجوع لقائمة الإدارة", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_leaderboard_menu() -> InlineKeyboardMarkup:
    """
    إنشاء قائمة الترتيبات.
    
    يتيح للمستخدم اختيار نوع الترتيب (نقاط، مستوى، إحالات).
    
    Returns:
        InlineKeyboardMarkup: أزرار الترتيبات
        
    Example:
        >>> menu = create_leaderboard_menu()
        >>> len(menu.inline_keyboard) > 0
        True
    """
    keyboard = [
        [InlineKeyboardButton("🏆 أفضل النقاط", callback_data="leaderboard_points")],
        [InlineKeyboardButton("📈 أفضل الإحالات", callback_data="leaderboard_referrals")],
        [InlineKeyboardButton("⭐ أعلى المستويات", callback_data="leaderboard_levels")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_confirmation_menu(action: str) -> InlineKeyboardMarkup:
    """
    إنشاء قائمة تأكيد إجراء ما.
    
    Args:
        action (str): نوع الإجراء (مثل: "delete", "ban", "reset")
        
    Returns:
        InlineKeyboardMarkup: أزرار التأكيد والإلغاء
        
    Example:
        >>> menu = create_confirmation_menu("delete")
        >>> len(menu.inline_keyboard)
        1
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ نعم، متأكد", callback_data=f"confirm_{action}"),
            InlineKeyboardButton("❌ إلغاء", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
