"""
معالج أمر /start والعمليات المتعلقة بتسجيل المستخدمين الجدد.

يتعامل هذا الملف مع:
- تسجيل المستخدمين الجدد
- التحقق من رموز الإحالة
- إبلاغ المسؤول بالمستخدمين الجدد
"""

import datetime
import logging
from typing import Optional
from telegram import Update
from telegram.ext import ContextTypes
from src.models.user import User
from src.database import get_user, save_user, get_user_by_referral_code
from src.utils.helpers import generate_referral_code, is_admin
from src.core.config import POINTS_PER_REFERRAL, ADMIN_IDS, PRIMARY_ADMIN_ID
from src.bot.ui import create_main_menu
from src.utils.exceptions import UserNotFound, UserBanned, DatabaseError

logger: logging.Logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج أمر /start الرئيسي.
    
    يتحقق من وجود المستخدم وتسجيل المستخدمين الجدد، 
    ويعالج رموز الإحالة.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    effective_user = update.effective_user
    if not effective_user:
        logger.warning("⚠️ لم يتم العثور على معلومات المستخدم")
        return

    try:
        db_user: Optional[User] = get_user(effective_user.id)

        # إذا كان المستخدم محظورًا، لا تفعل شيئًا
        if db_user and db_user.is_banned:
            await update.message.reply_text("❌ أنت محظور من استخدام هذا البوت.")
            logger.warning(f"محاولة وصول من مستخدم محظور: {effective_user.id}")
            return

        # التحقق من وجود إحالة قبل تسجيل المستخدم الجديد
        if not db_user:
            await _check_for_referral(update, context)
            db_user = await _register_new_user(effective_user, context)

        # عرض الترحيب والقائمة الرئيسية
        welcome_text: str = (
            f"👋 أهلاً بك {effective_user.first_name}!\n\n"
            "اختر أحد الخيارات من القائمة أدناه:"
        )
        await update.message.reply_text(
            welcome_text,
            reply_markup=create_main_menu()
        )
        logger.info(f"✅ رحب البوت بالمستخدم: {effective_user.id} ({effective_user.first_name})")

    except UserBanned as e:
        await update.message.reply_text(f"❌ {e.message}")
        logger.warning(f"محاولة وصول من مستخدم محظور: {e.message}")
    except DatabaseError as e:
        await update.message.reply_text("❌ عذرًا، حدث خطأ في قاعدة البيانات.")
        logger.error(f"❌ خطأ في قاعدة البيانات: {e.message}")
    except Exception as e:
        await update.message.reply_text(
            "❌ عذرًا، حدث خطأ داخلي. تم إبلاغ المطور."
        )
        logger.error(f"❌ خطأ غير متوقع في معالج /start: {str(e)}", exc_info=True)


async def _register_new_user(
    user: any,
    context: ContextTypes.DEFAULT_TYPE
) -> User:
    """
    تسجيل مستخدم جديد في قاعدة البيانات.
    
    Args:
        user: كائن المستخدم من Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        User: كائن المستخدم الجديد
        
    Raises:
        DatabaseError: في حالة فشل حفظ المستخدم
    """
    try:
        referral_code: str = generate_referral_code()
        new_user = User(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            referral_code=referral_code,
            join_date=datetime.datetime.now(),
            referred_by=context.user_data.get('referrer_id')
        )
        save_user(new_user)
        logger.info(f"✅ تم تسجيل مستخدم جديد: {user.id} ({user.first_name})")

        # إرسال إشعار للمدير بوجود مستخدم جديد
        await _notify_admin_new_user(user, new_user, context)

        return new_user

    except DatabaseError as e:
        logger.error(f"❌ فشل تسجيل المستخدم {user.id}: {e.message}")
        raise


async def _notify_admin_new_user(
    user: any,
    new_user: User,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    إرسال إشعار للمسؤول بوجود مستخدم جديد.
    
    Args:
        user: كائن المستخدم من Telegram
        new_user (User): كائن المستخدم الجديد
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    try:
        username_text: str = f"@{user.username}" if user.username else "لا يوجد"
        admin_message: str = (
            f"✨ **مستخدم جديد انضم:**\n"
            f"- الاسم: {user.first_name}\n"
            f"- المعرف: {username_text}\n"
            f"- ID: `{user.id}`"
        )

        if new_user.referred_by:
            referrer_user: Optional[User] = get_user(new_user.referred_by)
            if referrer_user:
                admin_message += f"\n- انضم عبر: {referrer_user.first_name} (`{referrer_user.user_id}`)"

        # إرسال الإشعار لجميع المسؤولين
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"فشل إرسال إشعار للمسؤول {admin_id}: {e}")

    except Exception as e:
        logger.error(f"خطأ في إخطار المسؤول بمستخدم جديد: {e}", exc_info=True)


async def _check_for_referral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    التحقق من رمز الإحالة ومكافأة المُحيل.
    
    يتحقق من وجود رمز إحالة في أوامر البوت
    ويكافئ المُحيل بنقاط.
    
    Args:
        update (Update): تحديث Telegram
        context (ContextTypes.DEFAULT_TYPE): السياق
        
    Returns:
        None
    """
    if not context.args or len(context.args) == 0:
        return

    referrer_code: str = context.args[0]

    try:
        # البحث عن المحيل بواسطة الكود
        referrer: Optional[User] = get_user_by_referral_code(referrer_code)

        if not referrer or referrer.user_id == update.effective_user.id:
            logger.warning(
                f"محاولة استخدام رمز إحالة غير صحيح: {referrer_code} "
                f"من قبل المستخدم {update.effective_user.id}"
            )
            return

        # مكافأة المُحيل بالنقاط
        referrer.points += POINTS_PER_REFERRAL
        save_user(referrer)
        logger.info(f"✅ تم مكافأة المُحيل {referrer.user_id} بـ {POINTS_PER_REFERRAL} نقطة")

        # تخزين هوية المحيل لمكافأته لاحقًا عند التسجيل
        context.user_data['referrer_id'] = referrer.user_id

        # إبلاغ المُحيل بنجاح الإحالة
        try:
            await context.bot.send_message(
                chat_id=referrer.user_id,
                text=(
                    f"🎉 لقد حصلت على {POINTS_PER_REFERRAL} نقطة "
                    f"لأن {update.effective_user.first_name} انضم عبر رابطك!"
                )
            )
        except Exception as e:
            logger.error(f"فشل إرسال إشعار الإحالة إلى {referrer.user_id}: {e}")

        # إبلاغ المستخدم الجديد بأنه تمت إحالته
        await update.message.reply_text("🎉 شكرًا لانضمامك عبر دعوة!")

    except DatabaseError as e:
        logger.error(f"❌ خطأ في معالجة الإحالة: {e.message}")
    except Exception as e:
        logger.error(f"❌ خطأ غير متوقع في معالجة الإحالة: {str(e)}", exc_info=True)
