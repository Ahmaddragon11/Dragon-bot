"""
نظام الاستثناءات المخصص للبوت Dragon-bot.

يحتوي هذا الملف على جميع الاستثناءات المخصصة المستخدمة في المشروع
لتوفير معالجة أخطاء شاملة وموحدة.
"""


class DragonBotException(Exception):
    """
    فئة استثناء أساسية لجميع استثناءات البوت.
    
    جميع الاستثناءات المخصصة الأخرى يجب أن ترث من هذه الفئة.
    """
    
    def __init__(self, message: str) -> None:
        """
        تهيئة الاستثناء.
        
        Args:
            message (str): رسالة الخطأ
        """
        super().__init__(message)
        self.message = message


class UserNotFound(DragonBotException):
    """استثناء يُرفع عندما لا يتم العثور على المستخدم."""
    pass


class UserAlreadyExists(DragonBotException):
    """استثناء يُرفع عندما يحاول تسجيل مستخدم موجود بالفعل."""
    pass


class UserBanned(DragonBotException):
    """استثناء يُرفع عندما يكون المستخدم محظور."""
    pass


class InvalidReferralCode(DragonBotException):
    """استثناء يُرفع عندما يكون كود الإحالة غير صحيح."""
    pass


class InsufficientPoints(DragonBotException):
    """استثناء يُرفع عندما لا يملك المستخدم نقاطًا كافية."""
    pass


class DatabaseError(DragonBotException):
    """استثناء يُرفع عند حدوث خطأ في قاعدة البيانات."""
    pass


class ConfigurationError(DragonBotException):
    """استثناء يُرفع عند وجود خطأ في التكوين."""
    pass


class RewardNotFound(DragonBotException):
    """استثناء يُرفع عندما لا يتم العثور على المكافأة."""
    pass


class TaskNotFound(DragonBotException):
    """استثناء يُرفع عندما لا يتم العثور على المهمة."""
    pass


class InvalidOperation(DragonBotException):
    """استثناء يُرفع عند محاولة إجراء عملية غير صحيحة."""
    pass


class PermissionDenied(DragonBotException):
    """استثناء يُرفع عندما لا يملك المستخدم الصلاحيات اللازمة."""
    pass
