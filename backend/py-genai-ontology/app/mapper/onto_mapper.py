
# -*- coding: utf-8 -*-
"""本体知识服务存储层（SQLite：本体空间/本体/类/关系规则/映射/数据源）

迁移自 app/storage.py；目录层级对齐 py-genai-rag-reranker 分层结构。
"""
import sqlite3, json, time, os

DB_PATH = os.environ.get("ONTO_DB", os.path.join(os.path.dirname(__file__), "..", "..", "onto.db"))


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_onto_space(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
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
        CREATE TABLE IF NOT EXISTS tb_onto_version(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL, version_no INTEGER NOT NULL,
          op TEXT NOT NULL, note TEXT DEFAULT '', snapshot TEXT DEFAULT '{}',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        """)
        # 本体归属空间（对齐知识库 space 模型）
        try:
            c.execute("ALTER TABLE tb_ontology ADD COLUMN space_id INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass


def migrate_ensure_space():
    """本体必须归属本体空间：保证至少一个空间存在，并把未归属的存量本体归入默认空间"""
    if not one("SELECT id FROM tb_onto_space LIMIT 1"):
        run("INSERT INTO tb_onto_space(name, description) VALUES('默认空间','系统自动创建')")
    d = one("SELECT id FROM tb_onto_space ORDER BY id LIMIT 1")
    run("UPDATE tb_ontology SET space_id=? WHERE space_id IS NULL OR space_id=0", (d["id"],))


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


# ===== 版本快照（对齐图谱模块 tb_graph_version） =====
def snapshot(oid):
    """本体全量快照：本体定义 + 类 + 关系规则 + 映射"""
    return {
        "ontology": one("SELECT * FROM tb_ontology WHERE id=?", (oid,)),
        "classes": rows("SELECT * FROM tb_onto_class WHERE ontology_id=? ORDER BY id", (oid,)),
        "rels": rows("SELECT * FROM tb_onto_rel WHERE ontology_id=? ORDER BY id", (oid,)),
        "mappings": rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=? ORDER BY id", (oid,)),
    }


def save_version(oid, op, note=""):
    """写操作后自动快照（version_no 自增）"""
    last = one("SELECT MAX(version_no) m FROM tb_onto_version WHERE ontology_id=?", (oid,))
    no = (last["m"] or 0) + 1
    run("INSERT INTO tb_onto_version(ontology_id, version_no, op, note, snapshot) VALUES(?,?,?,?,?)",
        (oid, no, op, note, json.dumps(snapshot(oid), ensure_ascii=False)))
    return no


init_db()
migrate_ensure_space()
