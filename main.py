"""
نقطة البداية الرئيسية لبوت Dragon.

يحتوي هذا الملف على كود التشغيل الرئيسي للبوت،
بما في ذلك معالجات التحديثات والأخطاء والمحادثات.
"""

import logging
import sys
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)

# --- استيراد الإعدادات والمعالجات ---
from src.core.config import BOT_TOKEN, logger as config_logger, DEBUG_MODE, ADMIN_IDS
from src.database import init_db
from src.bot.handlers import (
    start, button_callback_handler, admin_panel, admin_callback_handler,
    find_user_by_id_handler, find_user_by_username_handler,
    broadcast_message_handler, add_points_handler, cancel_handler,
    show_store_menu, claim_reward_handler, admin_manage_rewards,
    ASK_FOR_USER_ID, ASK_FOR_USERNAME, ASK_FOR_BROADCAST_MESSAGE, ASK_FOR_POINTS
)
from src.utils.exceptions import DragonBotException, ConfigurationError

# --- إعداد تسجيل الأنشطة ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger: logging.Logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    معالج الأخطاء العام للبوت.

    يسجل جميع الأخطاء التي تحدث أثناء معالجة التحديثات
    ويرسل رسالة للمستخدم تخبره بحدوث خطأ.

    Args:
        update (object): التحديث الذي حدث خلاله الخطأ
        context (ContextTypes.DEFAULT_TYPE): السياق

    Returns:
        None
    """
    logger.error(
        f"❌ حدث استثناء أثناء معالجة التحديث: {update}",
        exc_info=context.error
    )

    # محاولة إرسال رسالة للمستخدم إذا كان ممكنًا
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ عذرًا، حدث خطأ داخلي أثناء معالجة طلبك.\n"
                "تم إبلاغ المطور بهذه المشكلة."
            )
        except Exception as e:
            logger.error(f"فشل إرسال رسالة الخطأ: {e}")

    # إرسال إشعار للمسؤول بالخطأ (اختياري)
    if ADMIN_IDS and context.error:
        error_message: str = (
            f"⚠️ **خطأ في البوت**\n\n"
            f"```\n{str(context.error)}\n```\n"
            f"تحديث: {update}"
        )
        
        for admin_id in ADMIN_IDS[:1]:  # إرسال للمسؤول الأول فقط
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=error_message,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"فشل إرسال إشعار الخطأ للمسؤول: {e}")


def main() -> None:
    """
    الدالة الرئيسية لتشغيل البوت.

    تقوم بـ:
    1. تهيئة قاعدة البيانات
    2. إنشاء تطبيق البوت
    3. إضافة معالجات التحديثات
    4. بدء البوت في وضع polling

    Returns:
        None

    Raises:
        ConfigurationError: إذا فشل التكوين
        Exception: إذا فشل تشغيل البوت
    """
    logger.info("=" * 50)
    logger.info("🚀 بدء تشغيل بوت Dragon...")
    logger.info("=" * 50)

    # --- التحقق من التكوين ---
    try:
        if not BOT_TOKEN:
            raise ConfigurationError("BOT_TOKEN لم يتم تعيينه")
        if not ADMIN_IDS:
            raise ConfigurationError("ADMIN_IDS فارغة")
        logger.info(f"✅ التكوين صحيح. عدد المسؤولين: {len(ADMIN_IDS)}")
    except ConfigurationError as e:
        logger.critical(f"❌ خطأ في التكوين: {e.message}")
        return

    # --- تهيئة قاعدة البيانات ---
    try:
        init_db()
        logger.info("✅ تم تهيئة قاعدة البيانات بنجاح")
    except Exception as e:
        logger.critical(f"❌ فشل تهيئة قاعدة البيانات: {e}", exc_info=True)
        return

    try:
        # --- إنشاء كائن التطبيق ---
        logger.info(f"🔧 إنشاء تطبيق البوت...")
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("✅ تم إنشاء التطبيق بنجاح")

        # --- محادثة المدير (للبحث عن مستخدم، الإذاعة، إلخ) ---
        admin_conv_handler = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    admin_callback_handler,
                    pattern=r'^(admin_find_user_by_id|admin_find_user_by_username|admin_broadcast|admin_add_points_)'
                )
            ],
            states={
                ASK_FOR_USER_ID: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        find_user_by_id_handler
                    )
                ],
                ASK_FOR_USERNAME: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        find_user_by_username_handler
                    )
                ],
                ASK_FOR_BROADCAST_MESSAGE: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        broadcast_message_handler
                    )
                ],
                ASK_FOR_POINTS: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND,
                        add_points_handler
                    )
                ],
            },
            fallbacks=[
                CommandHandler('cancel', cancel_handler),
                CallbackQueryHandler(admin_callback_handler, pattern='^admin_panel$')
            ],
            per_message=False
        )

        logger.info("📝 إضافة معالجات التحديثات...")

        # --- إضافة المعالجات الأساسية ---
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("admin", admin_panel))

        # معالج أزرار المستخدم العادي
        application.add_handler(
            CallbackQueryHandler(
                button_callback_handler,
                pattern=r'^(user_|main_menu|about_|store)'
            )
        )

        # معالج أزرار المدير (خارج المحادثة)
        application.add_handler(
            CallbackQueryHandler(
                admin_callback_handler,
                pattern=r'^(admin_|top_|manage_)'
            )
        )
        
        # معالج المكافآت
        async def reward_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """معالج استعلامات المكافآت."""
            reward_id_str = update.callback_query.data.split('_')[-1]
            try:
                reward_id = int(reward_id_str)
                await claim_reward_handler(update, context, reward_id)
            except (ValueError, IndexError):
                logger.warning(f"معرّف مكافأة غير صحيح: {reward_id_str}")
                await update.callback_query.answer("❌ خطأ في المكافأة", show_alert=True)
        
        application.add_handler(
            CallbackQueryHandler(
                reward_callback_handler,
                pattern=r'^claim_reward_\d+$'
            )
        )

        # إضافة محادثة المدير
        application.add_handler(admin_conv_handler)

        # إضافة معالج الأخطاء العالمي
        application.add_error_handler(error_handler)

        logger.info("✅ تم إضافة جميع المعالجات")

        # --- عرض معلومات البدء ---
        if DEBUG_MODE:
            logger.warning("⚠️ البوت يعمل في وضع التطوير")
        
        logger.info(f"📱 مسؤولون: {ADMIN_IDS}")
        logger.info("🟢 البوت جاهز للعمل")
        logger.info("=" * 50)

        # --- بدء البوت ---
        logger.info("🚀 بدء البوت بنمط polling...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

    except KeyboardInterrupt:
        logger.info("⏹️ تم إيقاف البوت من قبل المستخدم")
    except Exception as e:
        logger.critical(
            f"❌ خطأ فادح أثناء تشغيل البوت: {e}",
            exc_info=True
        )
    finally:
        logger.info("=" * 50)
        logger.info("🛑 تم إيقاف البوت")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()
