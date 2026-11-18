# -*- coding: utf-8 -*-
"""知识图谱服务存储层（SQLite：节点 / 关系边）"""
import sqlite3, os, json

DB_PATH = os.environ.get("GRAPH_DB", os.path.join(os.path.dirname(__file__), "..", "graph.db"))


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_graph_node(
          id INTEGER PRIMARY KEY AUTOINCREMENT, label TEXT NOT NULL,
          name TEXT NOT NULL, props TEXT DEFAULT '',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_graph_edge(
          id INTEGER PRIMARY KEY AUTOINCREMENT, source_id INTEGER NOT NULL,
          target_id INTEGER NOT NULL, rel_type TEXT NOT NULL,
          props TEXT DEFAULT '',
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


def seed_demo():
    """内置示例：公司组织数据（与本体平台 builtin-demo 同源）"""
    if one("SELECT id FROM tb_graph_node LIMIT 1"):
        return
    nodes = [
        ("公司", "GenAI 科技"), ("部门", "研发部"), ("部门", "市场部"), ("部门", "财务部"),
        ("员工", "张三"), ("员工", "李四"), ("项目", "Studio 平台"), ("项目", "RAG 系统"),
    ]
    ids = {}
    for label, name in nodes:
        ids[name] = run("INSERT INTO tb_graph_node(label, name) VALUES(?,?)", (label, name))
    edges = [
        ("张三", "研发部", "works_in"), ("李四", "市场部", "works_in"),
        ("研发部", "GenAI 科技", "belongs_to"), ("市场部", "GenAI 科技", "belongs_to"),
        ("财务部", "GenAI 科技", "belongs_to"),
        ("张三", "Studio 平台", "join_project"), ("张三", "RAG 系统", "join_project"),
        ("李四", "Studio 平台", "join_project"),
    ]
    for s, t, rel in edges:
        run("INSERT INTO tb_graph_edge(source_id, target_id, rel_type) VALUES(?,?,?)",
            (ids[s], ids[t], rel))


init_db()
seed_demo()
