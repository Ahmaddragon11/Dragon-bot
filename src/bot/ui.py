# src/bot/ui.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# --- القائمة الرئيسية ---
def create_main_menu() -> InlineKeyboardMarkup:
    """إنشاء وإرجاع أزرار القائمة الرئيسية."""
    keyboard = [
        [InlineKeyboardButton("💰 نقاطي", callback_data="user_points")],
        [InlineKeyboardButton("🔗 رابط الإحالة", callback_data="user_referral")],
        [InlineKeyboardButton("ℹ️ حول البوت", callback_data="user_about")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- قائمة (حول البوت) ---
def create_about_menu() -> InlineKeyboardMarkup:
    """إنشاء وإرجاع قائمة (حول البوت)."""
    keyboard = [
        [InlineKeyboardButton("📱 تواصل مع المطور", url="https://t.me/ahmaddragon")],
        [InlineKeyboardButton("💬 إرسال ملاحظة", callback_data="user_feedback")],
        [InlineKeyboardButton("🔙 العودة", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- زر العودة للقائمة الرئيسية ---
def back_to_main_menu_button() -> InlineKeyboardMarkup:
    """إنشاء زر واحد للعودة إلى القائمة الرئيسية."""
    keyboard = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

# --- لوحة تحكم المدير ---
def create_admin_menu() -> InlineKeyboardMarkup:
    """إنشاء وإرجاع قائمة لوحة تحكم المدير."""
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

# --- قائمة إدارة المستخدم (للمدير) ---
def create_manage_user_menu() -> InlineKeyboardMarkup:
    """قائمة أزرار للبحث عن مستخدم."""
    keyboard = [
        [InlineKeyboardButton("🔍 بحث بالمعرف", callback_data="admin_find_user_by_id")],
        [InlineKeyboardButton("🔎 بحث باسم المستخدم", callback_data="admin_find_user_by_username")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- أزرار التحكم في المستخدم (للمدير) ---
def create_user_control_panel(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    """إنشاء أزرار التحكم في مستخدم معين."""
    ban_button_text = "✅ رفع الحظر" if is_banned else "🚫 حظر"
    ban_button_callback = f"admin_unban_{user_id}" if is_banned else f"admin_ban_{user_id}"
    keyboard = [
        [
            InlineKeyboardButton(ban_button_text, callback_data=ban_button_callback),
            InlineKeyboardButton("➕ إضافة نقاط", callback_data=f"admin_add_points_{user_id}")
        ],
        [InlineKeyboardButton("🔙 رجوع لقائمة الإدارة", callback_data="admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)
