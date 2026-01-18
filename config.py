# config.py
import os

# Telegram Bot Token - استبدل بتوكن البوت الخاص بك
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# معرف الأدمن (استبدل بمعرفك)
ADMIN_ID = 123456789  # استبدل بمعرف التيليجرام الخاص بك

# قاعدة البيانات
DATABASE_FILE = 'bot.db'

# إعدادات أخرى
POINTS_PER_REFERRAL = 10  # نقاط لكل إحالة
START_POINTS = 0  # نقاط البداية للمستخدم الجديد