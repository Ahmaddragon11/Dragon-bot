# handlers.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import ADMIN_ID
from models import User
from database import get_user, save_user, get_all_users
from utils import generate_referral_code, is_admin, create_main_menu, create_admin_menu

POINTS_PER_REFERRAL = 10  # نقاط لكل إحالة، يمكن تغييرها عبر الأدمن

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)
    if not db_user:
        referral_code = generate_referral_code()
        db_user = User(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            referral_code=referral_code
        )
        save_user(db_user)
        # التحقق من الإحالة
        if context.args and len(context.args) > 0:
            referrer_code = context.args[0]
            referrer = next((u for u in get_all_users() if u.referral_code == referrer_code), None)
            if referrer and referrer.user_id != user.id:
                referrer.points += POINTS_PER_REFERRAL
                db_user.referred_by = referrer.user_id
                save_user(referrer)
                save_user(db_user)
                await update.message.reply_text(f"تم منح {POINTS_PER_REFERRAL} نقاط للمحيل!")

    if db_user.is_banned:
        await update.message.reply_text("أنت محظور من البوت.")
        return

    text = f"مرحبا {user.first_name}!\nاختر من القائمة:"
    await update.message.reply_text(text, reply_markup=create_main_menu())

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    db_user = get_user(user_id)
    if not db_user or db_user.is_banned:
        await query.edit_message_text("أنت محظور من البوت.")
        return

    data = query.data

    if data == "points":
        await query.edit_message_text(f"نقاطك: {db_user.points}", reply_markup=create_main_menu())
    elif data == "referral":
        link = f"https://t.me/{context.bot.username}?start={db_user.referral_code}"
        await query.edit_message_text(f"رابط الإحالة الخاص بك:\n{link}", reply_markup=create_main_menu())
    elif data == "details":
        details = "هذا البوت يحتوي على نظام نقاط وإحالة. يمكنك كسب النقاط عبر الإحالات."
        await query.edit_message_text(details, reply_markup=create_main_menu())
    elif data == "feedback":
        await query.edit_message_text("أرسل ملاحظتك أو فكرتك الآن:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("إلغاء", callback_data="back_to_main")]]))
        context.user_data['awaiting_feedback'] = True
    elif data == "back_to_main":
        await query.edit_message_text("اختر من القائمة:", reply_markup=create_main_menu())
    elif data.startswith("admin_"):
        if not is_admin(user_id):
            await query.edit_message_text("غير مصرح لك.", reply_markup=create_main_menu())
            return
        if data == "admin_points":
            # قائمة المستخدمين مع النقاط
            users = get_all_users()
            text = "\n".join([f"{u.first_name} ({u.user_id}): {u.points} نقاط" for u in users])
            await query.edit_message_text(text, reply_markup=create_admin_menu())
        elif data == "admin_referrals":
            # إحصائيات الإحالات
            users = get_all_users()
            total_referrals = sum(1 for u in users if u.referred_by is not None)
            total_points_from_referrals = total_referrals * POINTS_PER_REFERRAL
            text = f"إجمالي الإحالات: {total_referrals}\nإجمالي النقاط من الإحالات: {total_points_from_referrals}"
            await query.edit_message_text(text, reply_markup=create_admin_menu())
        elif data == "admin_users":
            # قائمة المستخدمين
            users = get_all_users()
            text = "\n".join([f"{u.first_name} ({u.user_id}): {'محظور' if u.is_banned else 'نشط'}" for u in users])
            await query.edit_message_text(text, reply_markup=create_admin_menu())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if context.user_data.get('awaiting_feedback'):
        feedback = update.message.text
        # إرسال للأدمن
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"ملاحظة من {user_id}: {feedback}")
        await update.message.reply_text("تم إرسال ملاحظتك!")
        context.user_data['awaiting_feedback'] = False
        await update.message.reply_text("اختر من القائمة:", reply_markup=create_main_menu())
    else:
        await update.message.reply_text("استخدم /start لبدء.")

# أوامر الأدمن
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("غير مصرح لك.")
        return
    await update.message.reply_text("قائمة الأدمن:", reply_markup=create_admin_menu())

# إضافة أوامر أدمن إضافية
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("غير مصرح لك.")
        return
    if not context.args:
        await update.message.reply_text("استخدم: /ban <user_id>")
        return
    try:
        target_id = int(context.args[0])
        user = get_user(target_id)
        if user:
            user.is_banned = True
            save_user(user)
            await update.message.reply_text(f"تم حظر المستخدم {target_id}")
        else:
            await update.message.reply_text("المستخدم غير موجود.")
    except ValueError:
        await update.message.reply_text("معرف المستخدم غير صحيح.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("غير مصرح لك.")
        return
    if not context.args:
        await update.message.reply_text("استخدم: /unban <user_id>")
        return
    try:
        target_id = int(context.args[0])
        user = get_user(target_id)
        if user:
            user.is_banned = False
            save_user(user)
            await update.message.reply_text(f"تم إلغاء حظر المستخدم {target_id}")
        else:
            await update.message.reply_text("المستخدم غير موجود.")
    except ValueError:
        await update.message.reply_text("معرف المستخدم غير صحيح.")

async def add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("غير مصرح لك.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("استخدم: /add_points <user_id> <points>")
        return
    try:
        target_id = int(context.args[0])
        points = int(context.args[1])
        user = get_user(target_id)
        if user:
            user.points += points
            save_user(user)
            await update.message.reply_text(f"تم إضافة {points} نقاط للمستخدم {target_id}")
        else:
            await update.message.reply_text("المستخدم غير موجود.")
    except ValueError:
        await update.message.reply_text("المعرف أو النقاط غير صحيحة.")

async def set_referral_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("غير مصرح لك.")
        return
    if not context.args:
        await update.message.reply_text("استخدم: /set_referral_points <points>")
        return
    try:
        new_points = int(context.args[0])
        # تحديث في config، لكن بما أنه ثابت، ربما أضف متغير عالمي أو شيء
        # للبساطة، سنفترض أنه يغير المتغير، لكن في الواقع يحتاج إعادة تشغيل
        global POINTS_PER_REFERRAL
        POINTS_PER_REFERRAL = new_points
        await update.message.reply_text(f"تم تحديث نقاط الإحالة إلى {new_points}")
    except ValueError:
        await update.message.reply_text("النقاط غير صحيحة.")