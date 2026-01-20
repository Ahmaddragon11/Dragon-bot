"""
مدير الرسائل المخصصة للبوت.

يتعامل مع إنشاء وتعديل واسترجاع الرسائل المخصصة.
"""

import logging
from typing import Optional, Dict, Any
from src.models.message import BotMessage, DEFAULT_MESSAGES
from src.utils.exceptions import InvalidOperation

logger: logging.Logger = logging.getLogger(__name__)


class MessageManager:
    """
    مدير الرسائل - يتعامل مع تخزين واسترجاع الرسائل المخصصة.
    """
    
    def __init__(self):
        """تهيئة مدير الرسائل بالرسائل الافتراضية."""
        self._messages: Dict[str, BotMessage] = DEFAULT_MESSAGES.copy()
    
    def get_message(self, message_id: str) -> Optional[BotMessage]:
        """
        الحصول على رسالة برقمها.
        
        Args:
            message_id (str): معرّف الرسالة
            
        Returns:
            Optional[BotMessage]: كائن الرسالة أو None
        """
        return self._messages.get(message_id)
    
    def get_formatted_message(self, message_id: str, **kwargs) -> str:
        """
        الحصول على رسالة منسقة بالمتغيرات.
        
        Args:
            message_id (str): معرّف الرسالة
            **kwargs: قاموس المتغيرات
            
        Returns:
            str: الرسالة المنسقة
        """
        message = self.get_message(message_id)
        
        if not message:
            logger.warning(f"رسالة غير موجودة: {message_id}")
            return f"❌ رسالة غير موجودة: {message_id}"
        
        if not message.is_active:
            logger.warning(f"رسالة معطلة: {message_id}")
            return f"⚠️ الرسالة معطلة: {message_id}"
        
        try:
            return message.format(**kwargs)
        except Exception as e:
            logger.error(f"خطأ في تنسيق الرسالة {message_id}: {e}")
            return f"❌ خطأ في الرسالة: {str(e)}"
    
    def update_message(self, message_id: str, content: str) -> bool:
        """
        تحديث محتوى الرسالة.
        
        Args:
            message_id (str): معرّف الرسالة
            content (str): المحتوى الجديد
            
        Returns:
            bool: هل تم التحديث بنجاح؟
            
        Raises:
            InvalidOperation: إذا لم تجد الرسالة
        """
        message = self.get_message(message_id)
        
        if not message:
            raise InvalidOperation(f"الرسالة {message_id} غير موجودة")
        
        if not content:
            raise InvalidOperation("المحتوى الجديد مطلوب")
        
        message.content = content
        message.updated_at = __import__('datetime').datetime.now()
        
        logger.info(f"تم تحديث الرسالة: {message_id}")
        return True
    
    def add_message(self, message_id: str, name: str, content: str, description: str = "", variables: list = None) -> BotMessage:
        """
        إضافة رسالة جديدة.
        
        Args:
            message_id (str): معرّف الرسالة
            name (str): اسم الرسالة
            content (str): المحتوى
            description (str): الوصف
            variables (list): قائمة المتغيرات
            
        Returns:
            BotMessage: الرسالة الجديدة
            
        Raises:
            InvalidOperation: إذا كانت البيانات غير صحيحة
        """
        if message_id in self._messages:
            raise InvalidOperation(f"الرسالة {message_id} موجودة بالفعل")
        
        if not message_id or not name or not content:
            raise InvalidOperation("جميع الحقول مطلوبة")
        
        message = BotMessage(
            message_id=message_id,
            name=name,
            content=content,
            description=description,
            variables=variables or []
        )
        
        self._messages[message_id] = message
        logger.info(f"تمت إضافة رسالة جديدة: {message_id}")
        return message
    
    def delete_message(self, message_id: str) -> bool:
        """
        حذف رسالة (تعطيلها بدلاً من الحذف الدائم).
        
        Args:
            message_id (str): معرّف الرسالة
            
        Returns:
            bool: هل تم الحذف بنجاح؟
            
        Raises:
            InvalidOperation: إذا لم تجد الرسالة
        """
        message = self.get_message(message_id)
        
        if not message:
            raise InvalidOperation(f"الرسالة {message_id} غير موجودة")
        
        message.is_active = False
        logger.info(f"تم تعطيل الرسالة: {message_id}")
        return True
    
    def activate_message(self, message_id: str) -> bool:
        """
        تفعيل رسالة معطلة.
        
        Args:
            message_id (str): معرّف الرسالة
            
        Returns:
            bool: هل تم التفعيل بنجاح؟
            
        Raises:
            InvalidOperation: إذا لم تجد الرسالة
        """
        message = self.get_message(message_id)
        
        if not message:
            raise InvalidOperation(f"الرسالة {message_id} غير موجودة")
        
        message.is_active = True
        logger.info(f"تم تفعيل الرسالة: {message_id}")
        return True
    
    def get_all_messages(self) -> Dict[str, BotMessage]:
        """
        الحصول على جميع الرسائل.
        
        Returns:
            Dict[str, BotMessage]: قاموس بجميع الرسائل
        """
        return self._messages.copy()
    
    def get_active_messages(self) -> Dict[str, BotMessage]:
        """
        الحصول على الرسائل المفعلة فقط.
        
        Returns:
            Dict[str, BotMessage]: قاموس الرسائل المفعلة
        """
        return {
            msg_id: msg for msg_id, msg in self._messages.items()
            if msg.is_active
        }
    
    def reset_to_defaults(self) -> bool:
        """
        إعادة تعيين جميع الرسائل إلى الافتراضية.
        
        Returns:
            bool: هل تم بنجاح؟
        """
        self._messages = DEFAULT_MESSAGES.copy()
        logger.info("تم إعادة تعيين الرسائل إلى الافتراضية")
        return True
    
    def get_message_stats(self) -> dict:
        """
        الحصول على إحصائيات الرسائل.
        
        Returns:
            dict: قاموس بالإحصائيات
        """
        total = len(self._messages)
        active = sum(1 for m in self._messages.values() if m.is_active)
        
        return {
            "total_messages": total,
            "active_messages": active,
            "inactive_messages": total - active,
        }


# إنشاء مثيل من مدير الرسائل
message_manager = MessageManager()
