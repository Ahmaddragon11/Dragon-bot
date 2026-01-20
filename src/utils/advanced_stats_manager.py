"""
نظام الإحصائيات المتقدمة للمشرفين.

يوفر تحليلات شاملة عن أنشطة المستخدمين والبوت.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class UserActivityStats:
    """إحصائيات نشاط المستخدم."""
    
    total_users: int = 0
    """إجمالي المستخدمين"""
    
    active_today: int = 0
    """النشطون اليوم"""
    
    active_this_week: int = 0
    """النشطون هذا الأسبوع"""
    
    active_this_month: int = 0
    """النشطون هذا الشهر"""
    
    new_users_today: int = 0
    """المستخدمون الجدد اليوم"""
    
    new_users_this_week: int = 0
    """المستخدمون الجدد هذا الأسبوع"""
    
    new_users_this_month: int = 0
    """المستخدمون الجدد هذا الشهر"""
    
    total_points_earned: int = 0
    """إجمالي النقاط المكتسبة"""
    
    average_points_per_user: float = 0.0
    """متوسط النقاط لكل مستخدم"""
    
    total_referrals: int = 0
    """إجمالي الإحالات"""
    
    average_referrals_per_user: float = 0.0
    """متوسط الإحالات لكل مستخدم"""


@dataclass
class FeatureUsageStats:
    """إحصائيات استخدام الميزات."""
    
    commands_used: Dict[str, int] = field(default_factory=dict)
    """الأوامر المستخدمة وعددها"""
    
    most_used_command: Optional[Tuple[str, int]] = None
    """الأمر الأكثر استخداماً"""
    
    rewards_claimed: int = 0
    """المكافآت المطالب بها"""
    
    tasks_completed: int = 0
    """المهام المكتملة"""
    
    tasks_abandoned: int = 0
    """المهام المهجورة"""
    
    levels_reached: int = 0
    """الأشخاص الذين وصلوا لمستوى جديد"""
    
    referral_clicks: int = 0
    """عدد نقرات الإحالة"""


@dataclass
class SystemHealthStats:
    """إحصائيات صحة النظام."""
    
    total_errors: int = 0
    """إجمالي الأخطاء"""
    
    errors_today: int = 0
    """الأخطاء اليوم"""
    
    banned_users: int = 0
    """عدد المستخدمين المحظورين"""
    
    database_size_mb: float = 0.0
    """حجم قاعدة البيانات بالميغابايت"""
    
    last_backup: Optional[datetime] = None
    """آخر نسخة احتياطية"""
    
    system_uptime_hours: float = 0.0
    """وقت تشغيل النظام بالساعات"""


class AdvancedStatsManager:
    """
    مدير الإحصائيات المتقدمة.
    
    يتعامل مع جمع وتحليل البيانات الشاملة عن النظام والمستخدمين.
    """
    
    def __init__(self):
        """تهيئة مدير الإحصائيات."""
        self._user_activity_stats = UserActivityStats()
        self._feature_usage_stats = FeatureUsageStats()
        self._system_health_stats = SystemHealthStats()
        self._last_update = datetime.now()
        self._command_history: Dict[str, int] = {}
        self._daily_stats_cache: Dict[str, dict] = {}
    
    def record_command_usage(self, command: str) -> None:
        """
        تسجيل استخدام أمر.
        
        Args:
            command (str): اسم الأمر
        """
        self._command_history[command] = self._command_history.get(command, 0) + 1
        self._feature_usage_stats.commands_used[command] = (
            self._feature_usage_stats.commands_used.get(command, 0) + 1
        )
        
        # تحديث الأمر الأكثر استخداماً
        most_used = max(
            self._feature_usage_stats.commands_used.items(),
            key=lambda x: x[1],
            default=None
        )
        self._feature_usage_stats.most_used_command = most_used
        
        logger.debug(f"تم تسجيل استخدام الأمر: {command}")
    
    def record_reward_claimed(self, reward_value: int) -> None:
        """
        تسجيل مكافأة مطالب بها.
        
        Args:
            reward_value (int): قيمة المكافأة
        """
        self._feature_usage_stats.rewards_claimed += 1
        logger.debug(f"تم تسجيل مكافأة: {reward_value}")
    
    def record_task_completed(self) -> None:
        """تسجيل مهمة مكتملة."""
        self._feature_usage_stats.tasks_completed += 1
        logger.debug("تم تسجيل مهمة مكتملة")
    
    def record_task_abandoned(self) -> None:
        """تسجيل مهمة مهجورة."""
        self._feature_usage_stats.tasks_abandoned += 1
        logger.debug("تم تسجيل مهمة مهجورة")
    
    def record_level_up(self) -> None:
        """تسجيل ارتقاء مستوى."""
        self._feature_usage_stats.levels_reached += 1
        logger.debug("تم تسجيل ارتقاء مستوى")
    
    def record_referral_click(self) -> None:
        """تسجيل نقرة إحالة."""
        self._feature_usage_stats.referral_clicks += 1
        logger.debug("تم تسجيل نقرة إحالة")
    
    def record_error(self, error_type: str) -> None:
        """
        تسجيل خطأ.
        
        Args:
            error_type (str): نوع الخطأ
        """
        self._system_health_stats.total_errors += 1
        self._system_health_stats.errors_today += 1
        logger.warning(f"تم تسجيل خطأ: {error_type}")
    
    def update_user_activity_stats(self, stats: dict) -> None:
        """
        تحديث إحصائيات نشاط المستخدمين.
        
        Args:
            stats (dict): قاموس يحتوي على الإحصائيات المحدثة
        """
        for key, value in stats.items():
            if hasattr(self._user_activity_stats, key):
                setattr(self._user_activity_stats, key, value)
        
        self._last_update = datetime.now()
        logger.info("تم تحديث إحصائيات نشاط المستخدمين")
    
    def update_system_health_stats(self, stats: dict) -> None:
        """
        تحديث إحصائيات صحة النظام.
        
        Args:
            stats (dict): قاموس يحتوي على الإحصائيات المحدثة
        """
        for key, value in stats.items():
            if hasattr(self._system_health_stats, key):
                setattr(self._system_health_stats, key, value)
        
        logger.info("تم تحديث إحصائيات صحة النظام")
    
    def get_daily_summary(self) -> dict:
        """
        الحصول على ملخص اليومي.
        
        Returns:
            dict: قاموس يحتوي على ملخص الإحصائيات اليومية
        """
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "active_users": self._user_activity_stats.active_today,
            "new_users": self._user_activity_stats.new_users_today,
            "rewards_claimed": self._feature_usage_stats.rewards_claimed,
            "tasks_completed": self._feature_usage_stats.tasks_completed,
            "errors": self._system_health_stats.errors_today,
            "top_command": self._feature_usage_stats.most_used_command[0] 
                if self._feature_usage_stats.most_used_command else "N/A",
        }
    
    def get_weekly_summary(self) -> dict:
        """
        الحصول على ملخص أسبوعي.
        
        Returns:
            dict: قاموس يحتوي على ملخص الإحصائيات الأسبوعية
        """
        return {
            "week_active_users": self._user_activity_stats.active_this_week,
            "new_users_this_week": self._user_activity_stats.new_users_this_week,
            "total_points_earned": self._user_activity_stats.total_points_earned,
            "referral_clicks": self._feature_usage_stats.referral_clicks,
            "tasks_completed": self._feature_usage_stats.tasks_completed,
            "levels_reached": self._feature_usage_stats.levels_reached,
        }
    
    def get_monthly_summary(self) -> dict:
        """
        الحصول على ملخص شهري.
        
        Returns:
            dict: قاموس يحتوي على ملخص الإحصائيات الشهرية
        """
        avg_engagement = (
            self._user_activity_stats.active_this_month / max(1, self._user_activity_stats.total_users)
        ) * 100
        
        return {
            "total_users": self._user_activity_stats.total_users,
            "monthly_active_users": self._user_activity_stats.active_this_month,
            "new_users_this_month": self._user_activity_stats.new_users_this_month,
            "engagement_rate": f"{avg_engagement:.1f}%",
            "total_referrals": self._user_activity_stats.total_referrals,
            "rewards_claimed": self._feature_usage_stats.rewards_claimed,
            "tasks_completed": self._feature_usage_stats.tasks_completed,
        }
    
    def get_feature_usage_report(self) -> str:
        """
        الحصول على تقرير استخدام الميزات.
        
        Returns:
            str: التقرير المنسق
        """
        report = "📊 **تقرير استخدام الميزات**\n\n"
        
        # الأوامر
        if self._feature_usage_stats.commands_used:
            report += "🔧 **الأوامر المستخدمة:**\n"
            sorted_commands = sorted(
                self._feature_usage_stats.commands_used.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for cmd, count in sorted_commands:
                report += f"  • {cmd}: {count} مرة\n"
        
        report += f"\n💎 **المكافآت المطالب بها:** {self._feature_usage_stats.rewards_claimed}\n"
        report += f"✅ **المهام المكتملة:** {self._feature_usage_stats.tasks_completed}\n"
        report += f"⬆️ **ارتقاء المستويات:** {self._feature_usage_stats.levels_reached}\n"
        report += f"🔗 **نقرات الإحالة:** {self._feature_usage_stats.referral_clicks}\n"
        
        return report
    
    def get_health_report(self) -> str:
        """
        الحصول على تقرير صحة النظام.
        
        Returns:
            str: التقرير المنسق
        """
        report = "🏥 **تقرير صحة النظام**\n\n"
        
        status = "✅ جيد" if self._system_health_stats.errors_today < 5 else "⚠️ تحذير"
        report += f"{status}\n\n"
        
        report += f"❌ **الأخطاء اليوم:** {self._system_health_stats.errors_today}\n"
        report += f"🚫 **إجمالي الأخطاء:** {self._system_health_stats.total_errors}\n"
        report += f"🔒 **المستخدمون المحظورون:** {self._system_health_stats.banned_users}\n"
        
        if self._system_health_stats.database_size_mb:
            report += f"💾 **حجم قاعدة البيانات:** {self._system_health_stats.database_size_mb:.2f} MB\n"
        
        if self._system_health_stats.system_uptime_hours:
            days = int(self._system_health_stats.system_uptime_hours / 24)
            hours = int(self._system_health_stats.system_uptime_hours % 24)
            report += f"⏱️ **وقت التشغيل:** {days} يوم و {hours} ساعة\n"
        
        return report
    
    def get_complete_stats_report(self) -> str:
        """
        الحصول على تقرير إحصائيات شامل.
        
        Returns:
            str: التقرير المنسق
        """
        report = "📈 **التقرير الإحصائي الشامل**\n\n"
        report += "=" * 40 + "\n\n"
        
        # الملخص اليومي
        daily = self.get_daily_summary()
        report += "📅 **الملخص اليومي:**\n"
        report += f"  • المستخدمون النشطون: {daily['active_users']}\n"
        report += f"  • مستخدمون جدد: {daily['new_users']}\n"
        report += f"  • المكافآت المطالب بها: {daily['rewards_claimed']}\n\n"
        
        # الملخص الأسبوعي
        weekly = self.get_weekly_summary()
        report += "📊 **الملخص الأسبوعي:**\n"
        report += f"  • النقاط المكتسبة: {weekly['total_points_earned']}\n"
        report += f"  • نقرات الإحالة: {weekly['referral_clicks']}\n\n"
        
        # الملخص الشهري
        monthly = self.get_monthly_summary()
        report += "📈 **الملخص الشهري:**\n"
        report += f"  • إجمالي المستخدمين: {monthly['total_users']}\n"
        report += f"  • معدل التفاعل: {monthly['engagement_rate']}\n\n"
        
        # تقارير إضافية
        report += self.get_feature_usage_report()
        report += "\n" + self.get_health_report()
        
        return report
    
    def reset_daily_stats(self) -> None:
        """إعادة تعيين الإحصائيات اليومية."""
        self._user_activity_stats.active_today = 0
        self._user_activity_stats.new_users_today = 0
        self._system_health_stats.errors_today = 0
        logger.info("تم إعادة تعيين الإحصائيات اليومية")


# إنشاء مثيل من مدير الإحصائيات
advanced_stats_manager = AdvancedStatsManager()
