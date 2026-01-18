# handlers.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import ADMIN_ID
from models import User
from database import get_user, save_user, get_all_users
from utils import generate_referral_code, is_admin, create_main_menu, create_admin_menu, create_details_menu

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
                await update.message.reply_text(f"🎉 تم منح {POINTS_PER_REFERRAL} نقاط للمحيل!")

    if db_user.is_banned:
        await update.message.reply_text("❌ عذراً، أنت محظور من استخدام هذا البوت. للاستفسار تواصل مع @ahmaddragon")
        return

    text = f"👋 مرحباً بك {user.first_name}!\n\n🤖 أهلاً وسهلاً في بوت Dragon 🐉\n\nاختر من الخيارات أدناه للبدء:"
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
        referral_count = sum(1 for u in get_all_users() if u.referred_by == user_id)
        points_text = f"💰 **إحصائياتك:**\n\n"
        points_text += f"🎯 نقاطك الإجمالية: **{db_user.points}**\n"
        points_text += f"👥 عدد الإحالات: **{referral_count}**\n"
        points_text += f"🆔 معرفك: `{db_user.referral_code}`"
        await query.edit_message_text(points_text, parse_mode="Markdown", reply_markup=create_main_menu())
    elif data == "referral":
        link = f"https://t.me/{context.bot.username}?start={db_user.referral_code}"
        referral_text = f"🔗 **رابط الإحالة الخاص بك:**\n\n`{link}`\n\n"
        referral_text += f"📌 **كيفية الاستخدام:**\n"
        referral_text += f"شارك هذا الرابط مع أصدقائك، وعند انضمامهم ستحصل على نقاط مكافأة!"
        await query.edit_message_text(referral_text, parse_mode="Markdown", reply_markup=create_main_menu())
    elif data == "details":
        details = "ℹ️ **تفاصيل البوت Dragon 🐉**\n\n"
        details += "🎮 **المميزات الرئيسية:**\n"
        details += "✅ نظام نقاط متطور\n"
        details += "✅ نظام إحالة مربح\n"
        details += "✅ أزرار تفاعلية سهلة الاستخدام\n"
        details += "✅ دعم أدمن متقدم\n\n"
        details += "💡 **اختر أحد الخيارات أدناه:**"
        await query.edit_message_text(details, parse_mode="Markdown", reply_markup=create_details_menu())
    elif data == "feedback":
        await query.edit_message_text("💬 **أرسل ملاحظتك أو فكرتك الآن:**\n\nقم بكتابة رسالتك وسيتم إرسالها للمطور مباشرة.", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="back_details")]]))
        context.user_data['awaiting_feedback'] = True
    elif data == "back_to_main":
        await query.edit_message_text("👋 اختر من الخيارات:", reply_markup=create_main_menu())
    elif data == "back_details":
        await query.edit_message_text("⬅️ العودة إلى تفاصيل البوت...", reply_markup=create_details_menu())
    elif data.startswith("admin_"):
        if not is_admin(user_id):
            await query.edit_message_text("غير مصرح لك.", reply_markup=create_main_menu())
            return
        if data == "admin_points":
            # قائمة المستخدمين مع النقاط
            users = get_all_users()
            text = "💰 **قائمة النقاط:**\n\n"
            for u in users:
                referrals = sum(1 for usr in users if usr.referred_by == u.user_id)
                text += f"👤 {u.first_name} ({u.user_id})\n"
                text += f"   💎 النقاط: {u.points} | 👥 إحالات: {referrals}\n\n"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=create_admin_menu())
        elif data == "admin_referrals":
            # إحصائيات الإحالات
            users = get_all_users()
            total_referrals = sum(1 for u in users if u.referred_by is not None)
            total_points_from_referrals = total_referrals * POINTS_PER_REFERRAL
            text = f"🔗 **إحصائيات الإحالات:**\n\n"
            text += f"📊 إجمالي الإحالات: **{total_referrals}**\n"
            text += f"💰 إجمالي النقاط من الإحالات: **{total_points_from_referrals}**\n"
            text += f"🎯 نقاط لكل إحالة: **{POINTS_PER_REFERRAL}**"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=create_admin_menu())
        elif data == "admin_users":
            # قائمة المستخدمين
            users = get_all_users()
            text = "👥 **قائمة المستخدمين:**\n\n"
            for u in users:
                status = "🚫 محظور" if u.is_banned else "✅ نشط"
                text += f"• {u.first_name} ({u.user_id}): {status}\n"
            await query.edit_message_text(text, parse_mode="Markdown", reply_markup=create_admin_menu())

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    if context.user_data.get('awaiting_feedback'):
        feedback = update.message.text
        user_info = f"👤 من: {update.effective_user.first_name} (@{update.effective_user.username})\n🆔 المعرف: {user_id}"
        # إرسال للأدمن
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 **ملاحظة جديدة:**\n\n{user_info}\n\n📝 الرسالة:\n{feedback}", parse_mode="Markdown")
        await update.message.reply_text("✅ شكراً لك! تم إرسال ملاحظتك إلى المطور بنجاح.")
        context.user_data['awaiting_feedback'] = False
        await update.message.reply_text("اختر من القائمة:", reply_markup=create_main_menu())
    else:
        await update.message.reply_text("📢 اضغط /start للعودة إلى القائمة الرئيسية.")

