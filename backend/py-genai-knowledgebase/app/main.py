# -*- coding: utf-8 -*-
"""知识库服务 v2（38126）：知识空间 / 知识库（存储 es|pg|内置 + 类型 + 切分 + embedding/reranker）/ 文档 / 检索路由"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.gateway_report import gateway_report
from app import storage

app = FastAPI(title="GenAI Studio - 知识库服务", version="0.2.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

gateway_report.init(settings)
gateway_report.install(app)


@app.get("/health")
async def health():
    return {"service": settings.service_id, "status": "ok"}


# ===== 选项与连通性 =====
@app.get("/api/kb/options")
async def kb_options():
    return {"code": 0, "data": {
        "dbTypes": [
            {"value": "sqlite", "label": "内置存储（SQLite）"},
            {"value": "es", "label": "Elasticsearch"},
            {"value": "pg", "label": "PostgreSQL"}],
        "kbTypes": [
            {"value": "golden_answer", "label": "Golden Answer（标准答案库）"},
            {"value": "qa", "label": "QA 问答对"},
            {"value": "doc", "label": "文档知识"},
            {"value": "faq", "label": "FAQ"}],
        "chunkModes": [
            {"value": "paragraph", "label": "按段落"},
            {"value": "sentence", "label": "按句子"},
            {"value": "fixed", "label": "固定长度"}],
        "embeddingModels": ["bge-m3", "text-embedding-ada-002", "nomic-embed-text", "bge-large-zh"],
        "rerankerModels": ["bge-reranker-v2-m3", "bge-reranker-large", "（无）"]
    }}


class PingIn(BaseModel):
    db_type: str
    db_config: str = ""


@app.post("/api/kb/ping")
async def kb_ping(b: PingIn):
    cfg = storage.jload(b.db_config, {})
    if b.db_type == "es":
        ok = storage.es_ping(cfg)
        return {"code": 0 if ok else 1, "data": {"ok": ok}, "message": "ES 连接成功" if ok else "ES 连接失败（检查地址/凭据）"}
    if b.db_type == "pg":
        ok = storage.pg_ping(cfg)
        return {"code": 0 if ok else 1, "data": {"ok": ok}, "message": "PG 连接成功" if ok else "PG 连接失败（检查地址/凭据/库名）"}
    return {"code": 0, "data": {"ok": True}, "message": "内置存储无需连接"}


# ===== 知识空间 =====
class SpaceIn(BaseModel):
    name: str
    description: str = ""


@app.get("/api/kb/spaces")
async def space_list():
    ss = storage.rows("SELECT * FROM tb_kb_space ORDER BY id")
    for s in ss:
        s["kbCount"] = storage.one("SELECT COUNT(*) n FROM tb_kb WHERE space_id=?", (s["id"],))["n"]
    return {"code": 0, "data": ss}


@app.post("/api/kb/spaces")
async def space_create(b: SpaceIn):
    if not b.name.strip():
        raise HTTPException(400, "空间名不能为空")
    sid = storage.run("INSERT INTO tb_kb_space(name, description) VALUES(?,?)", (b.name.strip(), b.description))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_kb_space WHERE id=?", (sid,))}


@app.delete("/api/kb/spaces/{sid}")
async def space_delete(sid: int):
    if storage.one("SELECT id FROM tb_kb WHERE space_id=?", (sid,)):
        raise HTTPException(400, "空间下还有知识库，先删除")
    storage.run("DELETE FROM tb_kb_space WHERE id=?", (sid,))
    return {"code": 0, "data": "deleted"}


# ===== 知识库 =====
class KbIn(BaseModel):
    name: str
    description: str = ""
    space_id: int = 0
    db_type: str = "sqlite"
    db_config: str = ""              # ES: {"url","user","password"} / PG: {"host","port","user","password","dbname"}
    kb_type: str = "doc"             # golden_answer | qa | doc | faq
    chunk_mode: str = "paragraph"    # paragraph | sentence | fixed
    chunk_len: int = 500
    embedding_model: str = ""
    reranker_model: str = ""


@app.get("/api/kb/list")
async def kb_list(space_id: int = 0):
    where, args = "", []
    if space_id:
        where, args = "WHERE space_id=?", [space_id]
    kbs = storage.rows(f"SELECT * FROM tb_kb {where} ORDER BY id DESC", args)
    for k in kbs:
        k["docCount"] = storage.one("SELECT COUNT(*) n FROM tb_kb_doc WHERE kb_id=?", (k["id"],))["n"]
        k["spaceName"] = (storage.one("SELECT name FROM tb_kb_space WHERE id=?", (k.get("space_id", 0),)) or {}).get("name", "")
        if k.get("db_type") == "es":
            k["dbOk"] = storage.es_ping(storage.es_cfg(k))
        elif k.get("db_type") == "pg":
            k["dbOk"] = storage.pg_ping(storage.jload(k.get("db_config"), {}))
    return {"code": 0, "data": kbs}


@app.post("/api/kb")
async def kb_create(b: KbIn):
    if not b.name.strip():
        raise HTTPException(400, "name 不能为空")
    if b.db_type == "es" and not storage.es_ping(storage.jload(b.db_config, {})):
        raise HTTPException(400, "ES 连接失败，请检查地址/凭据")
    if b.db_type == "pg" and not storage.pg_ping(storage.jload(b.db_config, {})):
        raise HTTPException(400, "PG 连接失败，请检查地址/凭据/库名")
    nid = storage.run(
        "INSERT INTO tb_kb(name, description, space_id, db_type, db_config, kb_type, chunk_mode, chunk_len, embedding_model, reranker_model) "
        "VALUES(?,?,?,?,?,?,?,?,?,?)",
        (b.name.strip(), b.description, b.space_id, b.db_type, b.db_config, b.kb_type,
         b.chunk_mode, b.chunk_len, b.embedding_model, b.reranker_model))
    if b.db_type == "es":
        try:
            storage.es_ensure_index(storage.one("SELECT * FROM tb_kb WHERE id=?", (nid,)), nid)
        except Exception:
            pass
    return {"code": 0, "data": storage.one("SELECT * FROM tb_kb WHERE id=?", (nid,))}


@app.put("/api/kb/{kid}")
async def kb_update(kid: int, b: KbIn):
    k = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
    if not k:
        raise HTTPException(404, "知识库不存在")
    storage.run(
        "UPDATE tb_kb SET name=?, description=?, space_id=?, db_type=?, db_config=?, kb_type=?, chunk_mode=?, chunk_len=?, embedding_model=?, reranker_model=? WHERE id=?",
        (b.name.strip(), b.description, b.space_id, b.db_type, b.db_config, b.kb_type,
         b.chunk_mode, b.chunk_len, b.embedding_model, b.reranker_model, kid))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))}


@app.delete("/api/kb/{kid}")
async def kb_delete(kid: int):
    k = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
    if k:
        storage.run("DELETE FROM tb_kb_chunk WHERE kb_id=?", (kid,))
        storage.run("DELETE FROM tb_kb_doc WHERE kb_id=?", (kid,))
        storage.run("DELETE FROM tb_kb WHERE id=?", (kid,))
        if k.get("db_type") == "es":
            try:
                storage.es_req(k, "DELETE", "/kb_%d" % kid)
            except Exception:
                pass
    return {"code": 0, "data": "deleted"}


# ===== 文档 =====
@app.post("/api/kb/{kid}/docs")
async def doc_add(kid: int, name: str = Form(...), text: str = Form(""), file: Optional[UploadFile] = File(None)):
    kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
    if not kb:
        raise HTTPException(404, "知识库不存在")
    if file is not None:
        raw = await file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="ignore")
        name = file.filename or name
    if not text.strip():
        raise HTTPException(400, "文档内容为空")
    chunks = storage.split_text(text, kb.get("chunk_mode") or "paragraph", kb.get("chunk_len") or 500)
    did = storage.run(
        "INSERT INTO tb_kb_doc(kb_id, name, source, size, chunks, status) VALUES(?,?,?,?,?, 'ready')",
        (kid, name, "upload", len(text), len(chunks)))
    try:
        backend = storage.insert_chunks(kb, kid, did, name, chunks)
    except Exception as e:
        storage.run("DELETE FROM tb_kb_doc WHERE id=?", (did,))
        raise HTTPException(400, f"分块写入 {backend if 'backend' in dir() else kb.get('db_type')} 失败：{e}")
    return {"code": 0, "data": {"id": did, "name": name, "chunks": len(chunks), "size": len(text), "backend": kb.get("db_type")}}


@app.get("/api/kb/{kid}/docs")
async def doc_list(kid: int):
    return {"code": 0, "data": storage.rows("SELECT id, name, source, size, chunks, status, created_at FROM tb_kb_doc WHERE kb_id=? ORDER BY id DESC", (kid,))}


@app.get("/api/kb/{kid}/docs/{did}/chunks")
async def chunk_list(kid: int, did: int):
    kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
    t = kb.get("db_type", "sqlite") if kb else "sqlite"
    if t == "es":
        j = storage.es_req(kb, "POST", "/kb_%d/_search" % kid,
                           {"query": {"term": {"doc_id": did}}, "size": 200, "sort": [{"idx": "asc"}]})
        return {"code": 0, "data": [{"idx": h["_source"]["idx"], "content": h["_source"]["content"]}
                                    for h in j["hits"]["hits"]]}
    if t == "pg":
        with storage.pg_conn(kb) as c:
            cur = c.cursor()
            cur.execute("SELECT idx, content FROM kb_%d_chunks WHERE doc_id=%%s ORDER BY idx" % kid, (did,))
            return {"code": 0, "data": [{"idx": r[0], "content": r[1]} for r in cur.fetchall()]}
    return {"code": 0, "data": storage.rows("SELECT idx, content FROM tb_kb_chunk WHERE doc_id=? ORDER BY idx", (did,))}


@app.delete("/api/kb/{kid}/docs/{did}")
async def doc_delete(kid: int, did: int):
    kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
    if kb:
        storage.delete_doc_chunks(kb, kid, did)
    storage.run("DELETE FROM tb_kb_doc WHERE id=? AND kb_id=?", (did, kid))
    return {"code": 0, "data": "deleted"}


# ===== 检索（按存储类型路由：es 全文 / pg ILIKE / 内置关键词打分） =====
@app.get("/api/kb/{kid}/search")
async def kb_search(kid: int, q: str, top_k: int = 5):
    if not q.strip():
        raise HTTPException(400, "q 不能为空")
    kb = storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))
    if not kb:
        raise HTTPException(404, "知识库不存在")
    t = kb.get("db_type", "sqlite")
    if t in ("es", "pg"):
        try:
            hits, backend = storage.search_chunks(kb, kid, q, top_k)
        except Exception as e:
            raise HTTPException(400, f"{t} 检索失败：{e}")
        return {"code": 0, "data": hits, "total": len(hits), "backend": backend}
    # 内置：多词关键词打分
    terms = [x for x in q.replace("，", " ").replace("。", " ").split() if x] or [q.strip()]
    chunks = storage.rows("SELECT id, doc_id, idx, content FROM tb_kb_chunk WHERE kb_id=?", (kid,))
    scored = []
    for c in chunks:
        score = sum(c["content"].lower().count(x.lower()) for x in terms)
        if score > 0:
            doc = storage.one("SELECT name FROM tb_kb_doc WHERE id=?", (c["doc_id"],))
            scored.append({"chunkId": c["id"], "docId": c["doc_id"], "doc": doc["name"] if doc else "",
                           "idx": c["idx"], "score": score, "content": c["content"][:400]})
    scored.sort(key=lambda x: -x["score"])
    return {"code": 0, "data": scored[:top_k], "total": len(scored), "backend": "sqlite"}


@app.on_event("shutdown")
async def shutdown() -> None:
    gateway_report.stop()
