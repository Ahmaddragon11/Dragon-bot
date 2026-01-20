"""
نموذج بيانات المستخدم للبوت Dragon-bot.

يحتوي هذا الملف على فئة User التي تمثل مستخدم البوت في قاعدة البيانات
مع جميع خصائصه البيانات الضرورية.
"""

from dataclasses import dataclass, field
from typing import Optional
import datetime


@dataclass
class User:
    """
    يمثل مستخدم البوت مع جميع بياناته.
    
    Attributes:
        user_id (int): معرّف المستخدم الفريد من Telegram
        username (Optional[str]): اسم المستخدم في Telegram (@ username)
        first_name (str): الاسم الأول للمستخدم
        points (int): عدد النقاط التي يملكها المستخدم
        referral_code (str): كود الإحالة الفريد للمستخدم
        referred_by (Optional[int]): معرّف المستخدم الذي أحاله (إن وجد)
        is_banned (bool): هل تم حظر المستخدم؟
        join_date (Optional[datetime.datetime]): تاريخ انضمام المستخدم
        level (int): مستوى المستخدم الحالي
        experience (int): نقاط الخبرة للمستخدم
        rank (str): رتبة المستخدم
    """
    
    user_id: int
    """معرّف المستخدم الفريد"""
    
    username: Optional[str] = None
    """اسم المستخدم في Telegram"""
    
    first_name: str = ""
    """الاسم الأول للمستخدم"""
    
    points: int = 0
    """عدد النقاط الحالية"""
    
    referral_code: str = ""
    """كود الإحالة الفريد"""
    
    referred_by: Optional[int] = None
    """معرّف المحيل (المستخدم الذي دعا هذا المستخدم)"""
    
    is_banned: bool = False
    """حالة الحظر"""
    
    join_date: Optional[datetime.datetime] = None
    """تاريخ الانضمام"""
    
    level: int = 1
    """مستوى المستخدم الحالي (افتراضي: 1)"""
    
    experience: int = 0
    """نقاط الخبرة (XP) للمستخدم"""
    
    rank: str = "مبتدئ"
    """رتبة المستخدم (افتراضي: مبتدئ)"""
    
    def get_display_name(self) -> str:
        """
        الحصول على اسم عرض المستخدم.
        
        Returns:
            str: الاسم الأول إذا كان متوفرًا، وإلا اسم المستخدم، وإلا معرّفه
        """
        if self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        return str(self.user_id)
    
    def is_admin(self, admin_ids: list[int]) -> bool:
        """
        التحقق من كون المستخدم مسؤولاً.
        
        Args:
            admin_ids (list[int]): قائمة معرّفات المسؤولين
            
        Returns:
            bool: True إذا كان المستخدم مسؤولاً
        """
        return self.user_id in admin_ids
