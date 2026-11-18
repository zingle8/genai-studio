# -*- coding: utf-8 -*-
"""知识库服务存储层 v2
- 知识空间 tb_kb_space → 知识库 tb_kb（存储类型 es/pg/sqlite、库类型、切分方式、embedding/reranker 模型）
- 文档元数据存 SQLite；分块按 db_type 写入对应存储：
  * sqlite：内置 tb_kb_chunk
  * es：Elasticsearch 索引 kb_{id}（HTTP，支持认证）
  * pg：PostgreSQL 表 kb_{id}_chunks（psycopg2）
"""
import sqlite3, os, json, requests

from app.config.settings import settings

DB_PATH = settings.db_path


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_kb_space(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
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
        # v2 加列（已存在则忽略）
        for ddl in [
            "ALTER TABLE tb_kb ADD COLUMN space_id INTEGER DEFAULT 0",
            "ALTER TABLE tb_kb ADD COLUMN db_type TEXT DEFAULT 'sqlite'",
            "ALTER TABLE tb_kb ADD COLUMN db_config TEXT DEFAULT ''",
            "ALTER TABLE tb_kb ADD COLUMN kb_type TEXT DEFAULT 'doc'",
            "ALTER TABLE tb_kb ADD COLUMN chunk_mode TEXT DEFAULT 'paragraph'",
            "ALTER TABLE tb_kb ADD COLUMN chunk_len INTEGER DEFAULT 500",
            "ALTER TABLE tb_kb ADD COLUMN embedding_model TEXT DEFAULT ''",
            "ALTER TABLE tb_kb ADD COLUMN reranker_model TEXT DEFAULT ''",
        ]:
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


def jload(s, default=None):
    try:
        return json.loads(s or "") if s else (default or {})
    except Exception:
        return default or {}


# ===== 分块 =====
def split_text(text, mode="paragraph", size=500):
    """切分方式：paragraph 段落优先 / fixed 固定长度 / sentence 按句号切"""
    text = text.replace("\r\n", "\n")
    if mode == "fixed":
        return [text[i:i + size] for i in range(0, len(text), size) if text[i:i + size].strip()] or ([text[:size]] if text else [])
    if mode == "sentence":
        import re
        parts = [s.strip() for s in re.split(r"[。！？!?\n]", text) if s.strip()]
        chunks, buf = [], ""
        for p in parts:
            if len(buf) + len(p) + 1 <= size:
                buf = (buf + "。" + p) if buf else p
            else:
                if buf: chunks.append(buf)
                buf = p
        if buf: chunks.append(buf)
        return chunks or ([text[:size]] if text else [])
    # paragraph（默认）
    paras = [p.strip() for p in text.split("\n") if p.strip()]
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


# ===== ES 适配（HTTP，支持认证） =====
def es_cfg(kb):
    return jload(kb.get("db_config"), {})


def es_req(kb, method, path, body=None, params=None):
    cfg = es_cfg(kb)
    url = cfg.get("url", "http://localhost:9200").rstrip("/") + path
    auth = None
    if cfg.get("user"):
        auth = (cfg["user"], cfg.get("password", ""))
    kw = {"params": params, "auth": auth, "timeout": 10}
    if isinstance(body, str):
        kw["data"] = body.encode("utf-8")
        kw["headers"] = {"Content-Type": "application/x-ndjson"}
    else:
        kw["json"] = body
    r = requests.request(method, url, **kw)
    j = r.json()
    if r.status_code >= 400 and "error" in j:
        raise RuntimeError("ES: " + str(j["error"].get("reason", j["error"]))[:200])
    return j


def es_ensure_index(kb, kid):
    idx = "kb_%d" % kid
    try:
        es_req(kb, "PUT", f"/{idx}", {"mappings": {"properties": {
            "doc_id": {"type": "integer"}, "idx": {"type": "integer"},
            "doc": {"type": "keyword"}, "content": {"type": "text"}}}})
    except RuntimeError as e:
        if "already exists" not in str(e):
            raise
    return idx


def es_insert_chunks(kb, kid, doc_id, doc_name, chunks):
    idx = es_ensure_index(kb, kid)
    body = []
    for i, c in enumerate(chunks):
        body.append({"index": {"_index": idx}})
        body.append({"doc_id": doc_id, "idx": i, "doc": doc_name, "content": c})
    es_req(kb, "POST", "/_bulk?refresh=true", body="\n".join(json.dumps(x, ensure_ascii=False) for x in body) + "\n")


def es_search(kb, kid, q, top_k):
    idx = "kb_%d" % kid
    j = es_req(kb, "POST", f"/{idx}/_search",
               {"query": {"match": {"content": q}}, "size": top_k})
    hits = []
    for h in j["hits"]["hits"]:
        s = h["_source"]
        hits.append({"chunkId": s.get("idx", 0), "docId": s.get("doc_id"), "doc": s.get("doc"),
                     "idx": s.get("idx", 0), "score": round(h["_score"], 4), "content": s.get("content", "")})
    return hits


def es_delete_doc(kb, kid, doc_id):
    idx = "kb_%d" % kid
    es_req(kb, "POST", f"/{idx}/_delete_by_query?refresh=true",
           {"query": {"term": {"doc_id": doc_id}}})


def es_ping(cfg):
    try:
        auth = (cfg.get("user"), cfg.get("password", "")) if cfg.get("user") else None
        r = requests.get(cfg.get("url", "http://localhost:9200") + "/_cluster/health", auth=auth, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


# ===== PG 适配（psycopg2，可选依赖） =====
def pg_conn(kb):
    import psycopg2
    cfg = jload(kb.get("db_config"), {})
    return psycopg2.connect(host=cfg.get("host", "localhost"), port=cfg.get("port", 5432),
                            user=cfg.get("user", "postgres"), password=cfg.get("password", ""),
                            dbname=cfg.get("dbname", "postgres"))


def pg_ensure_table(kb, kid):
    with pg_conn(kb) as c:
        cur = c.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS kb_%d_chunks(
            id SERIAL PRIMARY KEY, doc_id INTEGER, idx INTEGER, doc TEXT, content TEXT)""" % kid)
        c.commit()


def pg_insert_chunks(kb, kid, doc_id, doc_name, chunks):
    pg_ensure_table(kb, kid)
    with pg_conn(kb) as c:
        cur = c.cursor()
        cur.executemany("INSERT INTO kb_%d_chunks(doc_id, idx, doc, content) VALUES(%%s,%%s,%%s,%%s)" % kid,
                        [(doc_id, i, doc_name, t) for i, t in enumerate(chunks)])
        c.commit()


def pg_search(kb, kid, q, top_k):
    pg_ensure_table(kb, kid)
    with pg_conn(kb) as c:
        cur = c.cursor()
        cur.execute("SELECT doc_id, idx, doc, content FROM kb_%d_chunks WHERE content ILIKE %%s LIMIT %%s" % kid,
                    ("%" + q + "%", top_k))
        return [{"chunkId": r[1], "docId": r[0], "doc": r[2], "idx": r[1], "score": 1, "content": r[3]}
                for r in cur.fetchall()]


def pg_delete_doc(kb, kid, doc_id):
    with pg_conn(kb) as c:
        c.cursor().execute("DELETE FROM kb_%d_chunks WHERE doc_id=%%s" % kid, (doc_id,))
        c.commit()


def pg_ping(cfg):
    try:
        with pg_conn({"db_config": json.dumps(cfg)}):
            return True
    except Exception:
        return False


def insert_chunks(kb, kid, doc_id, doc_name, chunks):
    t = kb.get("db_type", "sqlite")
    if t == "es":
        es_insert_chunks(kb, kid, doc_id, doc_name, chunks)
        return "es"
    if t == "pg":
        pg_insert_chunks(kb, kid, doc_id, doc_name, chunks)
        return "pg"
    with conn() as c:
        c.executemany("INSERT INTO tb_kb_chunk(doc_id, kb_id, idx, content) VALUES(?,?,?,?)",
                      [(doc_id, kid, i, t2) for i, t2 in enumerate(chunks)])
        c.commit()
    return "sqlite"


def search_chunks(kb, kid, q, top_k):
    t = kb.get("db_type", "sqlite")
    if t == "es":
        return es_search(kb, kid, q, top_k), "es"
    if t == "pg":
        return pg_search(kb, kid, q, top_k), "pg"
    hits = rows("SELECT id, doc_id, idx, content FROM tb_kb_chunk WHERE kb_id=? AND content LIKE ? LIMIT ?",
                (kid, "%" + q + "%", top_k))
    return [{"chunkId": h["id"], "docId": h["doc_id"], "doc": "", "idx": h["idx"], "score": 1, "content": h["content"]}
            for h in hits], "sqlite"


def delete_doc_chunks(kb, kid, doc_id):
    t = kb.get("db_type", "sqlite")
    if t == "es":
        es_delete_doc(kb, kid, doc_id)
    elif t == "pg":
        pg_delete_doc(kb, kid, doc_id)
    else:
        run("DELETE FROM tb_kb_chunk WHERE kb_id=? AND doc_id=?", (kid, doc_id))


init_db()
