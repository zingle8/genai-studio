# -*- coding: utf-8 -*-
"""本体知识服务存储层（SQLite：本体/类/关系规则/映射/数据源）"""
import sqlite3, json, time, os

DB_PATH = os.environ.get("ONTO_DB", os.path.join(os.path.dirname(__file__), "..", "onto.db"))


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_ontology(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, scope TEXT DEFAULT 'domain',
          namespace TEXT DEFAULT '', authority TEXT DEFAULT 'normal', version TEXT DEFAULT 'v1',
          status TEXT DEFAULT 'active', comment TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_onto_class(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          name TEXT NOT NULL, parent_name TEXT DEFAULT '', comment TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_onto_rel(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          name TEXT NOT NULL, subj_class TEXT NOT NULL, obj_class TEXT NOT NULL,
          cardinality TEXT DEFAULT 'many' CHECK(cardinality IN ('one','many')),
          nullable INTEGER DEFAULT 1, inherits_from TEXT DEFAULT '', comment TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_onto_mapping(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          onto_type TEXT NOT NULL, physical_type TEXT NOT NULL, kind TEXT DEFAULT 'node' CHECK(kind IN ('node','edge')));
        CREATE TABLE IF NOT EXISTS tb_data_source(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type TEXT DEFAULT 'builtin-demo',
          config TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
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


def exec_many(sql_list):
    with conn() as c:
        for s, a in sql_list:
            c.execute(s, a)
        c.commit()


init_db()
