# -*- coding: utf-8 -*-
"""知识库服务存储层（SQLite：知识库 / 文档 / 分块）"""
import sqlite3, os

DB_PATH = os.environ.get("KB_DB", os.path.join(os.path.dirname(__file__), "..", "kb.db"))


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_kb(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_kb_doc(
          id INTEGER PRIMARY KEY AUTOINCREMENT, kb_id INTEGER NOT NULL,
          name TEXT NOT NULL, source TEXT DEFAULT 'upload', size INTEGER DEFAULT 0,
          chunk_size INTEGER DEFAULT 500, chunks INTEGER DEFAULT 0,
          status TEXT DEFAULT 'ready', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_kb_chunk(
          id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id INTEGER NOT NULL, kb_id INTEGER NOT NULL,
          idx INTEGER DEFAULT 0, content TEXT NOT NULL);
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


def split_text(text, size=500):
    """简单分块：按段落优先、超长按 size 硬切"""
    paras = [p.strip() for p in text.replace("\r\n", "\n").split("\n") if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        while len(p) > size:
            if buf:
                chunks.append(buf); buf = ""
            chunks.append(p[:size]); p = p[size:]
        if len(buf) + len(p) + 1 <= size:
            buf = (buf + "\n" + p) if buf else p
        else:
            if buf: chunks.append(buf)
            buf = p
    if buf: chunks.append(buf)
    return chunks or ([text[:size]] if text else [])


init_db()
