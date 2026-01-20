"""
معالجات أزرار القائمة للمستخدمين العاديين.

يحتوي هذا الملف على معالجات جميع الأزرار والاستعلامات
المتعلقة بحسابات المستخدمين العاديين.
"""

import logging
from typing import Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.database import get_user, get_referral_count
from src.core.config import POINTS_PER_REFERRAL
from src.bot.ui import create_main_menu, create_about_menu, back_to_main_menu_button
from src.models.user import User
from src.utils.exceptions import UserNotFound, DatabaseError

logger: logging.Logger = logging.getLogger(__name__)


async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    المعالج الرئيسي لجميع ردود الأزرار من المستخدمين العاديين.
    
    يتعامل مع توجيه الاستعلامات إلى المعالجات الفرعية المناسبة.
    
    Args:
        update (Update): تحديث Telegram يحتوي على استعلام الزر
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    await query.answer()  # يجب استدعاء answer() دائمًا لإغلاق قائمة التحميل

    # التأكد من وجود مستخدم مسجل
    user_id: int = query.from_user.id
    db_user: Optional[User] = get_user(user_id)

    if not db_user:
        await query.edit_message_text(
            "⚠️ عذرًا، حدث خطأ. يرجى الضغط على /start للبدء من جديد."
        )
        logger.warning(f"محاولة استخدام زر من مستخدم غير مسجل: {user_id}")
        return

    # توجيه الردود بناءً على بيانات الزر
    data: str = query.data

    try:
        if data == 'main_menu':
            await show_main_menu(update, context)
        elif data == 'user_points':
            await show_user_points(update, context)
        elif data == 'user_referral':
            await show_user_referral_link(update, context)
        elif data == 'user_about':
            await show_about_menu(update, context)
        elif data == 'user_feedback':
            await request_feedback(update, context)
        else:
            logger.warning(f"استعلام زر غير معروف: {data}")

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في قاعدة البيانات: {e.message}")
    except Exception as e:
        await query.edit_message_text("❌ حدث خطأ. يرجى المحاولة لاحقًا.")
        logger.error(f"خطأ غير متوقع في معالج الأزرار: {str(e)}", exc_info=True)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض القائمة الرئيسية للمستخدم.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    user_first_name: str = query.from_user.first_name or "صديقي"

    text: str = (
        f"👋 أهلاً بك مجددًا {user_first_name}!\n\n"
        "اختر أحد الخيارات من القائمة أدناه:"
    )
    await query.edit_message_text(text, reply_markup=create_main_menu())
    logger.debug(f"عرض القائمة الرئيسية للمستخدم {query.from_user.id}")


async def show_user_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض نقاط المستخدم والإحصائيات الخاصة به.
    
    يعرض النقاط الحالية والمستوى والخبرة وعدد الإحالات.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    user_id: int = query.from_user.id

    try:
        db_user: Optional[User] = get_user(user_id)

        if not db_user:
            await query.edit_message_text("❌ خطأ، لم يتم العثور على بياناتك. اضغط /start")
            return

        referral_count: int = get_referral_count(user_id)

        # بناء رسالة الإحصائيات
        points_text: str = (
            f"💰 **إحصائياتك:**\n\n"
            f"🎯 نقاطك الحالية: **{db_user.points}** نقطة\n"
            f"⭐ مستواك الحالي: **{db_user.level}**\n"
            f"✨ خبرتك: **{db_user.experience}** XP\n"
            f"🏅 رتبتك: **{db_user.rank}**\n"
            f"👥 عدد من دعوتهم: **{referral_count}** شخص"
        )

        await query.edit_message_text(
            points_text,
            parse_mode="Markdown",
            reply_markup=back_to_main_menu_button()
        )
        logger.debug(f"عرض النقاط للمستخدم {user_id}")

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ في البيانات: {e.message}")
        logger.error(f"خطأ في استرجاع نقاط المستخدم {user_id}: {e.message}")
    except Exception as e:
        await query.edit_message_text("❌ حدث خطأ غير متوقع.")
        logger.error(f"خطأ في show_user_points: {str(e)}", exc_info=True)


async def show_user_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض رابط الإحالة الخاص بالمستخدم.
    
    يعرض الرابط الفريد الذي يمكن للمستخدم مشاركته
    لإحالة أصدقائه والحصول على نقاط.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    user_id: int = query.from_user.id

    try:
        db_user: Optional[User] = get_user(user_id)

        if not db_user or not db_user.referral_code:
            await query.edit_message_text(
                "❌ خطأ، لم يتم العثور على رمز الإحالة. اضغط /start"
            )
            return

        # الحصول على اسم مستخدم البوت
        bot_me = await context.bot.get_me()
        bot_username: str = bot_me.username or "DragonBot"

        # بناء رابط الإحالة
        link: str = f"https://t.me/{bot_username}?start={db_user.referral_code}"

        referral_text: str = (
            f"🔗 **رابط دعوتك:**\n"
            f"`{link}`\n\n"
            f"شارك هذا الرابط مع أصدقائك. "
            f"ستحصل على **{POINTS_PER_REFERRAL}** نقطة عن كل شخص ينضم من خلاله."
        )

        await query.edit_message_text(
            referral_text,
            parse_mode="Markdown",
            reply_markup=back_to_main_menu_button(),
            disable_web_page_preview=True
        )
        logger.debug(f"عرض رابط الإحالة للمستخدم {user_id}")

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ في البيانات: {e.message}")
        logger.error(f"خطأ في استرجاع رمز الإحالة {user_id}: {e.message}")
    except Exception as e:
        await query.edit_message_text("❌ حدث خطأ غير متوقع.")
        logger.error(f"خطأ في show_user_referral_link: {str(e)}", exc_info=True)


async def show_about_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة معلومات البوت (حول البوت).
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    about_text: str = (
        "ℹ️ **حول البوت**\n\n"
        "هذا البوت تم تطويره لإدارة نظام النقاط والإحالات "
        "بكفاءة وسهولة.\n\n"
        "**الميزات الرئيسية:**\n"
        "✨ نظام نقاط متقدم\n"
        "🔗 نظام إحالة فعال\n"
        "⭐ نظام مستويات وخبرة\n"
        "🎮 واجهة سهلة الاستخدام\n"
        "👨‍💼 لوحة تحكم للمدير"
    )

    await query.edit_message_text(
        about_text,
        parse_mode="Markdown",
        reply_markup=create_about_menu()
    )
    logger.debug(f"عرض قائمة المعلومات للمستخدم {query.from_user.id}")


async def request_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    طلب إرسال ملاحظة أو تغذية راجعة من المستخدم.
    
    تحضير المستخدم لإرسال رسالة للمطور.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    query = update.callback_query
    await query.edit_message_text(
        "💬 **إرسال ملاحظة للمطور**\n\n"
        "اكتب الآن رسالتك وسأقوم بإيصالها مباشرة للمطور.\n"
        "لإلغاء العملية، اضغط على الزر أدناه.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔙 إلغاء", callback_data="user_about")]]
        )
    )
    context.user_data['awaiting_feedback'] = True
    logger.debug(f"بدء استقبال الملاحظات من المستخدم {query.from_user.id}")
