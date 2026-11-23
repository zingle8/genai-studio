# -*- coding: utf-8 -*-
"""本体知识服务业务层（迁移自 app/main.py 路由内逻辑）

依赖：mapper(数据访问) / common.onto_parser(Turtle+YAML 双格式解析) / common.onto_checker(一致性检查)
接口与拆分前完全兼容。
"""
import json
import os
import sqlite3

from fastapi import HTTPException

from app.common.onto_checker import check_ontology
from app.common.onto_parser import parse_ttl, parse_yaml, to_ttl, to_yaml
from app.mapper import onto_mapper as db

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


def _require_space(space_id):
    """本体必须归属本体空间"""
    if not (space_id and db.one("SELECT id FROM tb_onto_space WHERE id=?", (space_id,))):
        raise HTTPException(400, "本体必须归属本体空间，请选择有效空间")


# ========== 本体空间 ==========
def space_list() -> list:
    return db.rows("SELECT s.*, (SELECT COUNT(*) FROM tb_ontology o WHERE o.space_id=s.id) AS onto_count"
                   " FROM tb_onto_space s ORDER BY s.id")


def space_create(body) -> dict:
    if not body.name.strip():
        raise HTTPException(400, "空间名不能为空")
    sid = db.run("INSERT INTO tb_onto_space(name, description) VALUES(?,?)", (body.name.strip(), body.comment))
    return db.one("SELECT * FROM tb_onto_space WHERE id=?", (sid,))


def space_delete(sid: int) -> None:
    if db.one("SELECT id FROM tb_ontology WHERE space_id=?", (sid,)):
        raise HTTPException(400, "空间下还有本体，请先删除")
    db.run("DELETE FROM tb_onto_space WHERE id=?", (sid,))


# ========== 本体 CRUD ==========
def onto_list() -> list:
    return db.rows("SELECT o.*, (SELECT COUNT(*) FROM tb_onto_class c WHERE c.ontology_id=o.id) AS class_count,"
                   " (SELECT COUNT(*) FROM tb_onto_rel r WHERE r.ontology_id=o.id) AS rel_count,"
                   " (SELECT s.name FROM tb_onto_space s WHERE s.id=o.space_id) AS space_name"
                   " FROM tb_ontology o ORDER BY o.id DESC")


def onto_create(body) -> dict:
    if not body.name.strip():
        raise HTTPException(400, "本体名称不能为空")
    _require_space(body.space_id)
    new_id = db.run("INSERT INTO tb_ontology(name, space_id, scope, namespace, authority, comment) VALUES(?,?,?,?,?,?)",
                    (body.name.strip(), body.space_id, body.scope, body.namespace or body.name, body.authority, body.comment))
    db.save_version(new_id, "create_onto", f"创建本体 {body.name.strip()}")
    return db.one("SELECT * FROM tb_ontology WHERE id=?", (new_id,))


def onto_update(oid: int, body) -> None:
    _require_space(body.space_id)
    db.run("UPDATE tb_ontology SET name=?, space_id=?, scope=?, namespace=?, authority=?, comment=? WHERE id=?",
           (body.name.strip(), body.space_id, body.scope, body.namespace, body.authority, body.comment, oid))
    db.save_version(oid, "update_onto", f"更新本体 {body.name.strip()}")


def onto_delete(oid: int) -> None:
    db.save_version(oid, "delete_onto", "删除本体（删除前快照）")
    db.exec_many([("DELETE FROM tb_ontology WHERE id=?", (oid,)),
                  ("DELETE FROM tb_onto_class WHERE ontology_id=?", (oid,)),
                  ("DELETE FROM tb_onto_rel WHERE ontology_id=?", (oid,)),
                  ("DELETE FROM tb_onto_mapping WHERE ontology_id=?", (oid,)),
                  ("DELETE FROM tb_onto_version WHERE ontology_id=?", (oid,))])


def onto_full(oid: int) -> dict:
    onto = db.one("SELECT * FROM tb_ontology WHERE id=?", (oid,))
    if not onto:
        raise HTTPException(404, "本体不存在")
    return {
        "ontology": onto,
        "classes": db.rows("SELECT * FROM tb_onto_class WHERE ontology_id=? ORDER BY id", (oid,)),
        "rels": db.rows("SELECT * FROM tb_onto_rel WHERE ontology_id=? ORDER BY id", (oid,)),
        "mappings": db.rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=? ORDER BY id", (oid,)),
    }


