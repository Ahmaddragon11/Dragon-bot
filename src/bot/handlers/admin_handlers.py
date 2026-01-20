"""
معالجات لوحة التحكم والإدارة.

يحتوي هذا الملف على جميع معالجات الأوامر والأزرار
الخاصة بالمسؤولين فقط.
"""

import logging
from typing import Optional
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from src.database import (
    get_total_users_count, get_banned_users_count, get_top_users_by_points,
    get_top_users_by_referrals, get_user, find_user_by_username, save_user,
    get_all_users, get_referral_count, get_top_users_by_level
)
from src.utils.helpers import is_admin
from src.bot.ui import (
    create_admin_menu, create_manage_user_menu,
    create_user_control_panel, back_to_main_menu_button
)
from src.models.user import User
from src.utils.exceptions import DatabaseError

logger: logging.Logger = logging.getLogger(__name__)

# حالات ConversationHandler
ASK_FOR_USER_ID, ASK_FOR_USERNAME, ASK_FOR_BROADCAST_MESSAGE, ASK_FOR_POINTS = range(4)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج أمر /admin الرئيسي.

    يعرض لوحة التحكم للمسؤولين فقط.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    user_id: int = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text("⚠️ هذه المنطقة مخصصة للمدير فقط!")
        logger.warning(f"محاولة وصول غير مصرح بها من {user_id}")
        return

    text: str = "👑 أهلاً بك في لوحة تحكم المدير."
    await update.message.reply_text(text, reply_markup=create_admin_menu())
    logger.info(f"افتتح المسؤول {user_id} لوحة التحكم")


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[int]:
    """
    المعالج الرئيسي لجميع ردود أزرار المدير.

    يوجه الاستعلامات حسب نوع الزر المضغوط.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        Optional[int]: حالة ConversationHandler أو None
    """
    query = update.callback_query
    await query.answer()
    user_id: int = query.from_user.id

    if not is_admin(user_id):
        await query.answer("ليس لديك صلاحية لهذا الإجراء!", show_alert=True)
        logger.warning(f"محاولة وصول غير مصرح لـ {user_id}")
        return None

    data: str = query.data
    logger.debug(f"استعلام من مسؤول {user_id}: {data}")

    try:
        if data == "admin_panel":
            await query.edit_message_text("👑 لوحة تحكم المدير", reply_markup=create_admin_menu())
        elif data == "admin_stats":
            await show_stats(update, context)
        elif data == "admin_top_points":
            await show_top_users_by_points(update, context)
        elif data == "admin_top_referrals":
            await show_top_users_by_referrals(update, context)
        elif data == "admin_manage_user":
            await show_manage_user_menu(update, context)
        elif data == "admin_find_user_by_id":
            await query.edit_message_text("⌨️ أدخل المعرف الرقمي (ID) للمستخدم:")
            return ASK_FOR_USER_ID
        elif data == "admin_find_user_by_username":
            await query.edit_message_text("⌨️ أدخل اسم المستخدم (بدون @):")
            return ASK_FOR_USERNAME
        elif data == "admin_broadcast":
            await query.edit_message_text(
                "📝 أدخل الآن رسالة الإذاعة. يمكنك استخدام تنسيق Markdown.\n"
                "لإلغاء الإذاعة، أرسل /cancel."
            )
            return ASK_FOR_BROADCAST_MESSAGE
        elif "_ban_" in data or "_unban_" in data:
            await handle_ban_unban(update, context)
        elif "_add_points_" in data:
            user_id_to_add: int = int(data.split('_')[-1])
            context.user_data['user_id_to_modify'] = user_id_to_add
            await query.edit_message_text(
                f"➕ أدخل عدد النقاط التي تريد إضافتها للمستخدم `{user_id_to_add}`:"
            )
            return ASK_FOR_POINTS
        else:
            logger.warning(f"استعلام غير معروف: {data}")

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في قاعدة البيانات: {e.message}")
    except Exception as e:
        await query.edit_message_text("❌ حدث خطأ غير متوقع.")
        logger.error(f"خطأ في معالج الأزرار الإداري: {str(e)}", exc_info=True)

    return None


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض إحصائيات البوت العامة.

    يعرض عدد المستخدمين الكلي والمحظورين والنشطين.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    query = update.callback_query

    try:
        total_users: int = get_total_users_count()
        banned_users: int = get_banned_users_count()

        stats_text: str = (
            f"📊 **إحصائيات البوت:**\n\n"
            f"👥 إجمالي المستخدمين: **{total_users}**\n"
            f"🚫 المستخدمون المحظورون: **{banned_users}**\n"
            f"✅ المستخدمون النشطون: **{total_users - banned_users}**"
        )
        await query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_admin_menu()
        )
        logger.debug(f"عرض الإحصائيات للمسؤول {query.from_user.id}")

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في استرجاع الإحصائيات: {e.message}")


