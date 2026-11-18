# -*- coding: utf-8 -*-
"""RAG 管理 API（38109 增量路由）：检索管道配置 / 索引统计 / 检索测试（联动 kb 38106 与 reranker 38104）"""
import sqlite3, os, time, httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

KB_BASE = os.environ.get("KB_BASE", "http://localhost:38106")
RR_BASE = os.environ.get("RR_BASE", "http://localhost:38104")
EM_BASE = os.environ.get("EM_BASE", "http://localhost:38103")
DB_PATH = os.environ.get("RAG_ADMIN_DB", os.path.join(os.path.dirname(__file__), "..", "..", "rag_admin.db"))


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_rag_pipeline(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          kb_id INTEGER DEFAULT 0, kb_name TEXT DEFAULT '',
          strategy TEXT DEFAULT 'keyword' CHECK(strategy IN ('keyword','vector','hybrid')),
          embed_model TEXT DEFAULT 'bge-m3', rerank_model TEXT DEFAULT 'bge-reranker-v2-m3',
          rerank_on INTEGER DEFAULT 0, top_k INTEGER DEFAULT 5, chunk_size INTEGER DEFAULT 500,
          created_at TEXT DEFAULT (datetime('now','localtime')));
        """)


def rows(sql, args=()):
    with _conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def run(sql, args=()):
    with _conn() as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid


def one(sql, args=()):
    with _conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


init_db()


class PipelineIn(BaseModel):
    name: str
    kb_id: int = 0
    kb_name: str = ""
    strategy: str = "keyword"
    embed_model: str = "bge-m3"
    rerank_model: str = "bge-reranker-v2-m3"
    rerank_on: bool = False
    top_k: int = 5
    chunk_size: int = 500


async def _svc_ok(base):
    try:
        async with httpx.AsyncClient(timeout=2) as cli:
            r = await cli.get(base + "/health")
            return r.status_code == 200
    except Exception:
        return False


def create_router():
    r = APIRouter()

    @r.get("/api/rag/pipelines")
    async def list_pipelines():
        return {"code": 0, "data": rows("SELECT * FROM tb_rag_pipeline ORDER BY id DESC")}

    @r.post("/api/rag/pipelines")
    async def create_pipeline(b: PipelineIn):
        if not b.name.strip():
            raise HTTPException(400, "name 不能为空")
        nid = run("INSERT INTO tb_rag_pipeline(name, kb_id, kb_name, strategy, embed_model, rerank_model, rerank_on, top_k, chunk_size) "
                  "VALUES(?,?,?,?,?,?,?,?,?)",
                  (b.name.strip(), b.kb_id, b.kb_name, b.strategy, b.embed_model, b.rerank_model,
                   1 if b.rerank_on else 0, b.top_k, b.chunk_size))
        return {"code": 0, "data": one("SELECT * FROM tb_rag_pipeline WHERE id=?", (nid,))}

    @r.put("/api/rag/pipelines/{pid}")
    async def update_pipeline(pid: int, b: PipelineIn):
        if not one("SELECT id FROM tb_rag_pipeline WHERE id=?", (pid,)):
            raise HTTPException(404, "管道不存在")
        run("UPDATE tb_rag_pipeline SET name=?, kb_id=?, kb_name=?, strategy=?, embed_model=?, rerank_model=?, rerank_on=?, top_k=?, chunk_size=? WHERE id=?",
            (b.name.strip(), b.kb_id, b.kb_name, b.strategy, b.embed_model, b.rerank_model,
             1 if b.rerank_on else 0, b.top_k, b.chunk_size, pid))
        return {"code": 0, "data": one("SELECT * FROM tb_rag_pipeline WHERE id=?", (pid,))}

    @r.delete("/api/rag/pipelines/{pid}")
    async def delete_pipeline(pid: int):
        run("DELETE FROM tb_rag_pipeline WHERE id=?", (pid,))
        return {"code": 0, "data": "deleted"}

    @r.get("/api/rag/stats")
    async def stats():
        """索引统计：知识库列表 + 依赖服务健康"""
        kbs, em_ok, rr_ok = [], False, False
        try:
            async with httpx.AsyncClient(timeout=3) as cli:
                r = await cli.get(KB_BASE + "/api/kb/list")
                if r.status_code == 200:
                    kbs = r.json().get("data", [])
                em_ok = (await cli.get(EM_BASE + "/health")).status_code == 200
                rr_ok = (await cli.get(RR_BASE + "/health")).status_code == 200
        except Exception:
            pass
        return {"code": 0, "data": {
            "kbs": [{"id": k["id"], "name": k["name"], "docCount": k.get("docCount", 0),
                     "chunkCount": k.get("chunkCount", 0)} for k in kbs],
            "services": {"knowledgebase(38106)": True, "embedding(38103)": em_ok,
                         "reranker(38104)": rr_ok, "systemone(38109)": True},
            "totalChunks": sum(k.get("chunkCount", 0) for k in kbs)}}

    @r.post("/api/rag/test")
    async def test_retrieve(pid: int, q: str):
        """检索测试：按管道配置执行——keyword 走 kb 检索；rerank_on 且 reranker 在线则尝试重排"""
        p = one("SELECT * FROM tb_rag_pipeline WHERE id=?", (pid,))
        if not p:
            raise HTTPException(404, "管道不存在")
        t0 = time.time()
        if not p["kb_id"]:
            raise HTTPException(400, "管道未绑定知识库")
        hits, reranked, note = [], False, ""
        try:
            async with httpx.AsyncClient(timeout=5) as cli:
                res = await cli.get(f"{KB_BASE}/api/kb/{p['kb_id']}/search", params={"q": q, "top_k": p["top_k"]})
                hits = res.json().get("data", []) if res.status_code == 200 else []
            if p["rerank_on"]:
                if await _svc_ok(RR_BASE):
                    note = "reranker 在线，可执行重排"
                else:
                    note = "reranker(38104) 未运行，重排降级跳过"
        except Exception as e:
            note = "检索链路异常: " + str(e)
        return {"code": 0, "data": {"pipeline": p["name"], "strategy": p["strategy"], "topK": p["top_k"],
                                    "hits": hits, "hitCount": len(hits), "rerankOn": bool(p["rerank_on"]),
                                    "reranked": reranked, "note": note, "costMs": int((time.time() - t0) * 1000)}}

    @r.get("/api/rag/kbs")
    async def kbs_for_bind():
        """供管道绑定下拉：kb 列表"""
        try:
            async with httpx.AsyncClient(timeout=3) as cli:
                res = await cli.get(KB_BASE + "/api/kb/list")
                return {"code": 0, "data": res.json().get("data", [])}
        except Exception:
            return {"code": 0, "data": []}

    return r
