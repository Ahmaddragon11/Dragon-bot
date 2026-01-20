"""
نموذج المكافآت للبوت Dragon-bot.

يحتوي على فئة Reward التي تمثل مكافأة يمكن للمستخدم تبديل نقاطه بها.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum
import datetime


class RewardType(Enum):
    """أنواع المكافآت المختلفة."""
    
    COMMAND = "command"  # تنفيذ أمر خاص
    ROLE = "role"  # منح دور (رتبة خاصة)
    BADGE = "badge"  # شارة أو وسام
    FEATURE = "feature"  # تفعيل ميزة
    CUSTOM = "custom"  # مكافأة مخصصة


@dataclass
class Reward:
    """
    يمثل هذا الفئة مكافأة يمكن للمستخدم الحصول عليها.
    
    Attributes:
        reward_id (int): معرّف المكافأة الفريد
        name (str): اسم المكافأة
        description (str): وصف المكافأة
        cost (int): عدد النقاط المطلوبة للحصول على المكافأة
        reward_type (RewardType): نوع المكافأة
        is_active (bool): هل المكافأة مفعلة؟
        max_claims (Optional[int]): عدد المرات التي يمكن استخدامها (None للغير محدود)
        claim_count (int): عدد المرات التي تم استخدام المكافأة
        created_at (datetime.datetime): تاريخ إنشاء المكافأة
        updated_at (datetime.datetime): تاريخ آخر تحديث
        metadata (dict): بيانات إضافية مخصصة
    """
    
    reward_id: int
    """معرّف المكافأة الفريد"""
    
    name: str
    """اسم المكافأة"""
    
    description: str
    """وصف المكافأة"""
    
    cost: int
    """عدد النقاط المطلوبة"""
    
    reward_type: RewardType = RewardType.CUSTOM
    """نوع المكافأة"""
    
    is_active: bool = True
    """حالة المكافأة"""
    
    max_claims: Optional[int] = None
    """عدد المرات المسموح (None = غير محدود)"""
    
    claim_count: int = 0
    """عدد المرات المستخدمة"""
    
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ الإنشاء"""
    
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ التحديث"""
    
    metadata: dict = field(default_factory=dict)
    """بيانات إضافية مخصصة"""
    
    def is_available(self) -> bool:
        """
        التحقق من توفر المكافأة للاستخدام.
        
        Returns:
            bool: True إذا كانت المكافأة متاحة
        """
        if not self.is_active:
            return False
        
        if self.max_claims is None:
            return True
        
        return self.claim_count < self.max_claims
    
    def can_user_claim(self, user_points: int) -> bool:
        """
        التحقق من أن المستخدم يملك نقاطًا كافية وأن المكافأة متاحة.
        
        Args:
            user_points (int): نقاط المستخدم الحالية
            
        Returns:
            bool: True إذا كان المستخدم يستطيع الحصول على المكافأة
        """
        return self.is_available() and user_points >= self.cost
    
    def get_remaining_claims(self) -> Optional[int]:
        """
        الحصول على عدد المرات المتبقية لاستخدام المكافأة.
        
        Returns:
            Optional[int]: عدد المرات المتبقية أو None إذا كانت غير محدودة
        """
        if self.max_claims is None:
            return None
        
        return max(0, self.max_claims - self.claim_count)


@dataclass
class UserRewardClaim:
    """
    يمثل عملية حصول مستخدم على مكافأة.
    
    Attributes:
        claim_id (int): معرّف العملية الفريد
        user_id (int): معرّف المستخدم
        reward_id (int): معرّف المكافأة
        points_spent (int): عدد النقاط المستهلكة
        claimed_at (datetime.datetime): تاريخ الحصول على المكافأة
        status (str): حالة العملية (pending, completed, failed)
    """
    
    claim_id: int
    """معرّف العملية"""
    
    user_id: int
    """معرّف المستخدم"""
    
    reward_id: int
    """معرّف المكافأة"""
    
    points_spent: int
    """النقاط المستهلكة"""
    
    claimed_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    """تاريخ الحصول على المكافأة"""
    
    status: str = "completed"
    """حالة العملية"""
