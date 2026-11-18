# -*- coding: utf-8 -*-
"""知识库服务（38106）：知识库 / 文档 / 分块 / 关键词检索"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.gateway_report import gateway_report
from app import storage

app = FastAPI(title="GenAI Studio - 知识库服务", version="0.1.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


gateway_report.init(settings)
gateway_report.install(app)


@app.get("/health")
async def health():
    return {"service": settings.service_id, "status": "ok"}


# ===== 知识库 =====
class KbIn(BaseModel):
    name: str
    description: str = ""


@app.get("/api/kb/list")
async def kb_list():
    kbs = storage.rows("SELECT * FROM tb_kb ORDER BY id DESC")
    for k in kbs:
        k["docCount"] = storage.one("SELECT COUNT(*) n FROM tb_kb_doc WHERE kb_id=?", (k["id"],))["n"]
        k["chunkCount"] = storage.one("SELECT COUNT(*) n FROM tb_kb_chunk WHERE kb_id=?", (k["id"],))["n"]
    return {"code": 0, "data": kbs}


@app.post("/api/kb")
async def kb_create(b: KbIn):
    if not b.name.strip():
        raise HTTPException(400, "name 不能为空")
    nid = storage.run("INSERT INTO tb_kb(name, description) VALUES(?,?)", (b.name.strip(), b.description))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_kb WHERE id=?", (nid,))}


@app.put("/api/kb/{kid}")
async def kb_update(kid: int, b: KbIn):
    if not storage.one("SELECT id FROM tb_kb WHERE id=?", (kid,)):
        raise HTTPException(404, "知识库不存在")
    storage.run("UPDATE tb_kb SET name=?, description=? WHERE id=?", (b.name.strip(), b.description, kid))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_kb WHERE id=?", (kid,))}


@app.delete("/api/kb/{kid}")
async def kb_delete(kid: int):
    storage.run("DELETE FROM tb_kb_chunk WHERE kb_id=?", (kid,))
    storage.run("DELETE FROM tb_kb_doc WHERE kb_id=?", (kid,))
    storage.run("DELETE FROM tb_kb WHERE id=?", (kid,))
    return {"code": 0, "data": "deleted"}


# ===== 文档 =====
@app.post("/api/kb/{kid}/docs")
async def doc_add(kid: int, name: str = Form(...), text: str = Form(""), file: Optional[UploadFile] = File(None)):
    if not storage.one("SELECT id FROM tb_kb WHERE id=?", (kid,)):
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
    chunks = storage.split_text(text)
    did = storage.run(
        "INSERT INTO tb_kb_doc(kb_id, name, source, size, chunks, status) VALUES(?,?,?,?,?, 'ready')",
        (kid, name, "upload", len(text), len(chunks)))
    for i, ch in enumerate(chunks):
        storage.run("INSERT INTO tb_kb_chunk(doc_id, kb_id, idx, content) VALUES(?,?,?,?)", (did, kid, i, ch))
    return {"code": 0, "data": {"id": did, "name": name, "chunks": len(chunks), "size": len(text)}}


@app.get("/api/kb/{kid}/docs")
async def doc_list(kid: int):
    return {"code": 0, "data": storage.rows("SELECT id, name, source, size, chunks, status, created_at FROM tb_kb_doc WHERE kb_id=? ORDER BY id DESC", (kid,))}


@app.get("/api/kb/{kid}/docs/{did}/chunks")
async def chunk_list(kid: int, did: int):
    return {"code": 0, "data": storage.rows("SELECT idx, content FROM tb_kb_chunk WHERE doc_id=? ORDER BY idx", (did,))}


@app.delete("/api/kb/{kid}/docs/{did}")
async def doc_delete(kid: int, did: int):
    storage.run("DELETE FROM tb_kb_chunk WHERE doc_id=?", (did,))
    storage.run("DELETE FROM tb_kb_doc WHERE id=? AND kb_id=?", (did, kid))
    return {"code": 0, "data": "deleted"}


# ===== 检索（关键词 + 简单打分：命中次数与完整词频） =====
@app.get("/api/kb/{kid}/search")
async def kb_search(kid: int, q: str, top_k: int = 5):
    if not q.strip():
        raise HTTPException(400, "q 不能为空")
    terms = [t for t in q.replace("，", " ").replace("。", " ").split() if t]
    if not terms:
        terms = [q.strip()]
    chunks = storage.rows("SELECT id, doc_id, idx, content FROM tb_kb_chunk WHERE kb_id=?", (kid,))
    scored = []
    for c in chunks:
        score = sum(c["content"].lower().count(t.lower()) for t in terms)
        if score > 0:
            doc = storage.one("SELECT name FROM tb_kb_doc WHERE id=?", (c["doc_id"],))
            scored.append({"chunkId": c["id"], "docId": c["doc_id"], "doc": doc["name"] if doc else "",
                           "idx": c["idx"], "score": score, "content": c["content"][:400]})
    scored.sort(key=lambda x: -x["score"])
    return {"code": 0, "data": scored[:top_k], "total": len(scored)}


@app.on_event("shutdown")
async def shutdown() -> None:
    gateway_report.stop()
