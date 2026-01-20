"""
نظام الإشعارات المتقدم للمشرفين.

يسمح بإرسال إشعارات مختلفة للمشرفين حسب أهميتها وتفضيلاتهم.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import datetime
import logging

logger: logging.Logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """مستويات الإشعارات."""
    
    LOW = "منخفضة"
    MEDIUM = "متوسطة"
    HIGH = "عالية"
    CRITICAL = "حرجة"


class NotificationType(Enum):
    """أنواع الإشعارات."""
    
    NEW_USER = "مستخدم جديد"
    LEVEL_UP = "ارتقاء مستوى"
    REWARD_CLAIMED = "مكافأة مطالب بها"
    TASK_COMPLETED = "مهمة مكتملة"
    ERROR = "خطأ"
    REFERRAL = "إحالة"
    BAN = "حظر"
    ADMIN_ACTION = "إجراء إداري"


@dataclass
class Notification:
    """
    يمثل إشعار للمشرف.
    
    Attributes:
        notification_id (int): معرّف الإشعار
        notification_type (NotificationType): نوع الإشعار
        level (NotificationLevel): مستوى الأهمية
        title (str): عنوان الإشعار
        message (str): محتوى الإشعار
        related_user_id (Optional[int]): معرّف المستخدم ذي الصلة
        data (dict): بيانات إضافية
        read (bool): هل تم قراءته؟
        created_at (datetime.datetime): وقت الإنشاء
    """
    
    notification_id: int
    """معرّف الإشعار"""
    
    notification_type: NotificationType
    """نوع الإشعار"""
    
    level: NotificationLevel
    """مستوى الأهمية"""
    
    title: str
    """عنوان الإشعار"""
    
    message: str
    """محتوى الإشعار"""
    
    related_user_id: Optional[int] = None
    """معرّف المستخدم ذي الصلة"""
    
    data: dict = field(default_factory=dict)
    """بيانات إضافية"""
    
    read: bool = False
    """حالة القراءة"""
    
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """وقت الإنشاء"""
    
    def get_emoji(self) -> str:
        """
        الحصول على رمز تعبيري للإشعار حسب النوع والمستوى.
        
        Returns:
            str: الرمز التعبيري
        """
        level_emoji = {
            NotificationLevel.LOW: "ℹ️",
            NotificationLevel.MEDIUM: "ℹ️",
            NotificationLevel.HIGH: "⚠️",
            NotificationLevel.CRITICAL: "🚨",
        }
        
        return level_emoji.get(self.level, "ℹ️")
    
    def get_formatted(self) -> str:
        """
        الحصول على الإشعار بصيغة مجهزة للإرسال.
        
        Returns:
            str: الإشعار المنسق
        """
        return (
            f"{self.get_emoji()} **[{self.level.value}] {self.title}**\n\n"
            f"{self.message}\n\n"
            f"⏰ {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        )


class NotificationManager:
    """
    مدير الإشعارات - يتعامل مع إنشاء وإدارة الإشعارات.
    """
    
    def __init__(self):
        """تهيئة مدير الإشعارات."""
        self._notifications: Dict[int, Notification] = {}
        self._notification_id_counter = 1
        self._admin_preferences: Dict[int, set] = {}  # admin_id -> set of notification types
    
    def create_notification(
        self,
        notification_type: NotificationType,
        level: NotificationLevel,
        title: str,
        message: str,
        related_user_id: Optional[int] = None,
        data: Optional[dict] = None
    ) -> Notification:
        """
        إنشاء إشعار جديد.
        
        Args:
            notification_type (NotificationType): نوع الإشعار
            level (NotificationLevel): مستوى الأهمية
            title (str): العنوان
            message (str): المحتوى
            related_user_id (Optional[int]): معرّف المستخدم ذي الصلة
            data (Optional[dict]): بيانات إضافية
            
        Returns:
            Notification: الإشعار الجديد
        """
        notification = Notification(
            notification_id=self._notification_id_counter,
            notification_type=notification_type,
            level=level,
            title=title,
            message=message,
            related_user_id=related_user_id,
            data=data or {}
        )
        
        self._notifications[self._notification_id_counter] = notification
        self._notification_id_counter += 1
        
        logger.info(f"تم إنشاء إشعار: {title} (المستوى: {level.value})")
        return notification
    
    def get_notifications_for_admin(
        self,
        admin_id: int,
        unread_only: bool = True,
        limit: int = 10
    ) -> List[Notification]:
        """
        الحصول على الإشعارات المناسبة للمسؤول.
        
        Args:
            admin_id (int): معرّف المسؤول
            unread_only (bool): هل تريد فقط الإشعارات غير المقروءة؟
            limit (int): الحد الأقصى للإشعارات
            
        Returns:
            List[Notification]: قائمة الإشعارات
        """
        # الحصول على تفضيلات المسؤول
        preferred_types = self._admin_preferences.get(admin_id)
        
        notifications = list(self._notifications.values())
        
        # تصفية حسب التفضيلات
        if preferred_types:
            notifications = [
                n for n in notifications
                if n.notification_type in preferred_types
            ]
        
        # تصفية حسب قراءة
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        # ترتيب حسب الوقت
        notifications.sort(key=lambda n: n.created_at, reverse=True)
        
        return notifications[:limit]
    
    def mark_as_read(self, notification_id: int) -> bool:
        """
        تحديد الإشعار كمقروء.
        
        Args:
            notification_id (int): معرّف الإشعار
            
        Returns:
            bool: هل تم بنجاح؟
        """
        notification = self._notifications.get(notification_id)
        
        if not notification:
            return False
        
        notification.read = True
        logger.debug(f"تم تحديد الإشعار {notification_id} كمقروء")
        return True
    
    def mark_all_as_read(self, admin_id: int) -> int:
        """
        تحديد جميع إشعارات المسؤول كمقروءة.
        
        Args:
            admin_id (int): معرّف المسؤول
            
        Returns:
            int: عدد الإشعارات المحدثة
        """
        count = 0
        
        for notification in self._notifications.values():
            if not notification.read:
                notification.read = True
                count += 1
        
        logger.info(f"تم تحديد {count} إشعار كمقروء للمسؤول {admin_id}")
        return count
    
    def set_admin_preferences(self, admin_id: int, notification_types: List[NotificationType]) -> bool:
        """
        تعيين تفضيلات الإشعارات للمسؤول.
        
        Args:
            admin_id (int): معرّف المسؤول
            notification_types (List[NotificationType]): أنواع الإشعارات المفضلة
            
        Returns:
            bool: هل تم بنجاح؟
        """
        self._admin_preferences[admin_id] = set(notification_types)
        logger.info(f"تم تعيين تفضيلات الإشعارات للمسؤول {admin_id}")
        return True
    
    def get_admin_preferences(self, admin_id: int) -> List[NotificationType]:
        """
        الحصول على تفضيلات المسؤول.
        
        Args:
            admin_id (int): معرّف المسؤول
            
        Returns:
            List[NotificationType]: قائمة الأنواع المفضلة
        """
        if admin_id not in self._admin_preferences:
            # الافتراضي: جميع الأنواع
            return list(NotificationType)
        
        return list(self._admin_preferences[admin_id])
    
    def get_notification_stats(self) -> dict:
        """
        الحصول على إحصائيات الإشعارات.
        
        Returns:
            dict: قاموس بالإحصائيات
        """
        total = len(self._notifications)
        unread = sum(1 for n in self._notifications.values() if not n.read)
        
        by_type = {}
        for notification in self._notifications.values():
            notif_type = notification.notification_type.value
            by_type[notif_type] = by_type.get(notif_type, 0) + 1
        
        by_level = {}
        for notification in self._notifications.values():
            level = notification.level.value
            by_level[level] = by_level.get(level, 0) + 1
        
        return {
            "total_notifications": total,
            "unread_notifications": unread,
            "read_notifications": total - unread,
            "by_type": by_type,
            "by_level": by_level,
        }
    
    def clear_old_notifications(self, days: int = 30) -> int:
        """
        حذف الإشعارات القديمة.
        
        Args:
            days (int): عدد الأيام
            
        Returns:
            int: عدد الإشعارات المحذوفة
        """
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        to_delete = [
            notif_id for notif_id, notification in self._notifications.items()
            if notification.created_at < cutoff_date
        ]
        
        for notif_id in to_delete:
            del self._notifications[notif_id]
        
        logger.info(f"تم حذف {len(to_delete)} إشعار قديم")
        return len(to_delete)


# إنشاء مثيل من مدير الإشعارات
notification_manager = NotificationManager()
