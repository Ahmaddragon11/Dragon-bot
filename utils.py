# utils.py
import string
import random
from config import ADMIN_ID
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def generate_referral_code(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def create_main_menu():
    keyboard = [
        [InlineKeyboardButton("نقاطي", callback_data="points")],
        [InlineKeyboardButton("رابط الإحالة", callback_data="referral")],
        [InlineKeyboardButton("تفاصيل البوت", callback_data="details")],
        [InlineKeyboardButton("تواصل مع المطور", url="https://t.me/ahmaddragon")],
        [InlineKeyboardButton("إرسال ملاحظة أو فكرة", callback_data="feedback")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_admin_menu():
    keyboard = [
        [InlineKeyboardButton("إدارة النقاط", callback_data="admin_points")],
        [InlineKeyboardButton("إدارة الإحالات", callback_data="admin_referrals")],
        [InlineKeyboardButton("إدارة المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("العودة للقائمة الرئيسية", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)