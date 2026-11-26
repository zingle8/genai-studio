# -*- coding: utf-8 -*-
"""共享 PostgreSQL 适配层
- 用 psycopg2 替换 sqlite3，保持 conn()/rows()/run()/one() 接口不变
- 自动把 SQL 中的 ? 占位符转成 psycopg2 的 %s（兼容现有大量 SQL，service 层无需逐个改）
- 注意：SQL 中的 %% 为字面百分号，转换时跳过
"""
import os
import re
import threading
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

DEFAULT_DSN = "host=localhost port=5433 dbname=genai_graph user=genai password=genai123"


def pg_dsn(dbname=None):
    """从环境变量取 DSN；未设置时用默认本地容器地址"""
    dsn = os.environ.get("PG_DSN")
    if dsn:
        return dsn
    host = os.environ.get("PG_HOST", "localhost")
    port = os.environ.get("PG_PORT", "5433")
    user = os.environ.get("PG_USER", "genai")
    pwd = os.environ.get("PG_PASSWORD", "genai123")
    db = dbname or os.environ.get("PG_DB", "genai_graph")
    return f"host={host} port={port} dbname={db} user={user} password={pwd}"


def to_pg(sql: str) -> str:
    """? 占位符 → %s；跳过字符串字面量与 %%"""
    out, i, n = [], 0, len(sql)
    in_s = in_d = False
    while i < n:
        ch = sql[i]
        if ch == "'" and not in_d:
            in_s = not in_s
            out.append(ch); i += 1
            continue
        if ch == '"' and not in_s:
            in_d = not in_d
            out.append(ch); i += 1
            continue
        if ch == '?' and not in_s and not in_d:
            out.append('%s')
        elif ch == '%' and i + 1 < n and sql[i + 1] == '%':
            out.append('%%'); i += 1
        else:
            out.append(ch)
        i += 1
    return ''.join(out)


class PGRow(RealDictCursor):
    """RealDictCursor 的 dict(r) 可直接用"""


@contextmanager
def connect(dsn):
    c = psycopg2.connect(dsn)
    c.cursor_factory = RealDictCursor
    try:
        yield c
    finally:
        c.close()


def rows(dsn, sql, args=()):
    with connect(dsn) as c:
        with c.cursor() as cur:
            cur.execute(to_pg(sql), args)
            return [dict(r) for r in cur.fetchall()]


def one(dsn, sql, args=()):
    with connect(dsn) as c:
        with c.cursor() as cur:
            cur.execute(to_pg(sql), args)
            r = cur.fetchone()
            return dict(r) if r else None


def run(dsn, sql, args=(), returning=False):
    """执行写操作；INSERT 自动追加 RETURNING id，兼容 sqlite 的 lastrowid 语义"""
    with connect(dsn) as c:
        with c.cursor() as cur:
            q = to_pg(sql)
            is_insert = q.lstrip().upper().startswith('INSERT')
            if is_insert and 'RETURNING' not in q.upper():
                q = q.rstrip().rstrip(';') + ' RETURNING id'
            if returning or is_insert:
                # RETURNING id 需要按列序号取值，临时用 None 覆盖 RealDictCursor
                old = c.cursor_factory
                c.cursor_factory = None
                cur2 = c.cursor()
                cur2.execute(q, args)
                r = cur2.fetchone()
                c.commit()
                c.cursor_factory = old
                return r[0] if r else None
            cur.execute(q, args)
            c.commit()
            return None


def execute_script(dsn, script):
    """把 executescript 的多语句拆开执行（psycopg2 不支持多语句一次执行）"""
    with connect(dsn) as c:
        with c.cursor() as cur:
            for stmt in script.split(';'):
                s = stmt.strip()
                if s:
                    cur.execute(s)
            c.commit()
