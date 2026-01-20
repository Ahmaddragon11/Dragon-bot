# src/bot/handlers/start.py
import datetime
import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.models.user import User
from src.database import get_user, save_user, get_user_by_referral_code
from src.utils import generate_referral_code
from src.core.config import POINTS_PER_REFERRAL, ADMIN_ID
from src.bot.ui import create_main_menu

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر /start."""
    effective_user = update.effective_user
    if not effective_user:
        return

    db_user = get_user(effective_user.id)

    # إذا كان المستخدم محظورًا، لا تفعل شيئًا
    if db_user and db_user.is_banned:
        await update.message.reply_text("❌ أنت محظور من استخدام هذا البوت.")
        return

    # التحقق من وجود إحالة قبل تسجيل المستخدم الجديد
    if not db_user:
        await _check_for_referral(update, context)
        db_user = await _register_new_user(effective_user, context)

    welcome_text = f"👋 أهلاً بك {effective_user.first_name}!\n\nاختر أحد الخيارات من القائمة أدناه:"
    await update.message.reply_text(welcome_text, reply_markup=create_main_menu())

async def _register_new_user(user, context: ContextTypes.DEFAULT_TYPE) -> User:
    """تسجيل مستخدم جديد."""
    referral_code = generate_referral_code()
    new_user = User(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        referral_code=referral_code,
        join_date=datetime.datetime.now(),
        referred_by=context.user_data.get('referrer_id')
    )
    save_user(new_user)
    
    # إرسال إشعار للمدير بوجود مستخدم جديد
    try:
        username_text = f"@{user.username}" if user.username else "لا يوجد"
        admin_message = (
            f"✨ **مستخدم جديد انضم:**\n"
            f"- الاسم: {user.first_name}\n"
            f"- المعرف: {username_text}\n"
            f"- ID: `{user.id}`"
        )
        if new_user.referred_by:
            referrer_user = get_user(new_user.referred_by)
            if referrer_user:
                admin_message += f"\n- انضم عبر: {referrer_user.first_name} (`{referrer_user.user_id}`)"
            
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Failed to send new user notification to admin: {e}")

    return new_user

async def _check_for_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحقق من رمز الإحالة ومكافأة المُحيل."""
    if context.args and len(context.args) > 0:
        referrer_code = context.args[0]
        
        # البحث عن المحيل بواسطة الكود
        referrer = get_user_by_referral_code(referrer_code)

        if referrer and referrer.user_id != update.effective_user.id:
            referrer.points += POINTS_PER_REFERRAL
            save_user(referrer)
            
            # تخزين هوية المحيل لمكافأته لاحقًا عند التسجيل
            context.user_data['referrer_id'] = referrer.user_id

            # إبلاغ المُحيل بنجاح الإحالة
            try:
                await context.bot.send_message(
                    chat_id=referrer.user_id,
                    text=f"🎉 لقد حصلت على {POINTS_PER_REFERRAL} نقطة لأن {update.effective_user.first_name} انضم عبر رابطك!"
                )
            except Exception as e:
                logger.error(f"Failed to send referral notification to {referrer.user_id}: {e}")
            
            # إبلاغ المستخدم الجديد بأنه تمت إحالته
            await update.message.reply_text("🎉 شكرًا لانضمامك عبر دعوة!")
