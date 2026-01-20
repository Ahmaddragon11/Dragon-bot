"""
نموذج ونظام إدارة الرسائل المخصصة للبوت.

يسمح للمسؤولين بتخصيص جميع رسائل البوت الهامة.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import datetime


@dataclass
class BotMessage:
    """
    يمثل رسالة مخصصة من البوت.
    
    Attributes:
        message_id (str): معرّف الرسالة الفريد
        name (str): اسم الرسالة (للإشارة إليها في الكود)
        content (str): محتوى الرسالة (يدعم المتغيرات)
        description (str): وصف الرسالة
        variables (List[str]): قائمة المتغيرات المدعومة
        is_active (bool): هل الرسالة مفعلة؟
        created_at (datetime.datetime): تاريخ الإنشاء
        updated_at (datetime.datetime): تاريخ التحديث
    """
    
    message_id: str
    """معرّف الرسالة الفريد"""
    
    name: str
    """اسم الرسالة"""
    
    content: str
    """محتوى الرسالة"""
    
    description: str = ""
    """وصف الرسالة"""
    
    variables: list = field(default_factory=list)
    """قائمة المتغيرات المدعومة"""
    
    is_active: bool = True
    """حالة الرسالة"""
    
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ الإنشاء"""
    
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ التحديث"""
    
    def format(self, **kwargs) -> str:
        """
        تنسيق الرسالة بإدراج المتغيرات.
        
        Args:
            **kwargs: قاموس بقيم المتغيرات
            
        Returns:
            str: الرسالة المنسقة
            
        Example:
            >>> msg = BotMessage(
            ...     message_id="welcome",
            ...     name="Welcome",
            ...     content="مرحبا {name}! أنت في المستوى {level}"
            ... )
            >>> msg.format(name="أحمد", level=5)
            'مرحبا أحمد! أنت في المستوى 5'
        """
        try:
            return self.content.format(**kwargs)
        except KeyError as e:
            return f"❌ خطأ: متغير مفقود {e}"
    
    def validate(self) -> bool:
        """
        التحقق من صحة الرسالة.
        
        Returns:
            bool: هل الرسالة صحيحة؟
        """
        if not self.message_id or not self.name or not self.content:
            return False
        
        return True


# الرسائل الافتراضية للبوت
DEFAULT_MESSAGES = {
    "welcome": BotMessage(
        message_id="welcome",
        name="Welcome Message",
        content="👋 مرحباً بك {first_name}!\n\nاختر أحد الخيارات من القائمة أدناه:",
        description="رسالة الترحيب للمستخدم الجديد",
        variables=["first_name"]
    ),
    
    "new_level": BotMessage(
        message_id="new_level",
        name="Level Up Message",
        content="🎉 **تهانينا! لقد ارتقيت مستوى!**\n\nمستواك الجديد: {level}\nرتبتك: {rank}",
        description="رسالة الارتقاء للمستوى الجديد",
        variables=["level", "rank"]
    ),
    
    "referral_success": BotMessage(
        message_id="referral_success",
        name="Referral Success",
        content="🎉 لقد حصلت على {points} نقطة لأن {user_name} انضم عبر رابطك!",
        description="رسالة نجاح الإحالة",
        variables=["points", "user_name"]
    ),
    
    "reward_claimed": BotMessage(
        message_id="reward_claimed",
        name="Reward Claimed",
        content="✅ تم الحصول على المكافأة: {reward_name}\nنقاطك المتبقية: {remaining_points}",
        description="رسالة الحصول على مكافأة",
        variables=["reward_name", "remaining_points"]
    ),
    
    "task_completed": BotMessage(
        message_id="task_completed",
        name="Task Completed",
        content="✅ تم إكمال المهمة: {task_name}\nمكافأة: +{reward_points} نقطة و +{reward_xp} XP",
        description="رسالة إكمال مهمة",
        variables=["task_name", "reward_points", "reward_xp"]
    ),
    
    "insufficient_points": BotMessage(
        message_id="insufficient_points",
        name="Insufficient Points",
        content="⚠️ نقاطك ({current_points}) غير كافية.\nتحتاج إلى {required_points} نقطة",
        description="رسالة النقاط غير الكافية",
        variables=["current_points", "required_points"]
    ),
    
    "error_message": BotMessage(
        message_id="error_message",
        name="Error Message",
        content="❌ عذرًا، حدث خطأ: {error}\nتم إبلاغ المطور بهذه المشكلة.",
        description="رسالة الخطأ العام",
        variables=["error"]
    ),
    
    "admin_new_user": BotMessage(
        message_id="admin_new_user",
        name="Admin New User Notification",
        content="✨ **مستخدم جديد انضم:**\nالاسم: {first_name}\nالمعرف: {user_id}\nالدعوة من: {referrer_name}",
        description="إشعار المسؤول بمستخدم جديد",
        variables=["first_name", "user_id", "referrer_name"]
    ),
}
