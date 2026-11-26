# -*- coding: utf-8 -*-
"""知识库服务存储层 v3
- 知识空间 tb_kb_space → 知识库 tb_kb（存储类型 pg/es、库类型、切分方式、embedding/reranker 模型）
- 元数据存 MySQL（genai_kb）；分块按 db_type 写入对应存储：
  * pg：PostgreSQL 表 kb_{id}_chunks（psycopg2，pgvector 可选）
  * es：Elasticsearch 索引 kb_{id}（HTTP，支持认证）
"""
import os, sys, json, requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../py-genai-pg')))
from mysql_adapter import mysql_dsn, connect, rows as my_rows, one as my_one, run as my_run, execute_script

DSN = mysql_dsn('genai_kb')


def conn():
    import pymysql
    cfg = dict(DSN); cfg['cursorclass'] = pymysql.cursors.DictCursor
    return pymysql.connect(**cfg)


def init_db():
    execute_script(DSN, """
        CREATE TABLE IF NOT EXISTS tb_kb_space(
          id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(512) NOT NULL,
          description TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS tb_kb(
          id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(512) NOT NULL,
          description TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          space_id INT DEFAULT 0, db_type VARCHAR(32) DEFAULT 'pg',
          db_config TEXT, kb_type VARCHAR(64) DEFAULT 'doc',
          chunk_mode VARCHAR(64) DEFAULT 'paragraph', chunk_len INT DEFAULT 500,
          embedding_model VARCHAR(128) DEFAULT '', reranker_model VARCHAR(128) DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_kb_doc(
          id INT AUTO_INCREMENT PRIMARY KEY, kb_id INT NOT NULL,
          name VARCHAR(512) NOT NULL, source VARCHAR(64) DEFAULT 'upload', size INT DEFAULT 0,
          chunk_size INT DEFAULT 500, chunks INT DEFAULT 0,
          status VARCHAR(32) DEFAULT 'ready', created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS tb_kb_chunk(
          id INT AUTO_INCREMENT PRIMARY KEY, doc_id INT NOT NULL, kb_id INT NOT NULL,
          idx INT DEFAULT 0, content TEXT);
        """)


def migrate_ensure_space():
    """知识库必须归属空间：保证至少一个空间存在，并把未归属(space_id=0/NULL)的存量库归入默认空间"""
    if not one("SELECT id FROM tb_kb_space LIMIT 1"):
        run("INSERT INTO tb_kb_space(name, description) VALUES('默认空间','系统自动创建')")
    d = one("SELECT id FROM tb_kb_space ORDER BY id LIMIT 1")
    run("UPDATE tb_kb SET space_id=? WHERE space_id IS NULL OR space_id=0", (d["id"],))


def rows(sql, args=()):
    return my_rows(DSN, sql, args)


def run(sql, args=()):
    return my_run(DSN, sql, args)


def one(sql, args=()):
    return my_one(DSN, sql, args)


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


def _split_terms(q):
    """分词：空白/标点切分 + 中文长词滑窗双字（bigram）子词，解决无空格中文整句匹配问题"""
    import re
    base = [x for x in re.split(r"[\s，。,、;；？?！!]+", q) if x]
    terms = list(base)
    for w in base:
        if len(w) >= 2 and re.fullmatch(r"[\u4e00-\u9fff]+", w):
            terms += [w[i:i + 2] for i in range(len(w) - 1)]
    return terms or [q]