# ========== 类 / 关系规则 / 映射 CRUD ==========
def class_add(body) -> None:
    if not body.name.strip():
        raise HTTPException(400, "类名不能为空")
    dup = db.one("SELECT id FROM tb_onto_class WHERE ontology_id=? AND name=?", (body.ontologyId, body.name.strip()))
    if dup:
        raise HTTPException(400, f"类 {body.name} 已存在（同名类不可重复定义）")
    db.run("INSERT INTO tb_onto_class(ontology_id, name, parent_name, comment) VALUES(?,?,?,?)",
           (body.ontologyId, body.name.strip(), body.parentName, body.comment))
    db.save_version(body.ontologyId, "create_class", f"新增类 {body.name.strip()}")


def class_update(cid: int, body) -> None:
    """表单模式下编辑类定义"""
    if not body.name.strip():
        raise HTTPException(400, "类名不能为空")
    dup = db.one("SELECT id FROM tb_onto_class WHERE ontology_id=? AND name=? AND id<>?",
                 (body.ontologyId, body.name.strip(), cid))
    if dup:
        raise HTTPException(400, f"类 {body.name} 已存在（同名类不可重复定义）")
    db.run("UPDATE tb_onto_class SET name=?, parent_name=?, comment=? WHERE id=?",
           (body.name.strip(), body.parentName, body.comment, cid))
    db.save_version(body.ontologyId, "update_class", f"修改类 {body.name.strip()}")


def class_delete(cid: int) -> None:
    row = db.one("SELECT * FROM tb_onto_class WHERE id=?", (cid,))
    if row:
        db.save_version(row["ontology_id"], "delete_class", f"删除类 {row['name']}")
    db.run("DELETE FROM tb_onto_class WHERE id=?", (cid,))


def rel_add(body) -> None:
    if not body.name.strip():
        raise HTTPException(400, "关系名不能为空")
    if body.cardinality not in ("one", "many"):
        raise HTTPException(400, "cardinality 只能为 one/many")
    dup = db.one("SELECT id FROM tb_onto_rel WHERE ontology_id=? AND name=? AND subj_class=? AND obj_class=?",
                 (body.ontologyId, body.name.strip(), body.subjClass, body.objClass))
    if dup:
        raise HTTPException(400, f"关系规则重复：{body.subjClass} --{body.name}--> {body.objClass} 已定义")
    db.run("INSERT INTO tb_onto_rel(ontology_id, name, subj_class, obj_class, cardinality, nullable, inherits_from, comment)"
           " VALUES(?,?,?,?,?,?,?,?)",
           (body.ontologyId, body.name.strip(), body.subjClass, body.objClass, body.cardinality,
            1 if body.nullable else 0, body.inheritsFrom, body.comment))
    db.save_version(body.ontologyId, "create_rel", f"新增关系 {body.name.strip()}")


def rel_update(rid: int, body) -> None:
    """表单模式下编辑关系规则"""
    if not body.name.strip():
        raise HTTPException(400, "关系名不能为空")
    if body.cardinality not in ("one", "many"):
        raise HTTPException(400, "cardinality 只能为 one/many")
    dup = db.one("SELECT id FROM tb_onto_rel WHERE ontology_id=? AND name=? AND subj_class=? AND obj_class=? AND id<>?",
                 (body.ontologyId, body.name.strip(), body.subjClass, body.objClass, rid))
    if dup:
        raise HTTPException(400, f"关系规则重复：{body.subjClass} --{body.name}--> {body.objClass} 已定义")
    db.run("UPDATE tb_onto_rel SET name=?, subj_class=?, obj_class=?, cardinality=?, nullable=?, inherits_from=?, comment=?"
           " WHERE id=?",
           (body.name.strip(), body.subjClass, body.objClass, body.cardinality,
            1 if body.nullable else 0, body.inheritsFrom, body.comment, rid))
    db.save_version(body.ontologyId, "update_rel", f"修改关系 {body.name.strip()}")


def rel_delete(rid: int) -> None:
    row = db.one("SELECT * FROM tb_onto_rel WHERE id=?", (rid,))
    if row:
        db.save_version(row["ontology_id"], "delete_rel", f"删除关系 {row['name']}")
    db.run("DELETE FROM tb_onto_rel WHERE id=?", (rid,))


def map_add(body) -> None:
    db.run("INSERT INTO tb_onto_mapping(ontology_id, onto_type, physical_type, kind) VALUES(?,?,?,?)",
           (body.ontologyId, body.ontoType, body.physicalType, body.kind))
    db.save_version(body.ontologyId, "create_mapping", f"绑定映射 {body.ontoType} -> {body.physicalType}")


