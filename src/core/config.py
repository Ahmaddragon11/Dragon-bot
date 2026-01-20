"""
نظام التكوين المركزي للبوت Dragon-bot.

يحتوي هذا الملف على جميع الإعدادات والمتغيرات اللازمة لتشغيل البوت،
ويتم تحميل معظمها من متغيرات البيئة (.env).
"""

import os
import logging
from typing import Optional, List
from dotenv import load_dotenv
from src.utils.exceptions import ConfigurationError

# تحميل متغيرات البيئة من ملف .env إذا وجد
load_dotenv()


def _get_admin_ids() -> List[int]:
    """
    الحصول على قائمة معرّفات المسؤولين من متغير البيئة.
    
    يتوقع المتغير أن يكون بصيغة: "123,456,789"
    
    Returns:
        List[int]: قائمة معرّفات المسؤولين
        
    Raises:
        ConfigurationError: إذا كانت البيانات غير صحيحة
    """
    admin_ids_str = os.getenv("ADMIN_IDS", "8049455831")
    try:
        return [int(id.strip()) for id in admin_ids_str.split(",")]
    except ValueError as e:
        raise ConfigurationError(
            f"ADMIN_IDS يجب أن تكون قائمة أرقام مفصولة بفواصل. "
            f"القيمة الحالية: {admin_ids_str}"
        ) from e


# --- إعدادات التسجيل (Logging) ---
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
"""مستوى تسجيل السجلات (DEBUG, INFO, WARNING, ERROR, CRITICAL)"""

LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
"""صيغة رسائل السجل"""

LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
"""مسار ملف السجل"""

# إعداد نظام التسجيل
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8")
    ]
)

logger: logging.Logger = logging.getLogger("DragonBot")
"""كائن السجل الرئيسي للبوت"""


# --- إعدادات البوت الأساسية ---
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
"""رمز التحقق من البوت من Telegram Bot Father"""

if not BOT_TOKEN:
    raise ConfigurationError(
        "BOT_TOKEN لم يتم تعيينه. "
        "الرجاء إضافة BOT_TOKEN في ملف .env أو متغيرات البيئة"
    )

# --- إعدادات المسؤولين ---
ADMIN_IDS: List[int] = _get_admin_ids()
"""قائمة معرّفات المسؤولين المصرح لهم بتنفيذ أوامر إدارية"""

PRIMARY_ADMIN_ID: int = ADMIN_IDS[0] if ADMIN_IDS else 0
"""معرّف المسؤول الأساسي (الأول في القائمة)"""

logger.info(f"تم تحميل {len(ADMIN_IDS)} مسؤول(ين)")


# --- إعدادات قاعدة البيانات ---
DATABASE_FILE: str = os.getenv("DATABASE_FILE", "bot_database.db")
"""اسم ملف قاعدة البيانات SQLite"""

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_FILE}"
)
"""رابط الاتصال بقاعدة البيانات"""


# --- إعدادات نظام النقاط والإحالة ---
POINTS_PER_REFERRAL: int = int(os.getenv("POINTS_PER_REFERRAL", "10"))
"""عدد النقاط التي يحصل عليها المستخدم عند إحالة شخص جديد"""

POINTS_PER_MESSAGE: int = int(os.getenv("POINTS_PER_MESSAGE", "1"))
"""عدد النقاط التي يحصل عليها المستخدم عند إرسال رسالة"""


# --- إعدادات نظام المستويات والخبرة (XP) ---
XP_PER_MESSAGE: int = int(os.getenv("XP_PER_MESSAGE", "5"))
"""نقاط الخبرة التي يحصل عليها المستخدم عند إرسال رسالة"""

XP_PER_REFERRAL: int = int(os.getenv("XP_PER_REFERRAL", "50"))
"""نقاط الخبرة التي يحصل عليها المستخدم عند إحالة شخص جديد"""

XP_PER_LEVEL: int = int(os.getenv("XP_PER_LEVEL", "100"))
"""نقاط الخبرة المطلوبة للارتقاء إلى المستوى التالي"""

MAX_LEVEL: int = int(os.getenv("MAX_LEVEL", "100"))
"""الحد الأقصى للمستويات"""


# --- إعدادات الرسائل ---
WELCOME_MESSAGE: str = os.getenv(
    "WELCOME_MESSAGE",
    "👋 مرحباً بك في البوت! اختر أحد الخيارات من القائمة أدناه."
)
"""رسالة الترحيب للمستخدمين الجدد"""

ADMIN_WELCOME_NEW_USER: bool = os.getenv("ADMIN_WELCOME_NEW_USER", "true").lower() == "true"
"""هل يتم إبلاغ المسؤول بكل مستخدم جديد؟"""


# --- إعدادات التطبيق ---
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production").lower()
"""بيئة التطبيق (development, production)"""

DEBUG_MODE: bool = ENVIRONMENT == "development"
"""هل يكون التطبيق في وضع التصحيح؟"""

if DEBUG_MODE:
    logger.warning("⚠️ البوت يعمل في وضع التطوير (Development Mode)")


def validate_config() -> bool:
    """
    التحقق من صحة جميع الإعدادات الحساسة.
    
    Returns:
        bool: True إذا كانت جميع الإعدادات صحيحة
        
    Raises:
        ConfigurationError: إذا كانت هناك مشكلة في الإعدادات
    """
    errors: List[str] = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN مفقود")
    
    if not ADMIN_IDS:
        errors.append("ADMIN_IDS فارغة")
    
    if XP_PER_LEVEL <= 0:
        errors.append("XP_PER_LEVEL يجب أن يكون أكبر من صفر")
    
    if MAX_LEVEL <= 0:
        errors.append("MAX_LEVEL يجب أن يكون أكبر من صفر")
    
    if errors:
        raise ConfigurationError(
            "مشاكل في التكوين:\n" + "\n".join(f"- {error}" for error in errors)
        )
    
    logger.info("✅ تم التحقق من صحة التكوين بنجاح")
    return True


# التحقق من الإعدادات عند تحميل الملف
try:
    validate_config()
except ConfigurationError as e:
    logger.error(f"❌ خطأ في التكوين: {e.message}")
    raise
