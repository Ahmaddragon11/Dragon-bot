# src/bot/handlers/user_handlers.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from src.database import get_user, get_referral_count
from src.core.config import POINTS_PER_REFERRAL
from src.bot.ui import create_main_menu, create_about_menu, back_to_main_menu_button

# --- معالجات ردود الأزرار ---
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """المعالج الرئيسي لجميع ردود الأزرار."""
    query = update.callback_query
    await query.answer() # يجب استدعاء answer() دائمًا

    # التأكد من وجود مستخدم مسجل
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user:
        await query.edit_message_text("⚠️ عذرًا، حدث خطأ. يرجى الضغط على /start للبدء من جديد.")
        return
    
    # توجيه الردود بناءً على بيانات الزر
    data = query.data

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


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض القائمة الرئيسية."""
    query = update.callback_query
    user_first_name = query.from_user.first_name
    text = f"👋 أهلاً بك مجددًا {user_first_name}!\n\nاختر أحد الخيارات من القائمة أدناه:"
    await query.edit_message_text(text, reply_markup=create_main_menu())


async def show_user_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض نقاط المستخدم وعدد إحالاته."""
    query = update.callback_query
    user_id = query.from_user.id
    db_user = get_user(user_id)

    if not db_user:
        await query.edit_message_text("خطأ، لم يتم العثور على بياناتك. اضغط /start")
        return

    referral_count = get_referral_count(user_id)
    
    points_text = (
        f"💰 **إحصائياتك:**\n\n"
        f"🎯 نقاطك الحالية: **{db_user.points}** نقطة\n"
        f"👥 عدد من دعوتهم: **{referral_count}** شخص"
    )
    await query.edit_message_text(
        points_text,
        parse_mode="Markdown",
        reply_markup=back_to_main_menu_button()
    )


async def show_user_referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض رابط الإحالة الخاص بالمستخدم."""
    query = update.callback_query
    user_id = query.from_user.id
    db_user = get_user(user_id)

    if not db_user or not db_user.referral_code:
        await query.edit_message_text("خطأ، لم يتم العثور على رمز الإحالة. اضغط /start")
        return

    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={db_user.referral_code}"
    
    referral_text = (
        f"🔗 **رابط دعوتك:**\n"
        f"`{link}`\n\n"
        f"شارك هذا الرابط مع أصدقائك. ستحصل على **{POINTS_PER_REFERRAL}** نقطة عن كل شخص ينضم من خلاله."
    )
    await query.edit_message_text(
        referral_text, 
        parse_mode="Markdown", 
        reply_markup=back_to_main_menu_button(),
        disable_web_page_preview=True
    )


async def show_about_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة (حول البوت)."""
    query = update.callback_query
    about_text = (
        "ℹ️ **حول البوت**\n\n"
        "هذا البوت تم تطويره ليقدم ميزات... (هنا يمكنك كتابة وصف للبوت).\n\n"
        "**الميزات الرئيسية:**\n"
        "- نظام نقاط متقدم\n"
        "- نظام إحالة فعال\n"
        "- لوحة تحكم سهلة للمدير"
    )
    await query.edit_message_text(about_text, parse_mode="Markdown", reply_markup=create_about_menu())


async def request_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """طلب إرسال ملاحظة من المستخدم."""
    query = update.callback_query
    await query.edit_message_text(
        "💬 **إرسال ملاحظة للمطور**\n\n"
        "اكتب الآن رسالتك وسأقوم بإيصالها مباشرة للمطور. لإلغاء العملية، اضغط على الزر أدناه.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 إلغاء", callback_data="user_about")]])
    )
    context.user_data['awaiting_feedback'] = True
