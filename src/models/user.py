# src/models/user.py
from dataclasses import dataclass, field
from typing import Optional
import datetime

@dataclass
class User:
    """يمثل هذا الكلاس مستخدم البوت في قاعدة البيانات."""
    user_id: int
    username: Optional[str] = None
    first_name: str = ""
    points: int = 0
    referral_code: str = ""
    referred_by: Optional[int] = None
    is_banned: bool = False
    join_date: Optional[datetime.datetime] = None
