"""
STAKE MINES AI - Database Manager
Handles secure SQLite database transactions for user registration, profiles, and statistics
"""

import sqlite3
import datetime
from typing import Optional, Dict, Any, List
from config import DATABASE_NAME


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables with secure constraints"""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            language TEXT DEFAULT 'uz',
            mines_count INTEGER DEFAULT 1,
            signals_count INTEGER DEFAULT 0,
            verifications_count INTEGER DEFAULT 0,
            vip_level TEXT DEFAULT 'Boshlang''ich',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Signals history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mines_count INTEGER,
            safe_chance REAL,
            recommended_cells TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(telegram_id)
        )
    """)

    # Provably fair verifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            server_seed TEXT,
            client_seed TEXT,
            nonce INTEGER,
            mines_count INTEGER,
            mines_positions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(telegram_id)
        )
    """)

    conn.commit()
    conn.close()


def register_or_get_user(telegram_id: int, username: Optional[str], first_name: str) -> Dict[str, Any]:
    """Registers a new user if not exists, or returns current profile"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    if not user:
        cursor.execute("""
            INSERT INTO users (telegram_id, username, first_name, mines_count, signals_count, created_at)
            VALUES (?, ?, ?, 1, 0, ?)
        """, (telegram_id, username or "none", first_name, datetime.datetime.now()))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()

    user_dict = dict(user)
    conn.close()
    return user_dict


def update_mines_count(telegram_id: int, mines: int):
    mines = max(1, min(24, mines))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET mines_count = ? WHERE telegram_id = ?", (mines, telegram_id))
    conn.commit()
    conn.close()


def record_signal(telegram_id: int, mines_count: int, safe_chance: float, recommended_cells: List[int]):
    conn = get_connection()
    cursor = conn.cursor()
    cells_str = ",".join(map(str, recommended_cells))
    cursor.execute("""
        INSERT INTO signals_history (user_id, mines_count, safe_chance, recommended_cells)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, mines_count, safe_chance, cells_str))

    cursor.execute("""
        UPDATE users 
        SET signals_count = signals_count + 1 
        WHERE telegram_id = ?
    """, (telegram_id,))

    # Update VIP status based on signal count
    cursor.execute("SELECT signals_count FROM users WHERE telegram_id = ?", (telegram_id,))
    res = cursor.fetchone()
    if res:
        count = res[0]
        vip = "Boshlang'ich"
        if count >= 100: vip = "VIP Pro"
        elif count >= 50: vip = "Oltin"
        elif count >= 20: vip = "Kumush"
        elif count >= 5: vip = "Bronza"
        cursor.execute("UPDATE users SET vip_level = ? WHERE telegram_id = ?", (vip, telegram_id))

    conn.commit()
    conn.close()


def record_verification(telegram_id: int, server_seed: str, client_seed: str, nonce: int, mines_count: int, positions: List[int]):
    conn = get_connection()
    cursor = conn.cursor()
    pos_str = ",".join(map(str, positions))
    cursor.execute("""
        INSERT INTO verifications (user_id, server_seed, client_seed, nonce, mines_count, mines_positions)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (telegram_id, server_seed, client_seed, nonce, mines_count, pos_str))

    cursor.execute("""
        UPDATE users 
        SET verifications_count = verifications_count + 1 
        WHERE telegram_id = ?
    """, (telegram_id,))

    conn.commit()
    conn.close()


def get_user_stats(telegram_id: int) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {}

    cursor.execute("SELECT COUNT(*), AVG(mines_count), AVG(safe_chance) FROM signals_history WHERE user_id = ?", (telegram_id,))
    stats = cursor.fetchone()
    conn.close()

    return {
        "user": dict(user),
        "total_signals": stats[0] or 0,
        "avg_mines": round(stats[1] or 1, 1),
        "avg_safety": round(stats[2] or 96.0, 1)
    }