async def show_top_users_by_points(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة أكثر 10 مستخدمين نقاطاً.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    query = update.callback_query

    try:
        top_users = get_top_users_by_points(10)

        if not top_users:
            await query.edit_message_text(
                "🏆 لا يوجد مستخدمون لعرضهم.",
                reply_markup=create_admin_menu()
            )
            return

        text: str = "🏆 **أكثر 10 مستخدمين نقاطًا:**\n\n"
        for i, user in enumerate(top_users, 1):
            text += f"{i}. {user.first_name} (`{user.user_id}`) - **{user.points}** نقطة\n"

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_admin_menu()
        )

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في استرجاع الترتيب: {e.message}")


async def show_top_users_by_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة أكثر 10 مستخدمين إحالة.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    query = update.callback_query

    try:
        top_users = get_top_users_by_referrals(10)

        if not top_users:
            await query.edit_message_text(
                "📈 لا يوجد مستخدمون لعرضهم.",
                reply_markup=create_admin_menu()
            )
            return

        text: str = "📈 **أكثر 10 مستخدمين إحالة:**\n\n"
        for i, user_data in enumerate(top_users, 1):
            text += f"{i}. {user_data['first_name']} - **{user_data['referral_count']}** إحالة\n"

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_admin_menu()
        )

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في استرجاع الإحالات: {e.message}")


async def show_manage_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    عرض قائمة إدارة المستخدمين.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    query = update.callback_query
    await query.edit_message_text(
        "👤 **إدارة المستخدمين**\n\nاختر طريقة البحث عن المستخدم:",
        reply_markup=create_manage_user_menu()
    )


async def find_user_by_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    معالج استلام معرّف المستخدم للبحث.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        int: حالة ConversationHandler
    """
    try:
        user_id: int = int(update.message.text)
    except ValueError:
        await update.message.reply_text("⚠️ المعرف يجب أن يكون رقمًا. حاول مرة أخرى.")
        return ASK_FOR_USER_ID

    try:
        db_user: Optional[User] = get_user(user_id)
        await display_user_info_for_admin(update, context, db_user)
        logger.debug(f"بحث عن مستخدم برقمه: {user_id}")

    except DatabaseError as e:
        await update.message.reply_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في البحث: {e.message}")

    return ConversationHandler.END


async def find_user_by_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    معالج استلام اسم المستخدم للبحث.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        int: حالة ConversationHandler
    """
    username: str = update.message.text.lstrip('@')

    try:
        db_user: Optional[User] = find_user_by_username(username)
        await display_user_info_for_admin(update, context, db_user)
        logger.debug(f"بحث عن مستخدم باسم المستخدم: {username}")

    except DatabaseError as e:
        await update.message.reply_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في البحث: {e.message}")

    return ConversationHandler.END


