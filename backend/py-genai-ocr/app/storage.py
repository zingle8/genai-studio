# -*- coding: utf-8 -*-
"""OCR 服务存储层（SQLite：识别任务 / 结果）"""
import sqlite3, os

DB_PATH = os.environ.get("OCR_DB", os.path.join(os.path.dirname(__file__), "..", "ocr.db"))


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_ocr_task(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          engine TEXT DEFAULT 'auto', size INTEGER DEFAULT 0,
          status TEXT DEFAULT 'pending' CHECK(status IN ('pending','running','done','failed')),
          text TEXT DEFAULT '', error TEXT DEFAULT '', cost_ms INTEGER DEFAULT 0,
          created_at TEXT DEFAULT (datetime('now','localtime')));
        """)


def rows(sql, args=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def run(sql, args=()):
    with conn() as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid


def one(sql, args=()):
    with conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


init_db()
