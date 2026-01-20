"""
مدير نظام المهام اليومية والأسبوعية.

يتعامل مع إنشاء المهام وتتبع تقدم المستخدمين وإدارة المكافآت.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from src.models.task import Task, TaskFrequency, UserTaskProgress
from src.models.user import User
from src.utils.exceptions import TaskNotFound, InvalidOperation, DatabaseError

logger: logging.Logger = logging.getLogger(__name__)


class TaskManager:
    """
    مدير المهام - يتعامل مع عمليات المهام وتتبع التقدم.
    """
    
    # قاموس مؤقت للمهام (سيتم استبداله بقاعدة بيانات لاحقًا)
    _tasks: dict = {}
    _task_id_counter = 1
    _user_progress: dict = {}
    
    @classmethod
    def create_task(
        cls,
        name: str,
        description: str,
        reward_points: int = 10,
        reward_xp: int = 20,
        difficulty: str = "سهل",
        frequency: TaskFrequency = TaskFrequency.DAILY,
        metadata: Optional[dict] = None
    ) -> Task:
        """
        إنشاء مهمة جديدة.
        
        Args:
            name (str): اسم المهمة
            description (str): الوصف
            reward_points (int): النقاط المكتسبة
            reward_xp (int): الخبرة المكتسبة
            difficulty (str): مستوى الصعوبة
            frequency (TaskFrequency): التكرار
            metadata (Optional[dict]): بيانات إضافية
            
        Returns:
            Task: المهمة الجديدة
            
        Raises:
            InvalidOperation: إذا كانت البيانات غير صحيحة
        """
        if reward_points < 0 or reward_xp < 0:
            raise InvalidOperation("المكافآت لا يمكن أن تكون سالبة")
        
        if not name or not description:
            raise InvalidOperation("الاسم والوصف مطلوبان")
        
        task = Task(
            task_id=cls._task_id_counter,
            name=name,
            description=description,
            reward_points=reward_points,
            reward_xp=reward_xp,
            difficulty=difficulty,
            frequency=frequency,
            metadata=metadata or {}
        )
        
        cls._tasks[cls._task_id_counter] = task
        cls._task_id_counter += 1
        
        logger.info(f"تمت إضافة مهمة جديدة: {name} (ID: {task.task_id})")
        return task
    
    @classmethod
    def get_task(cls, task_id: int) -> Optional[Task]:
        """
        الحصول على مهمة برقمها.
        
        Args:
            task_id (int): معرّف المهمة
            
        Returns:
            Optional[Task]: كائن المهمة أو None
        """
        return cls._tasks.get(task_id)
    
    @classmethod
    def get_all_tasks(cls) -> List[Task]:
        """
        الحصول على جميع المهام المتاحة.
        
        Returns:
            List[Task]: قائمة المهام
        """
        return list(cls._tasks.values())
    
    @classmethod
    def get_active_tasks(cls) -> List[Task]:
        """
        الحصول على المهام المفعلة فقط.
        
        Returns:
            List[Task]: قائمة المهام المفعلة
        """
        return [t for t in cls._tasks.values() if t.is_active]
    
    @classmethod
    def get_available_tasks_for_user(cls, user_id: int) -> List[Task]:
        """
        الحصول على المهام المتاحة للمستخدم (غير المكتملة).
        
        Args:
            user_id (int): معرّف المستخدم
            
        Returns:
            List[Task]: قائمة المهام المتاحة
        """
        available_tasks = []
        
        for task in cls.get_active_tasks():
            progress = cls.get_user_task_progress(user_id, task.task_id)
            
            if not progress or not progress.is_completed:
                available_tasks.append(task)
        
        return available_tasks
    
    @classmethod
    def get_user_task_progress(cls, user_id: int, task_id: int) -> Optional[UserTaskProgress]:
        """
        الحصول على تقدم المستخدم في مهمة معينة.
        
        Args:
            user_id (int): معرّف المستخدم
            task_id (int): معرّف المهمة
            
        Returns:
            Optional[UserTaskProgress]: كائن التقدم أو None
        """
        key = f"{user_id}_{task_id}"
        return cls._user_progress.get(key)
    
    @classmethod
    def start_task(cls, user_id: int, task_id: int) -> bool:
        """
        بدء مهمة من قبل المستخدم.
        
        Args:
            user_id (int): معرّف المستخدم
            task_id (int): معرّف المهمة
            
        Returns:
            bool: هل تم البدء بنجاح؟
            
        Raises:
            TaskNotFound: إذا لم تجد المهمة
            InvalidOperation: إذا كانت المهمة معطلة
        """
        task = cls.get_task(task_id)
        
        if not task:
            raise TaskNotFound(f"المهمة برقم {task_id} غير موجودة")
        
        if not task.is_active:
            raise InvalidOperation("هذه المهمة معطلة حاليًا")
        
        key = f"{user_id}_{task_id}"
        
        # إنشاء سجل تقدم جديد إذا لم يكن موجودًا
        if key not in cls._user_progress:
            progress = UserTaskProgress(
                progress_id=len(cls._user_progress) + 1,
                user_id=user_id,
                task_id=task_id
            )
            cls._user_progress[key] = progress
        
        progress = cls._user_progress[key]
        progress.attempts += 1
        
        logger.info(f"المستخدم {user_id} بدأ المهمة {task_id}")
        return True
    
    @classmethod
    def complete_task(cls, user_id: int, task_id: int) -> Tuple[bool, int, int]:
        """
        إكمال مهمة من قبل المستخدم.
        
        Args:
            user_id (int): معرّف المستخدم
            task_id (int): معرّف المهمة
            
        Returns:
            Tuple[bool, int, int]: (هل تم بنجاح؟، النقاط، الخبرة)
            
        Raises:
            TaskNotFound: إذا لم تجد المهمة
        """
        task = cls.get_task(task_id)
        
        if not task:
            raise TaskNotFound(f"المهمة برقم {task_id} غير موجودة")
        
        key = f"{user_id}_{task_id}"
        
        # إنشاء سجل تقدم إذا لم يكن موجودًا
        if key not in cls._user_progress:
            progress = UserTaskProgress(
                progress_id=len(cls._user_progress) + 1,
                user_id=user_id,
                task_id=task_id
            )
            cls._user_progress[key] = progress
        
        progress = cls._user_progress[key]
        
        # التحقق من أن المهمة لم تكتمل بالفعل (إذا كانت يومية أو أسبوعية)
        if progress.is_completed:
            if task.frequency == TaskFrequency.ONE_TIME:
                raise InvalidOperation("تم إكمال هذه المهمة بالفعل")
            elif not cls._should_reset_task(progress, task.frequency):
                raise InvalidOperation("تم إكمال هذه المهمة اليوم بالفعل")
        
        progress.is_completed = True
        progress.completion_date = datetime.now()
        
        logger.info(f"المستخدم {user_id} أكمل المهمة {task_id}")
        
        return True, task.reward_points, task.reward_xp
    
    @classmethod
    def claim_task_reward(cls, user: User, task_id: int) -> Tuple[bool, str, int, int]:
        """
        المطالبة بمكافأة المهمة.
        
        Args:
            user (User): كائن المستخدم
            task_id (int): معرّف المهمة
            
        Returns:
            Tuple[bool, str, int, int]: (هل تم بنجاح؟، الرسالة، النقاط، الخبرة)
            
        Raises:
            TaskNotFound: إذا لم تجد المهمة
            InvalidOperation: إذا لم تكتمل المهمة
        """
        task = cls.get_task(task_id)
        
        if not task:
            raise TaskNotFound(f"المهمة برقم {task_id} غير موجودة")
        
        key = f"{user.user_id}_{task_id}"
        progress = cls._user_progress.get(key)
        
        if not progress or not progress.is_completed:
            raise InvalidOperation("يجب إكمال المهمة أولاً")
        
        # إضافة المكافآت
        user.points += task.reward_points
        user.experience += task.reward_xp
        
        # إعادة تعيين المهمة إذا كانت يومية أو أسبوعية
        if task.frequency != TaskFrequency.ONE_TIME:
            progress.is_completed = False
            progress.completion_date = None
            progress.last_reset = datetime.now()
        
        message = (
            f"✅ تم المطالبة بمكافأة المهمة: {task.name}\n"
            f"نقاط: +{task.reward_points}\n"
            f"خبرة: +{task.reward_xp} XP"
        )
        
        logger.info(
            f"المستخدم {user.user_id} طالب بمكافأة المهمة {task_id}"
        )
        
        return True, message, task.reward_points, task.reward_xp
    
    @classmethod
    def _should_reset_task(cls, progress: UserTaskProgress, frequency: TaskFrequency) -> bool:
        """
        التحقق من أن المهمة يجب إعادة تعيينها بناءً على التكرار.
        
        Args:
            progress (UserTaskProgress): كائن التقدم
            frequency (TaskFrequency): التكرار
            
        Returns:
            bool: هل يجب إعادة التعيين؟
        """
        now = datetime.now()
        last_reset = progress.last_reset
        
        if frequency == TaskFrequency.DAILY:
            # إذا كان اليوم مختلفًا عن يوم آخر إكمال
            return now.date() != last_reset.date()
        
        elif frequency == TaskFrequency.WEEKLY:
            # إذا كانت الأسبوع مختلفًا
            days_passed = (now - last_reset).days
            return days_passed >= 7
        
        elif frequency == TaskFrequency.MONTHLY:
            # إذا كان الشهر مختلفًا
            return (now.year, now.month) != (last_reset.year, last_reset.month)
        
        return False
    
    @classmethod
    def get_task_stats(cls) -> dict:
        """
        الحصول على إحصائيات المهام.
        
        Returns:
            dict: قاموس بالإحصائيات
        """
        total_tasks = len(cls._tasks)
        active_tasks = sum(1 for t in cls._tasks.values() if t.is_active)
        total_completions = sum(
            1 for p in cls._user_progress.values() if p.is_completed
        )
        
        return {
            "total_tasks": total_tasks,
            "active_tasks": active_tasks,
            "inactive_tasks": total_tasks - active_tasks,
            "total_completions": total_completions,
            "tasks_by_frequency": cls._get_tasks_by_frequency(),
        }
    
    @classmethod
    def _get_tasks_by_frequency(cls) -> dict:
        """
        الحصول على توزيع المهام حسب التكرار.
        
        Returns:
            dict: قاموس بتوزيع التكرارات
        """
        frequency_counts = {}
        for task in cls._tasks.values():
            freq = task.frequency.value
            frequency_counts[freq] = frequency_counts.get(freq, 0) + 1
        
        return frequency_counts


# إنشاء مثيل من مدير المهام
task_manager = TaskManager()
