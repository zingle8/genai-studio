# -*- coding: utf-8 -*-
"""知识图谱服务（38107）：节点/关系 CRUD + 邻域查询 + 全图输出"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.config import settings
from app.gateway_report import gateway_report
from app import storage

app = FastAPI(title="GenAI Studio - 知识图谱服务", version="0.1.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


gateway_report.init(settings)
gateway_report.install(app)


@app.get("/health")
async def health():
    return {"service": settings.service_id, "status": "ok"}


class NodeIn(BaseModel):
    label: str
    name: str
    props: str = ""


class EdgeIn(BaseModel):
    source_id: int
    target_id: int
    rel_type: str
    props: str = ""


# ===== 节点 =====
@app.get("/api/graph/nodes")
async def node_list(q: str = ""):
    if q.strip():
        like = f"%{q.strip()}%"
        return {"code": 0, "data": storage.rows(
            "SELECT * FROM tb_graph_node WHERE name LIKE ? OR label LIKE ? ORDER BY id", (like, like))}
    return {"code": 0, "data": storage.rows("SELECT * FROM tb_graph_node ORDER BY id")}


@app.post("/api/graph/nodes")
async def node_create(b: NodeIn):
    if not b.label.strip() or not b.name.strip():
        raise HTTPException(400, "label/name 不能为空")
    nid = storage.run("INSERT INTO tb_graph_node(label, name, props) VALUES(?,?,?)",
                      (b.label.strip(), b.name.strip(), b.props))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_graph_node WHERE id=?", (nid,))}


@app.put("/api/graph/nodes/{nid}")
async def node_update(nid: int, b: NodeIn):
    if not storage.one("SELECT id FROM tb_graph_node WHERE id=?", (nid,)):
        raise HTTPException(404, "节点不存在")
    storage.run("UPDATE tb_graph_node SET label=?, name=?, props=? WHERE id=?",
                (b.label.strip(), b.name.strip(), b.props, nid))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_graph_node WHERE id=?", (nid,))}


@app.delete("/api/graph/nodes/{nid}")
async def node_delete(nid: int):
    storage.run("DELETE FROM tb_graph_edge WHERE source_id=? OR target_id=?", (nid, nid))
    storage.run("DELETE FROM tb_graph_node WHERE id=?", (nid,))
    return {"code": 0, "data": "deleted"}


# ===== 关系边 =====
@app.get("/api/graph/edges")
async def edge_list():
    es = storage.rows("SELECT * FROM tb_graph_edge ORDER BY id")
    nodes = {n["id"]: n for n in storage.rows("SELECT id, label, name FROM tb_graph_node")}
    for e in es:
        s, t = nodes.get(e["source_id"]), nodes.get(e["target_id"])
        e["sourceName"] = s["name"] if s else "?"
        e["targetName"] = t["name"] if t else "?"
    return {"code": 0, "data": es}


@app.post("/api/graph/edges")
async def edge_create(b: EdgeIn):
    if not storage.one("SELECT id FROM tb_graph_node WHERE id=?", (b.source_id,)):
        raise HTTPException(400, "source 节点不存在")
    if not storage.one("SELECT id FROM tb_graph_node WHERE id=?", (b.target_id,)):
        raise HTTPException(400, "target 节点不存在")
    if not b.rel_type.strip():
        raise HTTPException(400, "rel_type 不能为空")
    eid = storage.run("INSERT INTO tb_graph_edge(source_id, target_id, rel_type, props) VALUES(?,?,?,?)",
                      (b.source_id, b.target_id, b.rel_type.strip(), b.props))
    e = storage.one("SELECT * FROM tb_graph_edge WHERE id=?", (eid,))
    s = storage.one("SELECT name FROM tb_graph_node WHERE id=?", (b.source_id,))
    t = storage.one("SELECT name FROM tb_graph_node WHERE id=?", (b.target_id,))
    e["sourceName"], e["targetName"] = s["name"], t["name"]
    return {"code": 0, "data": e}


@app.put("/api/graph/edges/{eid}")
async def edge_update(eid: int, b: EdgeIn):
    if not storage.one("SELECT id FROM tb_graph_edge WHERE id=?", (eid,)):
        raise HTTPException(404, "关系不存在")
    storage.run("UPDATE tb_graph_edge SET source_id=?, target_id=?, rel_type=?, props=? WHERE id=?",
                (b.source_id, b.target_id, b.rel_type.strip(), b.props, eid))
    return {"code": 0, "data": storage.one("SELECT * FROM tb_graph_edge WHERE id=?", (eid,))}


@app.delete("/api/graph/edges/{eid}")
async def edge_delete(eid: int):
    storage.run("DELETE FROM tb_graph_edge WHERE id=?", (eid,))
    return {"code": 0, "data": "deleted"}


# ===== 全图 / 邻域 =====
@app.get("/api/graph/view")
async def graph_view():
    nodes = storage.rows("SELECT * FROM tb_graph_node ORDER BY id")
    edges = storage.rows("SELECT * FROM tb_graph_edge ORDER BY id")
    labels = list({n["label"] for n in nodes})
    return {"code": 0, "data": {"nodes": nodes, "edges": edges, "labels": labels,
                                "stats": {"nodes": len(nodes), "edges": len(edges), "labels": len(labels)}}}


@app.get("/api/graph/neighborhood")
async def neighborhood(nid: int, depth: int = 1):
    """从指定节点扩展邻域子图（BFS depth 层）"""
    front, seen, edges_all = {nid}, {nid}, storage.rows("SELECT * FROM tb_graph_edge")
    for _ in range(max(1, depth)):
        nxt = set()
        for e in edges_all:
            if e["source_id"] in front:
                nxt.add(e["target_id"])
            if e["target_id"] in front:
                nxt.add(e["source_id"])
        seen |= nxt
        front = nxt - front
    nodes = storage.rows("SELECT * FROM tb_graph_node WHERE id IN (%s)" % ",".join(map(str, seen)))
    es = [e for e in edges_all if e["source_id"] in seen and e["target_id"] in seen]
    return {"code": 0, "data": {"nodes": nodes, "edges": es}}


@app.on_event("shutdown")
async def shutdown() -> None:
    gateway_report.stop()