async def display_user_info_for_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    db_user: Optional[User]
) -> None:
    """
    عرض معلومات المستخدم وأزرار التحكم للمدير.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        db_user (Optional[User]): بيانات المستخدم

    Returns:
        None
    """
    if not db_user:
        await update.message.reply_text(
            "❌ لم يتم العثور على المستخدم.",
            reply_markup=create_admin_menu()
        )
        logger.warning(f"محاولة البحث عن مستخدم غير موجود")
        return

    referral_count: int = get_referral_count(db_user.user_id)

    join_date_str: str = (
        db_user.join_date.strftime('%Y-%m-%d')
        if db_user.join_date else 'غير معروف'
    )

    user_info: str = (
        f"**معلومات المستخدم:**\n\n"
        f"- **الاسم:** {db_user.first_name}\n"
        f"- **المعرف:** `{db_user.user_id}`\n"
        f"- **اسم المستخدم:** @{db_user.username or 'لا يوجد'}\n"
        f"- **النقاط:** {db_user.points}\n"
        f"- **المستوى:** {db_user.level}\n"
        f"- **الخبرة:** {db_user.experience} XP\n"
        f"- **الإحالات:** {referral_count}\n"
        f"- **تاريخ الانضمام:** {join_date_str}\n"
        f"- **محظور:** {'نعم 🚫' if db_user.is_banned else 'لا ✅'}"
    )

    await update.message.reply_text(
        user_info,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_user_control_panel(db_user.user_id, db_user.is_banned)
    )


async def handle_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج حظر وإلغاء حظر المستخدم.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    query = update.callback_query
    data_parts: list = query.data.split('_')
    action: str = data_parts[1]
    user_id: int = int(data_parts[2])

    try:
        db_user: Optional[User] = get_user(user_id)

        if not db_user:
            await query.answer("المستخدم غير موجود!", show_alert=True)
            return

        if action == 'ban':
            db_user.is_banned = True
            message: str = f"🚫 تم حظر المستخدم {db_user.first_name} بنجاح."
            logger.info(f"المسؤول {query.from_user.id} حظر المستخدم {user_id}")
        else:  # unban
            db_user.is_banned = False
            message = f"✅ تم رفع الحظر عن المستخدم {db_user.first_name} بنجاح."
            logger.info(f"المسؤول {query.from_user.id} رفع الحظر عن المستخدم {user_id}")

        save_user(db_user)
        await query.edit_message_text(message, reply_markup=create_admin_menu())

    except DatabaseError as e:
        await query.edit_message_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في حظر/إلغاء الحظر: {e.message}")


