# src/core/config.py
import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة من ملف .env إذا وجد
load_dotenv()

# --- إعدادات البوت الأساسية ---
# يتم جلب التوكن من متغيرات البيئة، وإذا لم يوجد يستخدم القيمة الافتراضية (للتوافق)
TOKEN = os.getenv("BOT_TOKEN", "8560191198:AAESq5lFAdCuWShReqPy9KkLzjVfE4VgZmE")

# --- إعدادات المدير ---
ADMIN_ID = int(os.getenv("ADMIN_ID", 8049455831))

# --- إعدادات قاعدة البيانات ---
DATABASE_FILE = os.getenv("DATABASE_FILE", "bot_database.db")

# --- إعدادات نظام النقاط والإحالة ---
POINTS_PER_REFERRAL = int(os.getenv("POINTS_PER_REFERRAL", 10))
