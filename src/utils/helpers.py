# src/utils/helpers.py
import string
import random
from src.core.config import ADMIN_ID

def generate_referral_code(length: int = 8) -> str:
    """إنشاء رمز إحالة فريد."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_admin(user_id: int) -> bool:
    """التحقق مما إذا كان المستخدم هو المسؤول."""
    return user_id == ADMIN_ID
