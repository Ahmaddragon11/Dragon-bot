"""
نموذج المهام للبوت Dragon-bot.

يحتوي على فئة Task التي تمثل مهام يومية أو أسبوعية للمستخدمين.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import datetime


class TaskDifficulty(Enum):
    """مستويات صعوبة المهام."""
    
    EASY = "سهل"
    MEDIUM = "متوسط"
    HARD = "صعب"
    EXTREME = "صعب جداً"


class TaskFrequency(Enum):
    """تكرار المهام."""
    
    DAILY = "يومي"
    WEEKLY = "أسبوعي"
    MONTHLY = "شهري"
    ONE_TIME = "مرة واحدة"


@dataclass
class Task:
    """
    يمثل هذه الفئة مهمة يمكن للمستخدم إكمالها للحصول على مكافآت.
    
    Attributes:
        task_id (int): معرّف المهمة الفريد
        name (str): اسم المهمة
        description (str): وصف المهمة
        reward_points (int): النقاط المكتسبة عند إكمال المهمة
        reward_xp (int): نقاط الخبرة المكتسبة عند إكمال المهمة
        difficulty (TaskDifficulty): مستوى الصعوبة
        frequency (TaskFrequency): تكرار المهمة
        is_active (bool): هل المهمة مفعلة؟
        created_at (datetime.datetime): تاريخ الإنشاء
        updated_at (datetime.datetime): تاريخ التحديث
        metadata (dict): بيانات إضافية مخصصة
    """
    
    task_id: int
    """معرّف المهمة الفريد"""
    
    name: str
    """اسم المهمة"""
    
    description: str
    """وصف المهمة"""
    
    reward_points: int = 10
    """النقاط المكتسبة"""
    
    reward_xp: int = 20
    """نقاط الخبرة المكتسبة"""
    
    difficulty: TaskDifficulty = TaskDifficulty.EASY
    """مستوى الصعوبة"""
    
    frequency: TaskFrequency = TaskFrequency.DAILY
    """التكرار"""
    
    is_active: bool = True
    """حالة المهمة"""
    
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ الإنشاء"""
    
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ التحديث"""
    
    metadata: dict = field(default_factory=dict)
    """بيانات إضافية"""


@dataclass
class UserTaskProgress:
    """
    يمثل تقدم المستخدم في مهمة معينة.
    
    Attributes:
        progress_id (int): معرّف السجل الفريد
        user_id (int): معرّف المستخدم
        task_id (int): معرّف المهمة
        is_completed (bool): هل تم إكمال المهمة؟
        completion_date (Optional[datetime.datetime]): تاريخ الإكمال
        last_reset (datetime.datetime): تاريخ آخر إعادة تعيين
        attempts (int): عدد محاولات الإكمال
    """
    
    progress_id: int
    """معرّف السجل"""
    
    user_id: int
    """معرّف المستخدم"""
    
    task_id: int
    """معرّف المهمة"""
    
    is_completed: bool = False
    """حالة الإكمال"""
    
    completion_date: Optional[datetime.datetime] = None
    """تاريخ الإكمال"""
    
    last_reset: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ آخر إعادة تعيين"""
    
    attempts: int = 0
    """عدد المحاولات"""
    
    def can_claim_reward(self) -> bool:
        """
        التحقق من أن المستخدم يستطيع المطالبة بالمكافأة.
        
        Returns:
            bool: True إذا تم إكمال المهمة ولم يتم المطالبة بالمكافأة بعد
        """
        return self.is_completed and self.completion_date is not None
