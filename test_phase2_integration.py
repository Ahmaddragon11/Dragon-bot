"""
اختبار التكامل للتحقق من جميع المكونات الجديدة في Phase 2.

يتحقق من:
1. استيراد جميع المديرين
2. إنشاء نماذج
3. العمليات الأساسية
"""

import sys
from typing import List


def test_imports() -> bool:
    """اختبار استيراد جميع المكونات."""
    print("🔍 اختبار الاستيراد...")
    
    try:
        # استيراد المديرين
        from src.utils import (
            task_manager,
            message_manager,
            notification_manager,
            advanced_stats_manager,
        )
        print("  ✅ تم استيراد المديرين بنجاح")
        
        # استيراد النماذج
        from src.models import Task, TaskDifficulty, TaskFrequency
        from src.models.message import BotMessage, DEFAULT_MESSAGES
        from src.utils.notification_manager import (
            Notification, NotificationType, NotificationLevel
        )
        print("  ✅ تم استيراد النماذج بنجاح")
        
        # استيراد المعالجات
        from src.bot.handlers import (
            show_notifications_menu,
            notifications_callback_handler,
            toggle_notification_type,
        )
        print("  ✅ تم استيراد المعالجات بنجاح")
        
        return True
    except ImportError as e:
        print(f"  ❌ خطأ في الاستيراد: {e}")
        return False


def test_task_manager() -> bool:
    """اختبار TaskManager."""
    print("\n🎯 اختبار TaskManager...")
    
    try:
        from src.utils import task_manager
        from src.models import TaskDifficulty, TaskFrequency
        
        # إنشاء مهمة
        task = task_manager.create_task(
            name="مهمة اختبار",
            description="اختبار",
            reward_points=10,
            reward_xp=20,
            difficulty=TaskDifficulty.EASY,
            frequency=TaskFrequency.DAILY
        )
        print(f"  ✅ تم إنشاء مهمة: {task.name}")
        
        # الحصول على المهمة
        fetched = task_manager.get_task(task.task_id)
        assert fetched is not None
        print(f"  ✅ تم جلب المهمة: {fetched.name}")
        
        return True
    except Exception as e:
        print(f"  ❌ خطأ في TaskManager: {e}")
        return False


def test_message_manager() -> bool:
    """اختبار MessageManager."""
    print("\n💬 اختبار MessageManager...")
    
    try:
        from src.utils import message_manager
        from src.models.message import DEFAULT_MESSAGES
        
        # اختبار الرسائل الافتراضية
        welcome_msg = message_manager.get_message("welcome")
        assert welcome_msg is not None
        print(f"  ✅ تم جلب رسالة الترحيب")
        
        # اختبار تنسيق الرسالة
        formatted = message_manager.get_formatted_message(
            "welcome",
            username="أحمد"
        )
        assert formatted is not None
        print(f"  ✅ تم تنسيق الرسالة بنجاح")
        
        return True
    except Exception as e:
        print(f"  ❌ خطأ في MessageManager: {e}")
        return False


def test_notification_manager() -> bool:
    """اختبار NotificationManager."""
    print("\n🔔 اختبار NotificationManager...")
    
    try:
        from src.utils import notification_manager
        from src.utils.notification_manager import (
            NotificationType,
            NotificationLevel
        )
        
        # إنشاء إشعار
        notif = notification_manager.create_notification(
            notification_type=NotificationType.NEW_USER,
            level=NotificationLevel.MEDIUM,
            title="اختبار",
            message="رسالة اختبار"
        )
        print(f"  ✅ تم إنشاء إشعار: {notif.title}")
        
        # الحصول على الإحصائيات
        stats = notification_manager.get_notification_stats()
        assert stats["total_notifications"] >= 1
        print(f"  ✅ إحصائيات الإشعارات: {stats['total_notifications']} إشعار")
        
        return True
    except Exception as e:
        print(f"  ❌ خطأ في NotificationManager: {e}")
        return False


def test_advanced_stats_manager() -> bool:
    """اختبار AdvancedStatsManager."""
    print("\n📊 اختبار AdvancedStatsManager...")
    
    try:
        from src.utils import advanced_stats_manager
        
        # تسجيل أحداث
        advanced_stats_manager.record_command_usage("test")
        advanced_stats_manager.record_task_completed()
        print(f"  ✅ تم تسجيل الأحداث")
        
        # الحصول على الملخص اليومي
        daily = advanced_stats_manager.get_daily_summary()
        assert daily is not None
        print(f"  ✅ تم الحصول على الملخص اليومي")
        
        return True
    except Exception as e:
        print(f"  ❌ خطأ في AdvancedStatsManager: {e}")
        return False


def test_models() -> bool:
    """اختبار النماذج."""
    print("\n📦 اختبار النماذج...")
    
    try:
        from src.models import Task, TaskDifficulty, TaskFrequency
        from src.models.message import BotMessage, DEFAULT_MESSAGES
        from src.utils.notification_manager import (
            Notification, NotificationType, NotificationLevel
        )
        
        # اختبار Task
        task = Task(
            task_id=1,
            name="اختبار",
            description="وصف",
            reward_points=10,
            reward_xp=20,
            difficulty=TaskDifficulty.EASY,
            frequency=TaskFrequency.DAILY
        )
        print(f"  ✅ تم إنشاء نموذج Task")
        
        # اختبار BotMessage
        msg = BotMessage(
            message_id=1,
            name="test",
            content="محتوى اختبار",
            description="وصف",
            variables=["name"]
        )
        print(f"  ✅ تم إنشاء نموذج BotMessage")
        
        # اختبار Notification
        notif = Notification(
            notification_id=1,
            notification_type=NotificationType.NEW_USER,
            level=NotificationLevel.MEDIUM,
            title="اختبار",
            message="رسالة"
        )
        print(f"  ✅ تم إنشاء نموذج Notification")
        
        return True
    except Exception as e:
        print(f"  ❌ خطأ في النماذج: {e}")
        return False


def run_all_tests() -> bool:
    """تشغيل جميع الاختبارات."""
    print("=" * 50)
    print("🧪 اختبار التكامل - Phase 2")
    print("=" * 50)
    
    results = {
        "الاستيراد": test_imports(),
        "TaskManager": test_task_manager(),
        "MessageManager": test_message_manager(),
        "NotificationManager": test_notification_manager(),
        "AdvancedStatsManager": test_advanced_stats_manager(),
        "النماذج": test_models(),
    }
    
    print("\n" + "=" * 50)
    print("📋 النتائج:")
    print("=" * 50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n📊 الإجمالي: {passed}/{total} ✅")
    
    if passed == total:
        print("\n🎉 جميع الاختبارات نجحت!")
        return True
    else:
        print(f"\n⚠️ فشل {total - passed} اختبار(ات)")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
