"""
مدير قاعدة البيانات للبوت Dragon-bot.

يحتوي هذا الملف على جميع العمليات المتعلقة بالتفاعل مع قاعدة البيانات
بما في ذلك CRUD operations والاستعلامات المخصصة.
"""

import sqlite3
import datetime
import logging
from typing import Optional, List, Dict, Any
from src.models.user import User
from src.core.config import DATABASE_FILE
from src.utils.exceptions import DatabaseError

logger: logging.Logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    إنشاء واسترجاع اتصال جديد بقاعدة البيانات.
    
    Returns:
        sqlite3.Connection: كائن الاتصال بقاعدة البيانات
        
    Raises:
        DatabaseError: إذا فشل الاتصال بقاعدة البيانات
    """
    try:
        return sqlite3.connect(
            DATABASE_FILE,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
    except sqlite3.Error as e:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {e}")
        raise DatabaseError(f"فشل الاتصال بقاعدة البيانات: {e}") from e


def init_db() -> None:
    """
    تهيئة قاعدة البيانات وإنشاء الجداول اللازمة.
    
    ينشئ جدول users إذا لم يكن موجودًا، مع جميع الأعمدة المطلوبة.
    
    Raises:
        DatabaseError: إذا فشلت عملية التهيئة
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    points INTEGER DEFAULT 0,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    is_banned BOOLEAN DEFAULT 0,
                    join_date TIMESTAMP,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    rank TEXT DEFAULT 'مبتدئ'
                )
                """
            )
            
            # إنشاء فهارس لتحسين الأداء
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_referral_code ON users(referral_code)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_username ON users(username)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_points ON users(points)"
            )
            
            conn.commit()
            logger.info("✅ تم تهيئة قاعدة البيانات بنجاح")
    except sqlite3.Error as e:
        logger.error(f"❌ فشلت عملية تهيئة قاعدة البيانات: {e}")
        raise DatabaseError(f"فشلت عملية تهيئة قاعدة البيانات: {e}") from e


def _row_to_user(row: Optional[sqlite3.Row]) -> Optional[User]:
    """
    تحويل صف من قاعدة البيانات إلى كائن User.
    
    Args:
        row (Optional[sqlite3.Row]): الصف المراد تحويله
        
    Returns:
        Optional[User]: كائن User أو None إذا كان الصف فارغًا
    """
    if not row:
        return None
    
    data: Dict[str, Any] = dict(row)
    
    # تحويل الحقول إلى الأنواع الصحيحة
    if 'is_banned' in data:
        data['is_banned'] = bool(data['is_banned'])
    if 'level' not in data:
        data['level'] = 1
    if 'experience' not in data:
        data['experience'] = 0
    if 'rank' not in data:
        data['rank'] = 'مبتدئ'
    
    return User(**data)


def get_user(user_id: int) -> Optional[User]:
    """
    الحصول على مستخدم من قاعدة البيانات برقم معرّفه.
    
    Args:
        user_id (int): معرّف المستخدم الفريد
        
    Returns:
        Optional[User]: كائن المستخدم أو None إذا لم يتم العثور عليه
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return _row_to_user(row)
    except sqlite3.Error as e:
        logger.error(f"خطأ في استرجاع المستخدم {user_id}: {e}")
        raise DatabaseError(f"خطأ في استرجاع المستخدم: {e}") from e


def get_user_by_referral_code(code: str) -> Optional[User]:
    """
    البحث عن مستخدم باستخدام رمز الإحالة الخاص به.
    
    Args:
        code (str): رمز الإحالة
        
    Returns:
        Optional[User]: كائن المستخدم أو None إذا لم يتم العثور عليه
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE referral_code = ?", (code,))
            row = cursor.fetchone()
            return _row_to_user(row)
    except sqlite3.Error as e:
        logger.error(f"خطأ في البحث عن رمز الإحالة {code}: {e}")
        raise DatabaseError(f"خطأ في البحث عن رمز الإحالة: {e}") from e


def find_user_by_username(username: str) -> Optional[User]:
    """
    البحث عن مستخدم باستخدام اسم المستخدم (غير حساس لحالة الأحرف).
    
    Args:
        username (str): اسم المستخدم
        
    Returns:
        Optional[User]: كائن المستخدم أو None إذا لم يتم العثور عليه
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users WHERE LOWER(username) = LOWER(?)",
                (username,)
            )
            row = cursor.fetchone()
            return _row_to_user(row)
    except sqlite3.Error as e:
        logger.error(f"خطأ في البحث عن المستخدم {username}: {e}")
        raise DatabaseError(f"خطأ في البحث عن المستخدم: {e}") from e