def map_delete(mid: int) -> None:
    row = db.one("SELECT * FROM tb_onto_mapping WHERE id=?", (mid,))
    if row:
        db.save_version(row["ontology_id"], "delete_mapping", "删除映射")
    db.run("DELETE FROM tb_onto_mapping WHERE id=?", (mid,))


# ========== 导入 / 导出 / 一致性检查（Turtle 与 YAML 双格式） ==========
def import_onto(body) -> dict:
    if body.format == "yaml":
        parsed_fn = parse_yaml
    elif body.format == "ttl":
        parsed_fn = parse_ttl
    else:
        raise HTTPException(400, "format 仅支持 ttl / yaml")
    try:
        parsed = parsed_fn(body.text)
    except ValueError as e:
        raise HTTPException(400, str(e))
    oid = body.ontologyId
    sqls, n_class, n_rel = [], 0, 0
    for c in parsed["classes"]:
        if not db.one("SELECT id FROM tb_onto_class WHERE ontology_id=? AND name=?", (oid, c["name"])):
            sqls.append(("INSERT INTO tb_onto_class(ontology_id, name, parent_name, comment) VALUES(?,?,?,?)",
                         (oid, c["name"], c.get("parent", ""), c["comment"])))
            n_class += 1
    for r in parsed["rels"]:
        if not db.one("SELECT id FROM tb_onto_rel WHERE ontology_id=? AND name=? AND subj_class=? AND obj_class=?",
                      (oid, r["name"], r["subj"], r["obj"])):
            sqls.append(("INSERT INTO tb_onto_rel(ontology_id, name, subj_class, obj_class, cardinality, nullable, inherits_from, comment)"
                         " VALUES(?,?,?,?,?,?,?,?)", (oid, r["name"], r["subj"], r["obj"], r["cardinality"], 1 if r["nullable"] else 0, r["inherits"], r["comment"])))
            n_rel += 1
    db.exec_many(sqls)
    db.save_version(oid, "import", f"导入{body.format}：新增 {n_class} 类 / {n_rel} 规则")
    return {"classes": n_class, "rels": n_rel, "issues": check_ontology(oid)}


def export_onto(oid: int, format: str = "ttl") -> dict:
    if format not in ("ttl", "yaml"):
        raise HTTPException(400, "format 仅支持 ttl / yaml")
    data = {"classes": db.rows("SELECT * FROM tb_onto_class WHERE ontology_id=?", (oid,)),
            "rels": db.rows("SELECT * FROM tb_onto_rel WHERE ontology_id=?", (oid,))}
    text = to_yaml(data) if format == "yaml" else to_ttl(data)
    return {"text": text, "format": format}


def check(oid: int) -> list:
    return check_ontology(oid)


# ========== 数据源与图数据 ==========
def _graph_ref_data(cfg: dict) -> dict:
    """type=graph-ref 数据源：从图谱模块 SQLite 读取指定图谱的节点/边，按实体名与关系类型映射"""
    gid = cfg.get("graphId") or cfg.get("graph_id")
    if not gid:
        return {"nodes": [], "edges": []}
    path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "py-genai-graph", "graph.db")
    if not os.path.exists(path):
        return {"nodes": [], "edges": [], "message": "图谱数据文件不存在"}
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        ents = {r["id"]: r["name"] for r in con.execute("SELECT id, name FROM tb_graph_entity WHERE graph_id=?", (gid,))}
        nodes = []
        for r in con.execute("SELECT id, entity_id, name, props FROM tb_graph_node WHERE graph_id=?", (gid,)):
            d = dict(r); d["type"] = ents.get(d.get("entity_id"), "人物"); nodes.append(d)
        edges = []
        for r in con.execute("SELECT id, source_id, target_id, rel_type, props FROM tb_graph_edge WHERE graph_id=?", (gid,)):
            d = dict(r); d["type"] = d.get("rel_type", ""); edges.append(d)
        return {"nodes": nodes, "edges": edges}
    finally:
        con.close()


def datasources() -> list:
    data = db.rows("SELECT * FROM tb_data_source ORDER BY id")
    if not any(d["type"] == "builtin-demo" for d in data):
        db.run("INSERT INTO tb_data_source(name, type, config) VALUES(?,?,?)", ("内置示例·公司数据", "builtin-demo", "{}"))
        data = db.rows("SELECT * FROM tb_data_source ORDER BY id")
    return data


def datasource_add(body: dict) -> None:
    db.run("INSERT INTO tb_data_source(name, type, config) VALUES(?,?,?)",
           (body.get("name", ""), body.get("type", "neo4j"), json.dumps(body.get("config", {}), ensure_ascii=False)))