def pg_search(kb, kid, q, top_k):
    pg_ensure_table(kb, kid)
    terms = _split_terms(q)
    where = " OR ".join(["content ILIKE %s"] * len(terms))
    with pg_conn(kb) as c:
        cur = c.cursor()
        cur.execute(f"SELECT doc_id, idx, doc, content FROM kb_{kid}_chunks WHERE {where} LIMIT %s",
                    (*[f"%{t}%" for t in terms], max(top_k * 5, 20)))
        rows_ = cur.fetchall()
    rows_.sort(key=lambda r: -sum(1 for t in terms if t.lower() in (r[3] or "").lower()))
    return [{"chunkId": r[1], "docId": r[0], "doc": r[2], "idx": r[1],
             "score": sum(1 for t in terms if t.lower() in (r[3] or "").lower()), "content": r[3]}
            for r in rows_[:top_k]]


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
    t = kb.get("db_type", "pg")
    if t == "es":
        es_insert_chunks(kb, kid, doc_id, doc_name, chunks)
        return "es"
    if t in ("pg", "sqlite"):   # 存量 sqlite 库自动走 pg；新库默认 pg
        pg_insert_chunks(kb, kid, doc_id, doc_name, chunks)
        return "pg"
    with connect(DSN) as c:
        with c.cursor() as cur:
            cur.executemany("INSERT INTO tb_kb_chunk(doc_id,kb_id,idx,content) VALUES(%s,%s,%s,%s)",
                            [(doc_id, kid, i, t2) for i, t2 in enumerate(chunks)])
        c.commit()
    return "mysql"


def search_chunks(kb, kid, q, top_k):
    t = kb.get("db_type", "pg")
    if t == "es":
        return es_search(kb, kid, q, top_k), "es"
    if t in ("pg", "sqlite"):
        return pg_search(kb, kid, q, top_k), "pg"
    terms = _split_terms(q)
    where = " OR ".join(["content LIKE %s"] * len(terms))
    hits = rows(f"SELECT id, doc_id, idx, content FROM tb_kb_chunk WHERE kb_id=%s AND ({where}) LIMIT %s",
                (kid, *[f"%{t}%" for t in terms], max(top_k * 5, 20)))
    hits.sort(key=lambda h: -sum(1 for t in terms if t.lower() in (h["content"] or "").lower()))
    return [{"chunkId": h["id"], "docId": h["doc_id"], "doc": "", "idx": h["idx"],
             "score": sum(1 for t in terms if t.lower() in (h["content"] or "").lower()), "content": h["content"]}
            for h in hits[:top_k]], "mysql"


def all_chunks(kb, kid, limit=3000):
    """语义检索用：拉取知识库全部分块（三存储统一格式）"""
    t = kb.get("db_type", "pg")
    if t == "es":
        idx = "kb_%d" % kid
        j = es_req(kb, "POST", f"/{idx}/_search",
                   {"query": {"match_all": {}}, "size": limit,
                    "sort": [{"doc_id": "asc"}, {"idx": "asc"}]})
        return [{"chunkId": h["_source"].get("idx", 0), "docId": h["_source"].get("doc_id"),
                 "doc": h["_source"].get("doc", ""), "idx": h["_source"].get("idx", 0),
                 "content": h["_source"].get("content", "")}
                for h in j["hits"]["hits"]]
    if t == "pg":
        pg_ensure_table(kb, kid)
        with pg_conn(kb) as c:
            cur = c.cursor()
            cur.execute(f"SELECT doc_id, idx, doc, content FROM kb_{kid}_chunks LIMIT %s", (limit,))
            return [{"chunkId": r[1], "docId": r[0], "doc": r[2], "idx": r[1], "content": r[3]}
                    for r in cur.fetchall()]
    return [{"chunkId": h["id"], "docId": h["doc_id"], "doc": "", "idx": h["idx"], "content": h["content"]}
            for h in rows("SELECT id, doc_id, idx, content FROM tb_kb_chunk WHERE kb_id=%s LIMIT %s", (kid, limit))]


def delete_doc_chunks(kb, kid, doc_id):
    t = kb.get("db_type", "pg")
    if t == "es":
        es_delete_doc(kb, kid, doc_id)
    elif t in ("pg", "sqlite"):
        pg_delete_doc(kb, kid, doc_id)
    else:
        run("DELETE FROM tb_kb_chunk WHERE kb_id=%s AND doc_id=%s", (kid, doc_id))


init_db()
migrate_ensure_space()