async def add_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    معالج إضافة نقاط للمستخدم.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        int: حالة ConversationHandler
    """
    try:
        points_to_add: int = int(update.message.text)
        user_id: int = context.user_data.get('user_id_to_modify')

        if not user_id:
            await update.message.reply_text(
                "❌ حدث خطأ، يرجى المحاولة مرة أخرى.",
                reply_markup=create_admin_menu()
            )
            return ConversationHandler.END

        db_user: Optional[User] = get_user(user_id)

        if db_user:
            old_points: int = db_user.points
            db_user.points += points_to_add
            save_user(db_user)

            message: str = (
                f"✅ تم إضافة {points_to_add} نقطة إلى {db_user.first_name}.\n"
                f"النقاط السابقة: {old_points}\n"
                f"النقاط الحالية: {db_user.points}"
            )
            await update.message.reply_text(message, reply_markup=create_admin_menu())
            logger.info(
                f"المسؤول {update.effective_user.id} أضاف {points_to_add} نقطة "
                f"للمستخدم {user_id}"
            )
        else:
            await update.message.reply_text(
                "❌ لم يتم العثور على المستخدم.",
                reply_markup=create_admin_menu()
            )

    except ValueError:
        await update.message.reply_text(
            "⚠️ يجب إدخال عدد صحيح. حاول مرة أخرى."
        )
        return ASK_FOR_POINTS
    except DatabaseError as e:
        await update.message.reply_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في إضافة النقاط: {e.message}")

    finally:
        if 'user_id_to_modify' in context.user_data:
            del context.user_data['user_id_to_modify']

    return ConversationHandler.END


async def broadcast_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    معالج استلام رسالة الإذاعة وإرسالها لجميع المستخدمين.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        int: حالة ConversationHandler
    """
    message_text: str = update.message.text

    try:
        all_users = get_all_users()
        sent_count: int = 0
        failed_count: int = 0

        await update.message.reply_text(
            f"⏳ جاري بدء الإذاعة إلى {len(all_users)} مستخدم... "
            "يرجى الانتظار."
        )

        for user in all_users:
            if user.is_banned:
                continue

            try:
                await context.bot.send_message(
                    user.user_id,
                    message_text,
                    parse_mode=ParseMode.MARKDOWN
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"فشل إرسال الرسالة للمستخدم {user.user_id}: {e}")
                failed_count += 1

        feedback: str = (
            f"📣 اكتملت الإذاعة!\n\n"
            f"- ✅ تم الإرسال بنجاح إلى: **{sent_count}** مستخدم\n"
            f"- ❌ فشل الإرسال لـ: **{failed_count}** مستخدم"
        )

        await update.message.reply_text(
            feedback,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=create_admin_menu()
        )

        logger.info(
            f"المسؤول {update.effective_user.id} أرسل إذاعة: "
            f"نجح {sent_count}، فشل {failed_count}"
        )

    except DatabaseError as e:
        await update.message.reply_text(f"❌ خطأ: {e.message}")
        logger.error(f"خطأ في الإذاعة: {e.message}")

    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    إلغاء المحادثة الحالية.

    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        int: حالة ConversationHandler
    """
    await update.message.reply_text(
        "❌ تم إلغاء العملية.",
        reply_markup=create_admin_menu()
    )
    logger.debug(f"المستخدم {update.effective_user.id} ألغى العملية")
    return ConversationHandler.END

async def show_top_users_by_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة أكثر المستخدمين نقاطاً."""
    query = update.callback_query
    top_users = get_top_users_by_points(10)
    if not top_users:
        await query.edit_message_text("🏆 لا يوجد مستخدمون لعرضهم.", reply_markup=create_admin_menu())
        return

    text = "🏆 **أكثر 10 مستخدمين نقاطًا:**\n\n"
    for i, user in enumerate(top_users, 1):
        text += f"{i}. {user.first_name} (`{user.user_id}`) - **{user.points}** نقطة\n"
    
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_admin_menu())

async def show_top_users_by_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة أكثر المستخدمين إحالة."""
    query = update.callback_query
    top_users = get_top_users_by_referrals(10)
    if not top_users:
        await query.edit_message_text("📈 لا يوجد مستخدمون لعرضهم.", reply_markup=create_admin_menu())
        return

    text = "📈 **أكثر 10 مستخدمين دعوة للأصدقاء:**\n\n"
    for i, user_data in enumerate(top_users, 1):
        text += f"{i}. {user_data['first_name']} - **{user_data['referral_count']}** دعوة\n"

    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=create_admin_menu())

async def show_manage_user_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة إدارة المستخدمين."""
    query = update.callback_query
    await query.edit_message_text("👤 **إدارة المستخدمين**\n\nاختر طريقة البحث عن المستخدم:", reply_markup=create_manage_user_menu())

async def find_user_by_id_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج استلام معرف المستخدم للبحث."""
    try:
        user_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("⚠️ المعرف يجب أن يكون رقمًا. حاول مرة أخرى.")
        return ASK_FOR_USER_ID

    db_user = get_user(user_id)
    await display_user_info_for_admin(update, context, db_user)
    return ConversationHandler.END

async def find_user_by_username_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج استلام اسم المستخدم للبحث."""
    username = update.message.text.lstrip('@')
    db_user = find_user_by_username(username)
    await display_user_info_for_admin(update, context, db_user)
    return ConversationHandler.END

