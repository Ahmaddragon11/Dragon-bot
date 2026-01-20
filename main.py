import logging
import sys
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
)

# --- استيراد الإعدادات والمعالجات ---
from src.core.config import TOKEN
from src.database import init_db
from src.bot.handlers import (
    start, button_callback_handler, admin_panel, admin_callback_handler,
    find_user_by_id_handler, find_user_by_username_handler, 
    broadcast_message_handler, add_points_handler, cancel_handler,
    ASK_FOR_USER_ID, ASK_FOR_USERNAME, ASK_FOR_BROADCAST_MESSAGE, ASK_FOR_POINTS
)

# --- إعداد تسجيل الأنشطة ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """تسجيل الأخطاء التي تحدث أثناء معالجة التحديثات."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ عذرًا، حدث خطأ داخلي أثناء معالجة طلبك. تم إبلاغ المطور."
        )

def main() -> None:
    """البدء والتشغيل المستمر للبوت."""
    # تهيئة قاعدة البيانات
    try:
        init_db()
        logger.info("✅ تم تهيئة قاعدة البيانات بنجاح.")
    except Exception as e:
        logger.error(f"❌ فشل تهيئة قاعدة البيانات: {e}")
        return

    # إنشاء كائن التطبيق
    application = Application.builder().token(TOKEN).build()

    # --- محادثة المدير (للبحث عن مستخدم، الإذاعة، إلخ) ---
    admin_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_callback_handler, pattern='^(admin_find_user_by_id|admin_find_user_by_username|admin_broadcast|admin_add_points_)')
        ],
        states={
            ASK_FOR_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_user_by_id_handler)],
            ASK_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_user_by_username_handler)],
            ASK_FOR_BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message_handler)],
            ASK_FOR_POINTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_points_handler)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
            CallbackQueryHandler(admin_callback_handler, pattern='^admin_panel$')
        ],
        per_message=False
    )

    # --- إضافة المعالجات ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_panel))
    
    # معالج أزرار المستخدم
    application.add_handler(CallbackQueryHandler(button_callback_handler, pattern='^(user_|main_menu|about_)'))
    
    # معالج أزرار المدير (خارج المحادثة)
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern='^(admin_|top_|manage_)'))
    
    # إضافة محادثة المدير
    application.add_handler(admin_conv_handler)

    # إضافة معالج الأخطاء العالمي
    application.add_error_handler(error_handler)

    # --- بدء البوت ---
    logger.info("🚀 البوت قيد التشغيل...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
