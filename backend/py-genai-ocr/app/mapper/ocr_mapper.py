# -*- coding: utf-8 -*-
"""OCR 数据访问层（mapper）：SQLite tb_ocr_task 读写（迁移自 storage.py）"""
import sqlite3, os

from app.config.settings import settings


def conn():
    c = sqlite3.connect(settings.db_path)
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
        for ddl in ["ALTER TABLE tb_ocr_task ADD COLUMN prompt TEXT DEFAULT ''",
                    "ALTER TABLE tb_ocr_task ADD COLUMN image_path TEXT DEFAULT ''"]:
            try:
                c.execute(ddl)
                c.commit()
            except Exception:
                pass


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


def delete(tid: int):
    run("DELETE FROM tb_ocr_task WHERE id=?", (tid,))
