# -*- coding: utf-8 -*-
"""RAG 管理 API（38109 增量路由）：检索管道配置 / 索引统计 / 检索测试（联动 kb 38106 与 reranker 38104）"""
import sqlite3, os, time, httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

KB_BASE = os.environ.get("KB_BASE", "http://localhost:38126")
RR_BASE = os.environ.get("RR_BASE", "http://localhost:38104")
EM_BASE = os.environ.get("EM_BASE", "http://localhost:38103")
GRAPH_BASE = os.environ.get("GRAPH_BASE", "http://localhost:38137")
ONTO_BASE = os.environ.get("ONTO_BASE", "http://localhost:38105")
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
        CREATE TABLE IF NOT EXISTS tb_rag_eval(
          id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
          source_type TEXT DEFAULT 'kb', source_id INTEGER, source_name TEXT DEFAULT '',
          q TEXT NOT NULL, expect TEXT DEFAULT '', top_k INTEGER DEFAULT 5,
          hit INTEGER DEFAULT 0, rank INTEGER DEFAULT 0, score REAL DEFAULT 0,
          latency_ms INTEGER DEFAULT 0,
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


class QueryIn(BaseModel):
    source_type: str = "kb"          # kb | graph | onto
    source_id: int
    q: str
    top_k: int = 5


class EvalCase(BaseModel):
    q: str
    expect: str = ""                 # 期望关键词（空则仅要求有结果）


class EvalIn(BaseModel):
    source_type: str = "kb"
    source_id: int
    source_name: str = ""
    top_k: int = 5
    cases: list  # [{q, expect}]


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
        kbs, kb_ok, em_ok, rr_ok = [], False, False, False
        try:
            async with httpx.AsyncClient(timeout=3) as cli:
                r = await cli.get(KB_BASE + "/api/kb/list")
                if r.status_code == 200:
                    kbs = r.json().get("data", [])
                    kb_ok = True
                em_ok = (await cli.get(EM_BASE + "/health")).status_code == 200
                rr_ok = (await cli.get(RR_BASE + "/health")).status_code == 200
        except Exception:
            pass
        return {"code": 0, "data": {
            "kbs": [{"id": k["id"], "name": k["name"], "docCount": k.get("docCount", 0),
                     "chunkCount": k.get("chunkCount", 0)} for k in kbs],
            "services": {"knowledgebase(38126)": kb_ok, "embedding(38103)": em_ok,
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

    # ===== RAG 查询（多源：知识库 / 知识图谱 / 本体图谱） =====
    @r.get("/api/rag/sources")
    async def rag_sources():
        """三类知识源实例列表：kb / graph / onto"""
        out = {"kb": [], "graph": [], "onto": []}
        try:
            async with httpx.AsyncClient(timeout=5) as cli:
                res = await cli.get(KB_BASE + "/api/kb/list")
                if res.status_code == 200:
                    out["kb"] = [{"id": x["id"], "name": x["name"], "chunkCount": x.get("chunkCount", 0),
                                  "meta": (x.get("db_type") or "") + "/" + (x.get("kb_type") or "")}
                                 for x in res.json().get("data", [])]
                res = await cli.get(GRAPH_BASE + "/api/graphs")
                if res.status_code == 200:
                    out["graph"] = [{"id": x["id"], "name": x["name"], "chunkCount": x.get("nodeCount", 0),
                                     "meta": x.get("db_type") or ""} for x in res.json().get("data", [])]
                res = await cli.get(ONTO_BASE + "/api/onto/ontologies")
                if res.status_code == 200:
                    items = res.json().get("data", [])
                    if isinstance(items, dict):
                        items = items.get("data", items.get("list", []))
                    out["onto"] = [{"id": x.get("id"), "name": x.get("name"),
                                    "chunkCount": x.get("classCount", 0), "meta": "ontology"}
                                   for x in items if isinstance(x, dict)]
        except Exception:
            pass
        return {"code": 0, "data": out}

    @r.post("/api/rag/query")
    async def rag_query(b: QueryIn):
        """统一 RAG 查询：kb 全文检索 / graph 关键词匹配节点+邻域子图 / onto 类目匹配"""
        import re as _re, json as _json
        if not b.q.strip():
            raise HTTPException(400, "q 不能为空")
        terms = [x for x in _re.split(r"[\s，。,、;；]+", b.q) if x] or [b.q.strip()]
        try:
            async with httpx.AsyncClient(timeout=8) as cli:
                if b.source_type == "kb":
                    res = await cli.get(f"{KB_BASE}/api/kb/{b.source_id}/search",
                                        params={"q": b.q, "top_k": b.top_k})
                    if res.status_code != 200:
                        raise HTTPException(400, "知识库检索失败：" + res.text[:120])
                    j = res.json()
                    hits = [{"title": h.get("doc", ""), "content": h.get("content", ""),
                             "score": h.get("score", 0), "meta": f"chunk #{h.get('idx', '?')}"}
                            for h in j.get("data", [])]
                    return {"code": 0, "data": {"backend": j.get("backend", "kb"), "hits": hits}}
                if b.source_type == "graph":
                    res = await cli.get(f"{GRAPH_BASE}/api/graphs/{b.source_id}/nodes")
                    nodes = (res.json().get("data") or {}).get("nodes", [])
                    res = await cli.get(f"{GRAPH_BASE}/api/graphs/{b.source_id}/edges")
                    edges = res.json().get("data") or []
                    nm = {n["id"]: n.get("name", "?") for n in nodes}
                    matched = [n for n in nodes
                               if any(t.lower() in _json.dumps(n, ensure_ascii=False).lower() for t in terms)][: b.top_k]
                    hits = []
                    for n in matched:
                        rels = [e for e in edges
                                if e.get("source_id") == n["id"] or e.get("target_id") == n["id"]][: 8]
                        content = "\n".join(f"{nm.get(e.get('source_id'), '?')} -[{e.get('rel_type')}]-> "
                                            f"{nm.get(e.get('target_id'), '?')}" for e in rels) or "（无关系边）"
                        hits.append({"title": n.get("name", ""), "content": content,
                                     "score": 1.0, "meta": f"graph node #{n['id']}"})
                    return {"code": 0, "data": {"backend": "graph", "hits": hits}}
                if b.source_type == "onto":
                    res = await cli.get(f"{ONTO_BASE}/api/onto/{b.source_id}/full")
                    data = res.json().get("data") or {}
                    classes = data.get("classes", [])
                    matched = [c for c in classes
                               if any(t.lower() in ((c.get("name") or "") + (c.get("comment") or "")
                                                    + (c.get("description") or "")).lower()
                                      for t in terms)][: b.top_k]
                    hits = [{"title": c.get("name", ""), "content": c.get("comment") or c.get("description") or "（无描述）",
                             "score": 1.0, "meta": f"onto class #{c.get('id')}"} for c in matched]
                    return {"code": 0, "data": {"backend": "ontology", "hits": hits}}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"查询失败：{str(e)[:160]}")
        raise HTTPException(400, f"未知源类型 {b.source_type}（kb / graph / onto）")

    # ===== RAG 评估（测试集检索 → hit@k / MRR / 平均分 / 时延，结果落库留痕） =====
    @r.post("/api/rag/evaluate")
    async def rag_evaluate(b: EvalIn):
        import uuid as _uuid
        if not b.cases:
            raise HTTPException(400, "cases 不能为空")
        rid = _uuid.uuid4().hex[:10]
        details = []
        try:
            async with httpx.AsyncClient(timeout=10) as cli:
                for cse in b.cases:
                    q = cse.get("q") if isinstance(cse, dict) else cse.q
                    expect = (cse.get("expect") or "") if isinstance(cse, dict) else (cse.expect or "")
                    if not (q or "").strip():
                        continue
                    ts = time.time()
                    res = await cli.get(f"{KB_BASE}/api/kb/{b.source_id}/search",
                                        params={"q": q, "top_k": b.top_k})
                    latency = int((time.time() - ts) * 1000)
                    hits = res.json().get("data", []) if res.status_code == 200 else []
                    expect = (expect or "").strip()
                    rank = 0
                    if expect:
                        for i, h in enumerate(hits, 1):
                            blob = (h.get("content", "") + h.get("doc", "")).lower()
                            if expect.lower() in blob:
                                rank = i
                                break
                    hit = (rank > 0) if expect else bool(hits)
                    score = hits[0].get("score", 0) if hits else 0
                    run("INSERT INTO tb_rag_eval(run_id, source_type, source_id, source_name, q, expect, top_k, hit, rank, score, latency_ms) "
                        "VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                        (rid, b.source_type, b.source_id, b.source_name, q, expect, b.top_k,
                         1 if hit else 0, rank, score, latency))
                    details.append({"q": q, "expect": expect, "hit": hit, "rank": rank,
                                    "score": score, "latencyMs": latency,
                                    "topContent": (hits[0].get("content", "")[:120] if hits else "")})
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(400, f"评估执行失败：{str(e)[:160]}")
        n = len(details) or 1
        summary = {"cases": len(details),
                   "hitRate": round(sum(1 for d in details if d["hit"]) / n, 3),
                   "mrr": round(sum(1 / d["rank"] for d in details if d["rank"] > 0) / n, 3),
                   "avgScore": round(sum(d["score"] for d in details) / n, 2),
                   "avgLatencyMs": round(sum(d["latencyMs"] for d in details) / n)}
        return {"code": 0, "data": {"runId": rid, "summary": summary, "details": details}}

    @r.get("/api/rag/evals")
    async def rag_eval_history(limit: int = 30):
        rows_ = rows("SELECT * FROM tb_rag_eval ORDER BY id DESC LIMIT ?", (limit,))
        runs = {}
        for x in rows_:
            g = runs.setdefault(x["run_id"], {"runId": x["run_id"], "sourceType": x["source_type"],
                                              "sourceId": x["source_id"], "sourceName": x["source_name"],
                                              "createdAt": x["created_at"], "cases": 0, "hits": 0,
                                              "avgLatencyMs": 0, "mrr": 0.0})
            g["cases"] += 1
            g["hits"] += 1 if x["hit"] else 0
            g["avgLatencyMs"] += x["latency_ms"]
            g["mrr"] += (1 / x["rank"]) if x["rank"] else 0
        for g in runs.values():
            g["hitRate"] = round(g["hits"] / max(1, g["cases"]), 3)
            g["mrr"] = round(g["mrr"] / max(1, g["cases"]), 3)
            g["avgLatencyMs"] = round(g["avgLatencyMs"] / max(1, g["cases"]))
        return {"code": 0, "data": list(runs.values())}

    return r
