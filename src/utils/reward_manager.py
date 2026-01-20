"""
وحدة إدارة المكافآت والتبادل.

تحتوي على وظائف لإدارة المكافآت وتبديل النقاط والحصول على المكافآت.
"""

import logging
from typing import Optional, List, Tuple
from src.models.reward import Reward, RewardType, UserRewardClaim
from src.models.user import User
from src.utils.exceptions import (
    InsufficientPoints,
    RewardNotFound,
    InvalidOperation,
    DatabaseError
)

logger: logging.Logger = logging.getLogger(__name__)


class RewardManager:
    """
    مدير المكافآت - يتعامل مع عمليات المكافآت والتبادل.
    """
    
    # قاموس مؤقت للمكافآت (سيتم استبداله بقاعدة بيانات لاحقًا)
    _rewards: dict = {}
    _reward_id_counter = 1
    
    @classmethod
    def add_reward(
        cls,
        name: str,
        description: str,
        cost: int,
        reward_type: RewardType = RewardType.CUSTOM,
        max_claims: Optional[int] = None,
        metadata: Optional[dict] = None
    ) -> Reward:
        """
        إضافة مكافأة جديدة.
        
        Args:
            name (str): اسم المكافأة
            description (str): الوصف
            cost (int): التكلفة بالنقاط
            reward_type (RewardType): نوع المكافأة
            max_claims (Optional[int]): عدد المرات المسموح (None = غير محدود)
            metadata (Optional[dict]): بيانات إضافية
            
        Returns:
            Reward: كائن المكافأة الجديدة
            
        Raises:
            InvalidOperation: إذا كانت البيانات غير صحيحة
        """
        if cost < 0:
            raise InvalidOperation("تكلفة المكافأة لا يمكن أن تكون سالبة")
        
        if not name or not description:
            raise InvalidOperation("اسم والوصف مطلوبان")
        
        reward = Reward(
            reward_id=cls._reward_id_counter,
            name=name,
            description=description,
            cost=cost,
            reward_type=reward_type,
            max_claims=max_claims,
            metadata=metadata or {}
        )
        
        cls._rewards[cls._reward_id_counter] = reward
        cls._reward_id_counter += 1
        
        logger.info(f"تمت إضافة مكافأة جديدة: {name} (ID: {reward.reward_id})")
        return reward
    
    @classmethod
    def get_reward(cls, reward_id: int) -> Optional[Reward]:
        """
        الحصول على مكافأة برقمها.
        
        Args:
            reward_id (int): معرّف المكافأة
            
        Returns:
            Optional[Reward]: كائن المكافأة أو None
        """
        return cls._rewards.get(reward_id)
    
    @classmethod
    def get_all_rewards(cls) -> List[Reward]:
        """
        الحصول على جميع المكافآت المتاحة.
        
        Returns:
            List[Reward]: قائمة المكافآت
        """
        return list(cls._rewards.values())
    
    @classmethod
    def get_available_rewards(cls, user_points: int) -> List[Reward]:
        """
        الحصول على المكافآت المتاحة للمستخدم بناءً على نقاطه.
        
        Args:
            user_points (int): نقاط المستخدم
            
        Returns:
            List[Reward]: قائمة المكافآت المتاحة
        """
        return [
            r for r in cls._rewards.values()
            if r.can_user_claim(user_points)
        ]
    
    @classmethod
    def claim_reward(
        cls,
        user: User,
        reward_id: int
    ) -> Tuple[bool, str]:
        """
        محاولة الحصول على مكافأة.
        
        Args:
            user (User): كائن المستخدم
            reward_id (int): معرّف المكافأة
            
        Returns:
            Tuple[bool, str]: (هل تم بنجاح؟، الرسالة)
            
        Raises:
            RewardNotFound: إذا لم تجد المكافأة
            InsufficientPoints: إذا لم تكن النقاط كافية
            InvalidOperation: إذا كانت المكافأة غير متاحة
        """
        reward = cls.get_reward(reward_id)
        
        if not reward:
            raise RewardNotFound(f"المكافأة برقم {reward_id} غير موجودة")
        
        if not reward.is_active:
            raise InvalidOperation("هذه المكافأة معطلة حاليًا")
        
        if not reward.is_available():
            raise InvalidOperation(
                f"المكافأة غير متاحة. عدد المرات المتبقية: {reward.get_remaining_claims()}"
            )
        
        if user.points < reward.cost:
            raise InsufficientPoints(
                f"نقاطك ({user.points}) غير كافية. تحتاج إلى {reward.cost} نقطة"
            )
        
        # خصم النقاط
        user.points -= reward.cost
        reward.claim_count += 1
        
        logger.info(
            f"المستخدم {user.user_id} حصل على المكافأة: {reward.name} "
            f"(تكلفة: {reward.cost} نقطة)"
        )
        
        return True, f"✅ تم الحصول على المكافأة: {reward.name}!"
    
    @classmethod
    def update_reward(cls, reward_id: int, **kwargs) -> bool:
        """
        تحديث بيانات المكافأة.
        
        Args:
            reward_id (int): معرّف المكافأة
            **kwargs: الحقول المراد تحديثها
            
        Returns:
            bool: هل تم التحديث بنجاح؟
        """
        reward = cls.get_reward(reward_id)
        
        if not reward:
            raise RewardNotFound(f"المكافأة برقم {reward_id} غير موجودة")
        
        for key, value in kwargs.items():
            if hasattr(reward, key):
                setattr(reward, key, value)
        
        logger.info(f"تم تحديث المكافأة: {reward.name}")
        return True
    
    @classmethod
    def deactivate_reward(cls, reward_id: int) -> bool:
        """
        تعطيل مكافأة.
        
        Args:
            reward_id (int): معرّف المكافأة
            
        Returns:
            bool: هل تم بنجاح؟
        """
        reward = cls.get_reward(reward_id)
        
        if not reward:
            raise RewardNotFound(f"المكافأة برقم {reward_id} غير موجودة")
        
        reward.is_active = False
        logger.info(f"تم تعطيل المكافأة: {reward.name}")
        return True
    
    @classmethod
    def get_reward_stats(cls) -> dict:
        """
        الحصول على إحصائيات المكافآت.
        
        Returns:
            dict: قاموس بالإحصائيات
        """
        total_rewards = len(cls._rewards)
        active_rewards = sum(1 for r in cls._rewards.values() if r.is_active)
        total_claims = sum(r.claim_count for r in cls._rewards.values())
        
        return {
            "total_rewards": total_rewards,
            "active_rewards": active_rewards,
            "inactive_rewards": total_rewards - active_rewards,
            "total_claims": total_claims,
            "rewards_by_type": cls._get_rewards_by_type(),
        }
    
    @classmethod
    def _get_rewards_by_type(cls) -> dict:
        """
        الحصول على توزيع المكافآت حسب النوع.
        
        Returns:
            dict: قاموس بتوزيع الأنواع
        """
        type_counts = {}
        for reward in cls._rewards.values():
            reward_type = reward.reward_type.value
            type_counts[reward_type] = type_counts.get(reward_type, 0) + 1
        
        return type_counts


# إنشاء مثيل من مدير المكافآت
reward_manager = RewardManager()