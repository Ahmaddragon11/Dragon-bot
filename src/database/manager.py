# src/database/manager.py
import sqlite3
import datetime
from typing import Optional, List
from src.models.user import User
from src.core.config import DATABASE_FILE

def get_connection():
    """إنشاء وإرجاع اتصال بقاعدة البيانات."""
    return sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

def init_db():
    """تهيئة قاعدة البيانات وإنشاء جدول المستخدمين إذا لم يكن موجودًا."""
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
                join_date TIMESTAMP
            )
            """
        )
        conn.commit()

def _row_to_user(row: sqlite3.Row) -> Optional[User]:
    """تحويل صف من قاعدة البيانات إلى كائن User."""
    if not row:
        return None
    # تحويل الصف إلى قاموس ثم إلى كائن User
    data = dict(row)
    # التأكد من تحويل is_banned إلى bool
    if 'is_banned' in data:
        data['is_banned'] = bool(data['is_banned'])
    return User(**data)

def get_user(user_id: int) -> Optional[User]:
    """الحصول على مستخدم من قاعدة البيانات عن طريق المعرف الخاص به."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return _row_to_user(row)

def get_user_by_referral_code(code: str) -> Optional[User]:
    """البحث عن مستخدم عن طريق رمز الإحالة الخاص به."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE referral_code = ?", (code,))
        row = cursor.fetchone()
        return _row_to_user(row)

def save_user(user: User):
    """حفظ أو تحديث مستخدم في قاعدة البيانات."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO users (
                user_id, username, first_name, points, referral_code,
                referred_by, is_banned, join_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            ,
            (
                user.user_id, user.username, user.first_name, user.points,
                user.referral_code, user.referred_by, int(user.is_banned),
                user.join_date
            )
        )
        conn.commit()

def get_all_users() -> List[User]:
    """الحصول على جميع المستخدمين من قاعدة البيانات."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [_row_to_user(row) for row in rows]

def get_top_users_by_points(limit: int = 10) -> List[User]:
    """الحصول على أكثر المستخدمين نقاطًا."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY points DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [_row_to_user(row) for row in rows]

def get_total_users_count() -> int:
    """الحصول على العدد الإجمالي للمستخدمين."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(user_id) FROM users")
        result = cursor.fetchone()
        return result[0] if result else 0

def get_banned_users_count() -> int:
    """الحصول على عدد المستخدمين المحظورين."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(user_id) FROM users WHERE is_banned = 1")
        result = cursor.fetchone()
        return result[0] if result else 0

def get_referral_count(user_id: int) -> int:
    """الحصول على عدد الإحالات لمستخدم معين."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(user_id) FROM users WHERE referred_by = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

def get_top_users_by_referrals(limit: int = 10) -> List[dict]:
    """الحصول على أكثر المستخدمين إحالةً."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                u.user_id,
                u.first_name,
                (SELECT COUNT(r.user_id) FROM users r WHERE r.referred_by = u.user_id) as referral_count
            FROM
                users u
            ORDER BY
                referral_count DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

def find_user_by_username(username: str) -> Optional[User]:
    """البحث عن مستخدم عن طريق اسم المستخدم الخاص به (case-insensitive)."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # استخدام LOWER لضمان البحث غير الحساس لحالة الأحرف
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        row = cursor.fetchone()
        return _row_to_user(row)
