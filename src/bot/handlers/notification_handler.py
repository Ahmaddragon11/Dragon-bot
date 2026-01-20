"""
معالج الإشعارات للمشرفين.

يوفر واجهة لعرض وإدارة إشعارات النظام.
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import logging

from src.utils import (
    notification_manager,
    is_admin,
    get_admin_ids,
)
from src.utils.notification_manager import NotificationType, NotificationLevel
from src.bot.ui import create_confirmation_menu, create_admin_menu

logger: logging.Logger = logging.getLogger(__name__)


async def show_notifications_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة الإشعارات.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): سياق المعالج
    """
    if not is_admin(update.effective_user.id, get_admin_ids()):
        await update.callback_query.answer("❌ ليس لديك صلاحيات")
        return
    
    admin_id = update.effective_user.id
    notifications = notification_manager.get_notifications_for_admin(admin_id, unread_only=True)
    
    if not notifications:
        text = "✅ لا توجد إشعارات جديدة"
    else:
        text = f"📬 لديك {len(notifications)} إشعار(ات) جديد(ة):\n\n"
        
        for notification in notifications[:5]:  # عرض أول 5 إشعارات فقط
            text += f"{notification.get_emoji()} {notification.title}\n"
            text += f"   {notification.message[:50]}...\n\n"
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 تحديث", callback_data="notifications_refresh"),
            InlineKeyboardButton("✅ وضع علامة مقروء", callback_data="notifications_mark_read"),
        ],
        [
            InlineKeyboardButton("⚙️ الإعدادات", callback_data="notifications_settings"),
            InlineKeyboardButton("🔙 رجوع", callback_data="admin_back"),
        ],
    ]
    
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard_markup,
        parse_mode="HTML"
    )


async def notifications_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج استدعاءات الإشعارات.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): سياق المعالج
    """
    if not is_admin(update.effective_user.id, get_admin_ids()):
        await update.callback_query.answer("❌ ليس لديك صلاحيات")
        return
    
    query = update.callback_query
    admin_id = update.effective_user.id
    
    if query.data == "notifications_refresh":
        await show_notifications_menu(update, context)
    
    elif query.data == "notifications_mark_read":
        count = notification_manager.mark_all_as_read(admin_id)
        await query.answer(f"✅ تم تحديد {count} إشعار كمقروء")
        await show_notifications_menu(update, context)
    
    elif query.data == "notifications_settings":
        await show_notification_preferences(update, context)


async def show_notification_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض تفضيلات الإشعارات.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): سياق المعالج
    """
    admin_id = update.effective_user.id
    current_prefs = notification_manager.get_admin_preferences(admin_id)
    
    text = "⚙️ **تفضيلات الإشعارات**\n\n"
    text += "حدد أنواع الإشعارات التي تريد استقبالها:\n\n"
    
    # زر لكل نوع إشعار
    keyboard = []
    
    for notif_type in NotificationType:
        is_selected = notif_type in current_prefs
        emoji = "✅" if is_selected else "☐"
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {notif_type.value}",
                callback_data=f"toggle_notif_{notif_type.name}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton("🔙 رجوع", callback_data="show_notifications_menu")
    ])
    
    keyboard_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard_markup,
        parse_mode="HTML"
    )


async def toggle_notification_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    تبديل نوع الإشعار.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): سياق المعالج
    """
    query = update.callback_query
    admin_id = update.effective_user.id
    
    # استخراج نوع الإشعار من callback_data
    notif_type_name = query.data.replace("toggle_notif_", "")
    notif_type = NotificationType[notif_type_name]
    
    # الحصول على التفضيلات الحالية
    current_prefs = set(notification_manager.get_admin_preferences(admin_id))
    
    # تبديل الاختيار
    if notif_type in current_prefs:
        current_prefs.discard(notif_type)
    else:
        current_prefs.add(notif_type)
    
    # حفظ التفضيلات الجديدة
    notification_manager.set_admin_preferences(admin_id, list(current_prefs))
    
    await query.answer("✅ تم حفظ التفضيلات")
    await show_notification_preferences(update, context)


async def send_notification_to_admins(
    notification_type: NotificationType,
    level: NotificationLevel,
    title: str,
    message: str,
    related_user_id: int = None,
    data: dict = None,
    context: ContextTypes.DEFAULT_TYPE = None
) -> None:
    """
    إرسال إشعار لجميع المشرفين.
    
    Args:
        notification_type (NotificationType): نوع الإشعار
        level (NotificationLevel): مستوى الأهمية
        title (str): العنوان
        message (str): المحتوى
        related_user_id (int): معرّف المستخدم ذي الصلة
        data (dict): بيانات إضافية
        context (ContextTypes.DEFAULT_TYPE): سياق المعالج
    """
    # إنشاء الإشعار
    notification = notification_manager.create_notification(
        notification_type=notification_type,
        level=level,
        title=title,
        message=message,
        related_user_id=related_user_id,
        data=data or {}
    )
    
    # إرسال الإشعار للمشرفين
    if context:
        admin_ids = get_admin_ids()
        
        for admin_id in admin_ids:
            try:
                prefs = notification_manager.get_admin_preferences(admin_id)
                
                # التحقق من تفضيلات المشرف
                if notification_type in prefs or not prefs:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=notification.get_formatted(),
                        parse_mode="HTML"
                    )
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار للمشرف {admin_id}: {str(e)}")
    
    logger.info(f"تم إنشاء إشعار: {title}")
