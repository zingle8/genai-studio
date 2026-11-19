# -*- coding: utf-8 -*-
"""本体知识服务（端口 38105）：本体/类/关系规则管理、Turtle 导入导出、一致性检查、图数据源绑定"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import json

from config import settings
from gateway_report import GatewayReport
from storage import rows, run, one, exec_many
from checker import check_ontology
from parser import parse_ttl, to_ttl

app = FastAPI(title="py-genai-ontology")
report: Optional[GatewayReport] = None


def _require_space(space_id):
    """本体必须归属本体空间"""
    if not (space_id and one("SELECT id FROM tb_onto_space WHERE id=?", (space_id,))):
        raise HTTPException(400, "本体必须归属本体空间，请选择有效空间")


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_id}


@app.on_event("shutdown")
async def shutdown() -> None:
    if report:
        await report.stop()


@app.on_event("startup")
async def startup() -> None:
    global report
    try:
        report = GatewayReport()
        await report.start()
    except Exception:
        report = None


# ========== 数据模型 ==========
class OntoIn(BaseModel):
    name: str
    space_id: int = 0              # 归属本体空间（必填，创建时校验）
    scope: str = "domain"          # domain=领域 / personal=个人
    namespace: str = ""
    authority: str = "normal"      # high/normal
    comment: str = ""


class SpaceIn(BaseModel):
    name: str
    comment: str = ""


class ClassIn(BaseModel):
    ontologyId: int
    name: str
    parentName: str = ""
    comment: str = ""


class RelIn(BaseModel):
    ontologyId: int
    name: str
    subjClass: str
    objClass: str
    cardinality: str = "many"      # one / many
    nullable: bool = True
    inheritsFrom: str = ""
    comment: str = ""


class MapIn(BaseModel):
    ontologyId: int
    ontoType: str
    physicalType: str
    kind: str = "node"             # node / edge


class ImportIn(BaseModel):
    ontologyId: int
    text: str


# ========== 本体空间（对齐知识库空间模型；须先于 /api/onto/{oid} 模板注册） ==========
@app.get("/api/onto/spaces")
async def list_space():
    data = rows("SELECT s.*, (SELECT COUNT(*) FROM tb_ontology o WHERE o.space_id=s.id) AS onto_count"
                " FROM tb_onto_space s ORDER BY s.id")
    return {"code": 0, "data": data}


@app.post("/api/onto/spaces")
async def create_space(body: SpaceIn):
    if not body.name.strip():
        raise HTTPException(400, "空间名不能为空")
    sid = run("INSERT INTO tb_onto_space(name, description) VALUES(?,?)", (body.name.strip(), body.comment))
    return {"code": 0, "data": one("SELECT * FROM tb_onto_space WHERE id=?", (sid,))}


@app.delete("/api/onto/spaces/{sid}")
async def delete_space(sid: int):
    if one("SELECT id FROM tb_ontology WHERE space_id=?", (sid,)):
        raise HTTPException(400, "空间下还有本体，请先删除")
    run("DELETE FROM tb_onto_space WHERE id=?", (sid,))
    return {"code": 0}


# ========== 本体 CRUD ==========
@app.get("/api/onto/ontologies")
async def list_onto():
    data = rows("SELECT o.*, (SELECT COUNT(*) FROM tb_onto_class c WHERE c.ontology_id=o.id) AS class_count,"
                " (SELECT COUNT(*) FROM tb_onto_rel r WHERE r.ontology_id=o.id) AS rel_count,"
                " (SELECT s.name FROM tb_onto_space s WHERE s.id=o.space_id) AS space_name"
                " FROM tb_ontology o ORDER BY o.id DESC")
    return {"code": 0, "data": data}


@app.post("/api/onto/ontologies")
async def create_onto(body: OntoIn):
    if not body.name.strip():
        raise HTTPException(400, "本体名称不能为空")
    _require_space(body.space_id)
    new_id = run("INSERT INTO tb_ontology(name, space_id, scope, namespace, authority, comment) VALUES(?,?,?,?,?,?)",
                 (body.name.strip(), body.space_id, body.scope, body.namespace or body.name, body.authority, body.comment))
    return {"code": 0, "data": one("SELECT * FROM tb_ontology WHERE id=?", (new_id,))}


@app.put("/api/onto/ontologies/{oid}")
async def update_onto(oid: int, body: OntoIn):
    _require_space(body.space_id)
    run("UPDATE tb_ontology SET name=?, space_id=?, scope=?, namespace=?, authority=?, comment=? WHERE id=?",
        (body.name.strip(), body.space_id, body.scope, body.namespace, body.authority, body.comment, oid))
    return {"code": 0}


@app.delete("/api/onto/ontologies/{oid}")
async def delete_onto(oid: int):
    exec_many([("DELETE FROM tb_ontology WHERE id=?", (oid,)),
               ("DELETE FROM tb_onto_class WHERE ontology_id=?", (oid,)),
               ("DELETE FROM tb_onto_rel WHERE ontology_id=?", (oid,)),
               ("DELETE FROM tb_onto_mapping WHERE ontology_id=?", (oid,))])
    return {"code": 0}


@app.get("/api/onto/{oid}/full")
async def onto_full(oid: int):
    onto = one("SELECT * FROM tb_ontology WHERE id=?", (oid,))
    if not onto:
        raise HTTPException(404, "本体不存在")
    return {"code": 0, "data": {
        "ontology": onto,
        "classes": rows("SELECT * FROM tb_onto_class WHERE ontology_id=? ORDER BY id", (oid,)),
        "rels": rows("SELECT * FROM tb_onto_rel WHERE ontology_id=? ORDER BY id", (oid,)),
        "mappings": rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=? ORDER BY id", (oid,)),
    }}


# ========== 类 / 关系规则 / 映射 CRUD ==========
@app.post("/api/onto/classes")
async def add_class(body: ClassIn):
    if not body.name.strip():
        raise HTTPException(400, "类名不能为空")
    dup = one("SELECT id FROM tb_onto_class WHERE ontology_id=? AND name=?", (body.ontologyId, body.name.strip()))
    if dup:
        raise HTTPException(400, f"类 {body.name} 已存在（同名类不可重复定义）")
    run("INSERT INTO tb_onto_class(ontology_id, name, parent_name, comment) VALUES(?,?,?,?)",
        (body.ontologyId, body.name.strip(), body.parentName, body.comment))
    return {"code": 0}


@app.delete("/api/onto/classes/{cid}")
async def del_class(cid: int):
    run("DELETE FROM tb_onto_class WHERE id=?", (cid,))
    return {"code": 0}


@app.post("/api/onto/rels")
async def add_rel(body: RelIn):
    if not body.name.strip():
        raise HTTPException(400, "关系名不能为空")
    if body.cardinality not in ("one", "many"):
        raise HTTPException(400, "cardinality 只能为 one/many")
    dup = one("SELECT id FROM tb_onto_rel WHERE ontology_id=? AND name=? AND subj_class=? AND obj_class=?",
              (body.ontologyId, body.name.strip(), body.subjClass, body.objClass))
    if dup:
        raise HTTPException(400, f"关系规则重复：{body.subjClass} --{body.name}--> {body.objClass} 已定义")
    run("INSERT INTO tb_onto_rel(ontology_id, name, subj_class, obj_class, cardinality, nullable, inherits_from, comment)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (body.ontologyId, body.name.strip(), body.subjClass, body.objClass, body.cardinality,
         1 if body.nullable else 0, body.inheritsFrom, body.comment))
    return {"code": 0}


@app.delete("/api/onto/rels/{rid}")
async def del_rel(rid: int):
    run("DELETE FROM tb_onto_rel WHERE id=?", (rid,))
    return {"code": 0}


@app.post("/api/onto/mappings")
async def add_map(body: MapIn):
    run("INSERT INTO tb_onto_mapping(ontology_id, onto_type, physical_type, kind) VALUES(?,?,?,?)",
        (body.ontologyId, body.ontoType, body.physicalType, body.kind))
    return {"code": 0}


@app.delete("/api/onto/mappings/{mid}")
async def del_map(mid: int):
    run("DELETE FROM tb_onto_mapping WHERE id=?", (mid,))
    return {"code": 0}


# ========== 导入 / 导出 / 一致性检查 ==========
@app.post("/api/onto/import")
async def import_ttl(body: ImportIn):
    try:
        parsed = parse_ttl(body.text)
    except ValueError as e:
        raise HTTPException(400, str(e))
    oid = body.ontologyId
    sqls, n_class, n_rel = [], 0, 0
    for c in parsed["classes"]:
        if not one("SELECT id FROM tb_onto_class WHERE ontology_id=? AND name=?", (oid, c["name"])):
            sqls.append(("INSERT INTO tb_onto_class(ontology_id, name, comment) VALUES(?,?,?)", (oid, c["name"], c["comment"])))
            n_class += 1
    for r in parsed["rels"]:
        if not one("SELECT id FROM tb_onto_rel WHERE ontology_id=? AND name=? AND subj_class=? AND obj_class=?",
                   (oid, r["name"], r["subj"], r["obj"])):
            sqls.append(("INSERT INTO tb_onto_rel(ontology_id, name, subj_class, obj_class, cardinality, nullable, inherits_from, comment)"
                         " VALUES(?,?,?,?,?,?,?,?)", (oid, r["name"], r["subj"], r["obj"], r["cardinality"], 1 if r["nullable"] else 0, r["inherits"], r["comment"])))
            n_rel += 1
    exec_many(sqls)
    return {"code": 0, "data": {"classes": n_class, "rels": n_rel, "issues": check_ontology(oid)}}


@app.get("/api/onto/{oid}/export")
async def export_ttl(oid: int):
    data = {"classes": rows("SELECT * FROM tb_onto_class WHERE ontology_id=?", (oid,)),
            "rels": rows("SELECT * FROM tb_onto_rel WHERE ontology_id=?", (oid,))}
    return {"code": 0, "data": {"text": to_ttl(data)}}


@app.get("/api/onto/{oid}/check")
async def check(oid: int):
    return {"code": 0, "data": check_ontology(oid)}


# ========== 数据源与图数据（MVP：内置示例公司数据 + SQLite 物理表） ==========
DEMO_DATA = {
    "nodes": [
        {"type": "c0", "id": "c0-1", "props": {"名称": "研发部", "编码": "C0-DEV"}},
        {"type": "c0", "id": "c0-2", "props": {"名称": "市场部", "编码": "C0-MKT"}},
        {"type": "a1", "id": "a1-1", "props": {"姓名": "张三", "工号": "A1001"}},
        {"type": "a1", "id": "a1-2", "props": {"姓名": "李四", "工号": "A1002"}},
        {"type": "a1", "id": "a1-3", "props": {"姓名": "王五", "工号": "A1003"}},
        {"type": "b1", "id": "b1-1", "props": {"项目": "GenAI 平台", "编码": "B1-G01"}},
        {"type": "b1", "id": "b1-2", "props": {"项目": "本体 RAG", "编码": "B1-G02"}},
        {"type": "c1", "id": "c1-1", "props": {"外部组织": "合作方甲", "编码": "C1-P01"}},
    ],
    "edges": [
        {"type": "works_in", "from": "a1-1", "to": "c0-1", "props": {}},
        {"type": "works_in", "from": "a1-2", "to": "c0-1", "props": {}},
        {"type": "works_in", "from": "a1-3", "to": "c0-2", "props": {}},
        {"type": "join_project", "from": "a1-1", "to": "b1-1", "props": {"角色": "负责人"}},
        {"type": "join_project", "from": "a1-2", "to": "b1-2", "props": {"角色": "成员"}},
        {"type": "cooperate_with", "from": "c0-1", "to": "c1-1", "props": {}},
    ],
}


@app.get("/api/onto/datasources")
async def datasources():
    data = rows("SELECT * FROM tb_data_source ORDER BY id")
    if not any(d["type"] == "builtin-demo" for d in data):
        run("INSERT INTO tb_data_source(name, type, config) VALUES(?,?,?)", ("内置示例·公司数据", "builtin-demo", "{}"))
        data = rows("SELECT * FROM tb_data_source ORDER BY id")
    return {"code": 0, "data": data}


@app.post("/api/onto/datasources")
async def add_datasource(body: dict):
    run("INSERT INTO tb_data_source(name, type, config) VALUES(?,?,?)",
        (body.get("name", ""), body.get("type", "neo4j"), json.dumps(body.get("config", {}), ensure_ascii=False)))
    return {"code": 0}


@app.get("/api/onto/graph-data")
async def graph_data(ds: int = 1):
    src = one("SELECT * FROM tb_data_source WHERE id=?", (ds,))
    if not src:
        raise HTTPException(404, "数据源不存在")
    if src["type"] == "builtin-demo":
        return {"code": 0, "data": {**DEMO_DATA, "source": src["name"], "readonly": True}}
    # Neo4j 等真实图库：按 config 连接拉取（MVP 阶段返回占位，接入后替换）
    cfg = json.loads(src["config"] or "{}")
    return {"code": 0, "data": {"nodes": [], "edges": [], "source": src["name"], "readonly": True,
                                "message": f"类型 {src['type']} 数据源待接入（config: {cfg.get('uri', '')}）"}}


@app.get("/api/onto/{oid}/view-graph")
async def view_graph(oid: int, ds: int = 1):
    """本体视图投影：按本体映射将物理图数据投影为本体视角（MVP：映射类型过滤）"""
    maps = rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=?", (oid,))
    node_types = {m["physical_type"] for m in maps if m["kind"] == "node"}
    edge_types = {m["physical_type"] for m in maps if m["kind"] == "edge"}
    data = {**DEMO_DATA, "source": "示例数据"}
    if node_types:
        data["nodes"] = [n for n in data["nodes"] if n["type"] in node_types]
    if edge_types:
        data["edges"] = [e for e in data["edges"] if e["type"] in edge_types]
    return {"code": 0, "data": data}
