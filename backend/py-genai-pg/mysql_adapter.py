# -*- coding: utf-8 -*-
"""共享 MySQL 适配层
- 基于 pymysql，提供 conn()/rows()/run()/one() 统一接口
- 自动把 SQL 中的 ? 占位符转成 pymysql 的 %s
- run() 返回 lastrowid（INSERT 自增 id）
"""
import os
from contextlib import contextmanager

import pymysql
import pymysql.cursors


def mysql_dsn(dbname=None):
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = int(os.environ.get("MYSQL_PORT", "3306"))
    user = os.environ.get("MYSQL_USER", "root")
    pwd = os.environ.get("MYSQL_PASSWORD", "Root@123456")
    db = dbname or os.environ.get("MYSQL_DB", "genai_kb")
    return dict(host=host, port=port, user=user, password=pwd, database=db,
                charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor,
                autocommit=False)


def to_mysql(sql: str) -> str:
    """? 占位符 → %s；跳过字符串字面量与 %%"""
    out, i, n = [], 0, len(sql)
    in_s = in_d = False
    while i < n:
        ch = sql[i]
        if ch == "'" and not in_d:
            in_s = not in_s; out.append(ch); i += 1; continue
        if ch == '"' and not in_s:
            in_d = not in_d; out.append(ch); i += 1; continue
        if ch == '?' and not in_s and not in_d:
            out.append('%s')
        elif ch == '%' and i + 1 < n and sql[i + 1] == '%':
            out.append('%%'); i += 1
        else:
            out.append(ch)
        i += 1
    return ''.join(out)


@contextmanager
def connect(cfg):
    c = pymysql.connect(**cfg)
    try:
        yield c
    finally:
        c.close()


def rows(cfg, sql, args=()):
    with connect(cfg) as c:
        with c.cursor() as cur:
            cur.execute(to_mysql(sql), args)
            return [dict(r) for r in cur.fetchall()]


def one(cfg, sql, args=()):
    with connect(cfg) as c:
        with c.cursor() as cur:
            cur.execute(to_mysql(sql), args)
            r = cur.fetchone()
            return dict(r) if r else None


def run(cfg, sql, args=()):
    with connect(cfg) as c:
        with c.cursor() as cur:
            q = to_mysql(sql)
            cur.execute(q, args)
            c.commit()
            return cur.lastrowid


def execute_script(cfg, script):
    """把 executescript 的多语句拆开执行（pymysql 需分开）"""
    with connect(cfg) as c:
        with c.cursor() as cur:
            for stmt in script.split(';'):
                s = stmt.strip()
                if s:
                    cur.execute(s)
            c.commit()