def graph_data(ds: int = 1) -> dict:
    src = db.one("SELECT * FROM tb_data_source WHERE id=?", (ds,))
    if not src:
        raise HTTPException(404, "数据源不存在")
    if src["type"] == "builtin-demo":
        return {**DEMO_DATA, "source": src["name"], "readonly": True}
    cfg = json.loads(src["config"] or "{}")
    if src["type"] == "graph-ref":
        return {**_graph_ref_data(cfg), "source": src["name"], "readonly": True}
    # Neo4j 等真实图库：按 config 连接拉取（MVP 阶段返回占位，接入后替换）
    return {"nodes": [], "edges": [], "source": src["name"], "readonly": True,
            "message": f"类型 {src['type']} 数据源待接入（config: {cfg.get('uri', '')}）"}


def view_graph(oid: int, ds: int = 1) -> dict:
    """本体视图投影：按本体映射将物理图数据投影为本体视角（MVP：映射类型过滤）"""
    maps = db.rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=?", (oid,))
    node_types = {m["physical_type"] for m in maps if m["kind"] == "node"}
    edge_types = {m["physical_type"] for m in maps if m["kind"] == "edge"}
    src = db.one("SELECT * FROM tb_data_source WHERE id=?", (ds,))
    if src and src["type"] == "graph-ref":
        data = {**_graph_ref_data(json.loads(src["config"] or "{}")), "source": src["name"]}
    else:
        data = {**DEMO_DATA, "source": "示例数据"}
    if node_types:
        data["nodes"] = [n for n in data["nodes"] if n["type"] in node_types]
    if edge_types:
        data["edges"] = [e for e in data["edges"] if e["type"] in edge_types]
    return data


# ========== 版本快照（自动快照 + 详情 + 恢复） ==========
def version_list(oid: int) -> list:
    if not db.one("SELECT id FROM tb_ontology WHERE id=?", (oid,)):
        raise HTTPException(404, "本体不存在")
    return db.rows("SELECT id, ontology_id, version_no, op, note, created_at FROM tb_onto_version "
                   "WHERE ontology_id=? ORDER BY version_no DESC", (oid,))


def version_detail(oid: int, no: int) -> dict:
    v = db.one("SELECT * FROM tb_onto_version WHERE ontology_id=? AND version_no=?", (oid, no))
    if not v:
        raise HTTPException(404, "版本不存在")
    return {k: (json.loads(v[k]) if k == "snapshot" else v[k]) for k in
            ("id", "ontology_id", "version_no", "op", "note", "created_at", "snapshot")}


def version_restore(oid: int, no: int) -> dict:
    """恢复到指定版本：当前态先存一版，再按快照原 ID 回填类/关系/映射"""
    v = db.one("SELECT * FROM tb_onto_version WHERE ontology_id=? AND version_no=?", (oid, no))
    if not v:
        raise HTTPException(404, "版本不存在")
    db.save_version(oid, "pre_restore", f"恢复到 v{no} 前自动保存")
    snap = json.loads(v["snapshot"])
    db.exec_many([
        ("DELETE FROM tb_onto_mapping WHERE ontology_id=?", (oid,)),
        ("DELETE FROM tb_onto_rel WHERE ontology_id=?", (oid,)),
        ("DELETE FROM tb_onto_class WHERE ontology_id=?", (oid,)),
    ])
    for c in snap.get("classes", []):
        db.run("INSERT INTO tb_onto_class(id, ontology_id, name, parent_name, comment) VALUES(?,?,?,?,?)",
               (c["id"], oid, c["name"], c.get("parent_name", ""), c.get("comment", "")))
    for r in snap.get("rels", []):
        db.run("INSERT INTO tb_onto_rel(id, ontology_id, name, subj_class, obj_class, cardinality, nullable, inherits_from, comment) "
               "VALUES(?,?,?,?,?,?,?,?,?)",
               (r["id"], oid, r["name"], r["subj_class"], r["obj_class"], r.get("cardinality", "many"),
                r.get("nullable", 1), r.get("inherits_from", ""), r.get("comment", "")))
    for m in snap.get("mappings", []):
        db.run("INSERT INTO tb_onto_mapping(id, ontology_id, onto_type, physical_type, kind) VALUES(?,?,?,?,?)",
               (m["id"], oid, m["onto_type"], m["physical_type"], m.get("kind", "node")))
    db.save_version(oid, "restore", f"恢复到 v{no}")
    return {"restored": no}
