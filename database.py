# database.py
import sqlite3
from config import DATABASE_FILE
from models import User

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            points INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            is_banned BOOLEAN DEFAULT 0,
            restricted_features TEXT DEFAULT ''
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Optional[User]:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(
            user_id=row[0],
            username=row[1],
            first_name=row[2],
            points=row[3],
            referral_code=row[4],
            referred_by=row[5],
            is_banned=bool(row[6]),
            restricted_features=row[7].split(',') if row[7] else []
        )
    return None

def save_user(user: User):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, first_name, points, referral_code, referred_by, is_banned, restricted_features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user.user_id,
        user.username,
        user.first_name,
        user.points,
        user.referral_code,
        user.referred_by,
        user.is_banned,
        ','.join(user.restricted_features)
    ))
    conn.commit()
    conn.close()

def get_all_users() -> list[User]:
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    conn.close()
    return [User(
        user_id=row[0],
        username=row[1],
        first_name=row[2],
        points=row[3],
        referral_code=row[4],
        referred_by=row[5],
        is_banned=bool(row[6]),
        restricted_features=row[7].split(',') if row[7] else []
    ) for row in rows]