async def display_user_info_for_admin(update, context, db_user):
    """عرض معلومات المستخدم وأزرار التحكم للمدير."""
    if not db_user:
        await update.message.reply_text("❌ لم يتم العثور على المستخدم.", reply_markup=create_admin_menu())
        return

    user_info = (
        f"**معلومات المستخدم:**\n"
        f"- **الاسم:** {db_user.first_name}\n"
        f"- **المعرف:** `{db_user.user_id}`\n"
        f"- **اسم المستخدم:** @{db_user.username}\n"
        f"- **النقاط:** {db_user.points}\n"
        f"- **تاريخ الانضمام:** {db_user.join_date.strftime('%Y-%m-%d') if db_user.join_date else 'غير معروف'}\n"
        f"- **محظور:** {'نعم' if db_user.is_banned else 'لا'}"
    )
    await update.message.reply_text(
        user_info, 
        parse_mode=ParseMode.MARKDOWN, 
        reply_markup=create_user_control_panel(db_user.user_id, db_user.is_banned)
    )

async def handle_ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج حظر وإلغاء حظر المستخدم."""
    query = update.callback_query
    data_parts = query.data.split('_')
    action = data_parts[1]
    user_id = int(data_parts[2])

    db_user = get_user(user_id)
    if not db_user:
        await query.answer("المستخدم غير موجود!", show_alert=True)
        return

    if action == 'ban':
        db_user.is_banned = True
        message = f"🚫 تم حظر المستخدم {db_user.first_name} بنجاح."
    else: # unban
        db_user.is_banned = False
        message = f"✅ تم رفع الحظر عن المستخدم {db_user.first_name} بنجاح."
    
    save_user(db_user)
    await query.edit_message_text(message, reply_markup=create_admin_menu())

async def add_points_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج إضافة نقاط للمستخدم."""
    try:
        points_to_add = int(update.message.text)
        user_id = context.user_data.get('user_id_to_modify')
    except (ValueError, KeyError):
        await update.message.reply_text("حدث خطأ، يرجى المحاولة مرة أخرى.", reply_markup=create_admin_menu())
        return ConversationHandler.END

    db_user = get_user(user_id)
    if db_user:
        db_user.points += points_to_add
        save_user(db_user)
        await update.message.reply_text(f"✅ تم إضافة {points_to_add} نقطة إلى {db_user.first_name}. رصيده الآن {db_user.points} نقطة.", reply_markup=create_admin_menu())
    else:
        await update.message.reply_text("❌ لم يتم العثور على المستخدم.", reply_markup=create_admin_menu())

    if 'user_id_to_modify' in context.user_data:
        del context.user_data['user_id_to_modify']
    return ConversationHandler.END

async def broadcast_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج استلام رسالة الإذاعة وإرسالها لجميع المستخدمين."""
    message_text = update.message.text
    all_users = get_all_users()
    sent_count = 0
    failed_count = 0
    
    await update.message.reply_text(f"⏳ جاري بدء الإذاعة إلى {len(all_users)} مستخدم... يرجى الانتظار.")

    for user in all_users:
        if user.is_banned: continue
        try:
            await context.bot.send_message(user.user_id, message_text, parse_mode=ParseMode.HTML)
            sent_count += 1
        except Exception:
            failed_count += 1
    
    feedback = f"📣 اكتملت الإذاعة!\n\n- ✅ تم الإرسال بنجاح إلى: {sent_count} مستخدم.\n- ❌ فشل الإرسال لـ: {failed_count} مستخدم."
    await update.message.reply_text(feedback, reply_markup=create_admin_menu())
    return ConversationHandler.END

async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إلغاء المحادثة الحالية."""
    await update.message.reply_text("تم إلغاء العملية.", reply_markup=create_admin_menu())
    return ConversationHandler.END
