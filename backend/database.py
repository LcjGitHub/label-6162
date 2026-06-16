"""SQLite 数据库连接与初始化。"""

import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent / "data"
DB_PATH = DB_DIR / "envelope.db"


def get_connection() -> sqlite3.Connection:
    """
     * 获取 SQLite 连接，启用 Row 工厂便于字典访问。
     * @returns {sqlite3.Connection}
     """
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
     * 创建信封表（若不存在）。
     * @returns {None}
     """
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS envelopes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                year INTEGER NOT NULL,
                stamp_description TEXT NOT NULL,
                postmark_type TEXT NOT NULL,
                condition TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()