def save_user(user: User) -> None:
    """
    حفظ أو تحديث مستخدم في قاعدة البيانات.
    
    إذا كان المستخدم موجودًا، سيتم تحديث بيانته.
    وإلا، سيتم إنشاء مستخدم جديد.
    
    Args:
        user (User): كائن المستخدم المراد حفظه
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO users (
                    user_id, username, first_name, points, referral_code,
                    referred_by, is_banned, join_date, level, experience, rank
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.user_id, user.username, user.first_name, user.points,
                    user.referral_code, user.referred_by, int(user.is_banned),
                    user.join_date, user.level, user.experience, user.rank
                )
            )
            conn.commit()
            logger.debug(f"تم حفظ المستخدم {user.user_id}")
    except sqlite3.Error as e:
        logger.error(f"خطأ في حفظ المستخدم {user.user_id}: {e}")
        raise DatabaseError(f"خطأ في حفظ المستخدم: {e}") from e


def delete_user(user_id: int) -> bool:
    """
    حذف مستخدم من قاعدة البيانات.
    
    Args:
        user_id (int): معرّف المستخدم المراد حذفه
        
    Returns:
        bool: True إذا تم الحذف، False إذا لم يتم العثور على المستخدم
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"تم حذف المستخدم {user_id}")
                return True
            return False
    except sqlite3.Error as e:
        logger.error(f"خطأ في حذف المستخدم {user_id}: {e}")
        raise DatabaseError(f"خطأ في حذف المستخدم: {e}") from e


def get_all_users() -> List[User]:
    """
    الحصول على جميع المستخدمين من قاعدة البيانات.
    
    Returns:
        List[User]: قائمة بجميع المستخدمين
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return [_row_to_user(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"خطأ في استرجاع جميع المستخدمين: {e}")
        raise DatabaseError(f"خطأ في استرجاع المستخدمين: {e}") from e


def get_top_users_by_points(limit: int = 10) -> List[User]:
    """
    الحصول على أكثر المستخدمين نقاطًا.
    
    Args:
        limit (int): عدد المستخدمين المراد إرجاعهم (افتراضي: 10)
        
    Returns:
        List[User]: قائمة بأكثر المستخدمين نقاطًا
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users ORDER BY points DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [_row_to_user(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"خطأ في استرجاع أعلى المستخدمين بالنقاط: {e}")
        raise DatabaseError(f"خطأ في استرجاع أعلى المستخدمين: {e}") from e


def get_top_users_by_level(limit: int = 10) -> List[User]:
    """
    الحصول على أكثر المستخدمين مستوى.
    
    Args:
        limit (int): عدد المستخدمين المراد إرجاعهم (افتراضي: 10)
        
    Returns:
        List[User]: قائمة بأكثر المستخدمين مستوى
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM users ORDER BY level DESC, experience DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [_row_to_user(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"خطأ في استرجاع أعلى المستخدمين بالمستوى: {e}")
        raise DatabaseError(f"خطأ في استرجاع أعلى المستخدمين: {e}") from e


def get_total_users_count() -> int:
    """
    الحصول على العدد الإجمالي للمستخدمين.
    
    Returns:
        int: عدد المستخدمين
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(user_id) FROM users")
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"خطأ في عد المستخدمين: {e}")
        raise DatabaseError(f"خطأ في عد المستخدمين: {e}") from e


def get_banned_users_count() -> int:
    """
    الحصول على عدد المستخدمين المحظورين.
    
    Returns:
        int: عدد المستخدمين المحظورين
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(user_id) FROM users WHERE is_banned = 1")
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"خطأ في عد المستخدمين المحظورين: {e}")
        raise DatabaseError(f"خطأ في عد المستخدمين المحظورين: {e}") from e


def get_active_users_count(days: int = 1) -> int:
    """
    الحصول على عدد المستخدمين النشطين في آخر عدد من الأيام.
    
    Args:
        days (int): عدد الأيام للتحقق من النشاط (افتراضي: 1)
        
    Returns:
        int: عدد المستخدمين النشطين
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # يمكن توسيع هذا إذا أضفنا جدول نشاط
            cursor.execute("SELECT COUNT(user_id) FROM users")
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"خطأ في عد المستخدمين النشطين: {e}")
        raise DatabaseError(f"خطأ في عد المستخدمين النشطين: {e}") from e


def get_referral_count(user_id: int) -> int:
    """
    الحصول على عدد الإحالات لمستخدم معين.
    
    Args:
        user_id (int): معرّف المستخدم
        
    Returns:
        int: عدد الإحالات
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(user_id) FROM users WHERE referred_by = ?",
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"خطأ في عد إحالات المستخدم {user_id}: {e}")
        raise DatabaseError(f"خطأ في عد الإحالات: {e}") from e


def get_top_users_by_referrals(limit: int = 10) -> List[Dict[str, Any]]:
    """
    الحصول على أكثر المستخدمين إحالةً.
    
    Args:
        limit (int): عدد المستخدمين المراد إرجاعهم (افتراضي: 10)
        
    Returns:
        List[Dict[str, Any]]: قائمة بقواميس تحتوي على بيانات المستخدم وعدد إحالاته
        
    Raises:
        DatabaseError: في حالة حدوث خطأ في قاعدة البيانات
    """
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.first_name,
                    u.username,
                    (SELECT COUNT(r.user_id) FROM users r WHERE r.referred_by = u.user_id) as referral_count
                FROM
                    users u
                ORDER BY
                    referral_count DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"خطأ في استرجاع أعلى المستخدمين بالإحالات: {e}")
        raise DatabaseError(f"خطأ في استرجاع أعلى المستخدمين: {e}") from e