# أوامر الأدمن
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك بالوصول إلى لوحة الأدمن.")
        return
    admin_text = "👨‍💼 **لوحة التحكم - الأدمن**\n\nاختر من الخيارات أدناه:"
    await update.message.reply_text(admin_text, parse_mode="Markdown", reply_markup=create_admin_menu())

# إضافة أوامر أدمن إضافية
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ استخدم: `/ban <user_id>`", parse_mode="Markdown")
        return
    try:
        target_id = int(context.args[0])
        user = get_user(target_id)
        if user:
            user.is_banned = True
            save_user(user)
            await update.message.reply_text(f"✅ تم حظر المستخدم **{user.first_name}** ({target_id}) بنجاح.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات.")
    except ValueError:
        await update.message.reply_text("❌ معرف المستخدم غير صحيح.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ استخدم: `/unban <user_id>`", parse_mode="Markdown")
        return
    try:
        target_id = int(context.args[0])
        user = get_user(target_id)
        if user:
            user.is_banned = False
            save_user(user)
            await update.message.reply_text(f"✅ تم إلغاء حظر المستخدم **{user.first_name}** ({target_id}) بنجاح.", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات.")
    except ValueError:
        await update.message.reply_text("❌ معرف المستخدم غير صحيح.")

async def add_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ استخدم: `/add_points <user_id> <points>`", parse_mode="Markdown")
        return
    try:
        target_id = int(context.args[0])
        points = int(context.args[1])
        user = get_user(target_id)
        if user:
            old_points = user.points
            user.points += points
            save_user(user)
            await update.message.reply_text(f"✅ تم إضافة **{points}** نقاط للمستخدم **{user.first_name}**\n💰 النقاط السابقة: {old_points} → الحالية: {user.points}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ المستخدم غير موجود في قاعدة البيانات.")
    except ValueError:
        await update.message.reply_text("❌ المعرف أو النقاط غير صحيحة.")

async def set_referral_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ غير مصرح لك.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ استخدم: `/set_referral_points <points>`", parse_mode="Markdown")
        return
    try:
        new_points = int(context.args[0])
        global POINTS_PER_REFERRAL
        old_points = POINTS_PER_REFERRAL
        POINTS_PER_REFERRAL = new_points
        await update.message.reply_text(f"✅ تم تحديث نقاط الإحالة بنجاح!\n💰 من **{old_points}** إلى **{new_points}** نقطة", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ النقاط غير صحيحة.")