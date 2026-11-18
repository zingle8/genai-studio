# -*- coding: utf-8 -*-
"""图谱业务实现（service/impl）：图谱/实体/节点/关系/版本的编排与双后端（SQLite/Neo4j）路由"""
import json

from fastapi import HTTPException

from app.mapper import graph_mapper as storage
from app.service.graph_service import GraphService


class GraphServiceImpl(GraphService):

    # ===== 通用辅助 =====
    @staticmethod
    def _gcfg(g):
        try:
            return json.loads(g["db_config"] or "{}")
        except Exception:
            return {}

    def _get_graph(self, gid):
        g = storage.one("SELECT * FROM tb_graph WHERE id=?", (gid,))
        if not g:
            raise HTTPException(404, "图谱不存在")
        return g

    def _neo_nodes(self, g, gid):
        cfg = self._gcfg(g)
        j = storage.neo4j_exec(cfg,
            "MATCH (n:Graph_%d) RETURN id(n) AS id, labels(n) AS labels, n.name AS name, n.props AS props" % gid)
        return [{"id": row["row"][0], "entity_id": 0, "name": row["row"][2] or "",
                 "props": json.dumps(row["row"][3] or {}, ensure_ascii=False)}
                for row in j["results"][0]["data"]]

    def _neo_edges(self, g, gid):
        cfg = self._gcfg(g)
        j = storage.neo4j_exec(cfg,
            "MATCH (a:Graph_%d)-[r]->(b:Graph_%d) RETURN id(a) AS s, id(b) AS t, type(r) AS rt" % (gid, gid))
        return [{"id": i, "source_id": row["row"][0], "target_id": row["row"][1], "rel_type": row["row"][2]}
                for i, row in enumerate(j["results"][0]["data"])]

    def _node_by_key(self, g, gid, nid):
        """SQLite 后端按自增 id；Neo4j 后端按 Neo4j 内部 id"""
        if g["db_type"] == "neo4j":
            cfg = self._gcfg(g)
            storage.neo4j_exec(cfg, "MATCH (n:Graph_%d) WHERE id(n)=$id DETACH DELETE n" % gid, {"id": int(nid)})
        else:
            storage.run("DELETE FROM tb_graph_edge WHERE graph_id=? AND (source_id=? OR target_id=?)", (gid, nid, nid))
            storage.run("DELETE FROM tb_graph_node WHERE graph_id=? AND id=?", (gid, nid))

    # ===== 图谱（数据库概念） =====
    def graph_list(self):
        gs = storage.rows("SELECT * FROM tb_graph ORDER BY id")
        for g in gs:
            g["nodeCount"] = storage.one("SELECT COUNT(*) c FROM tb_graph_node WHERE graph_id=?", (g["id"],))["c"]
            g["versionCount"] = storage.one("SELECT COUNT(*) c FROM tb_graph_version WHERE graph_id=?", (g["id"],))["c"]
            if g["db_type"] == "neo4j":
                g["dbOk"] = storage.neo4j_ping(self._gcfg(g))
        return gs

    def graph_create(self, b):
        if not b.name.strip():
            raise HTTPException(400, "名称不能为空")
        if b.db_type == "neo4j":
            if not storage.neo4j_ping(self._gcfg(b.model_dump())):
                raise HTTPException(400, "Neo4j 连接失败，请检查地址/用户/密码（默认 http://localhost:7474）")
        gid = storage.run("INSERT INTO tb_graph(name, db_type, db_config, description) VALUES(?,?,?,?)",
                          (b.name.strip(), b.db_type, b.db_config, b.description))
        storage.save_version(gid, "create_graph", "创建图谱")
        return storage.one("SELECT * FROM tb_graph WHERE id=?", (gid,))

    def graph_update(self, gid, b):
        self._get_graph(gid)
        storage.run("UPDATE tb_graph SET name=?, db_type=?, db_config=?, description=? WHERE id=?",
                    (b.name.strip(), b.db_type, b.db_config, b.description, gid))
        return storage.one("SELECT * FROM tb_graph WHERE id=?", (gid,))

    def graph_delete(self, gid):
        g = self._get_graph(gid)
        if g["db_type"] == "neo4j":
            try:
                storage.neo4j_exec(self._gcfg(g), "MATCH (n:Graph_%d) DETACH DELETE n" % gid)
            except Exception as e:
                raise HTTPException(400, f"Neo4j 清理失败：{e}")
        for t in ("tb_graph_version", "tb_graph_edge", "tb_graph_node", "tb_graph_entity", "tb_graph"):
            storage.run(f"DELETE FROM {t} WHERE graph_id=?" if t != "tb_graph" else "DELETE FROM tb_graph WHERE id=?",
                        (gid,) if t != "tb_graph" else (gid,))

    # ===== 实体类型 =====
    def entity_list(self, gid):
        self._get_graph(gid)
        return storage.rows("SELECT * FROM tb_graph_entity WHERE graph_id=? ORDER BY id", (gid,))

    def entity_create(self, gid, b):
        self._get_graph(gid)
        if not b.name.strip():
            raise HTTPException(400, "实体类型名不能为空")
        eid = storage.run("INSERT INTO tb_graph_entity(graph_id, name, props_schema) VALUES(?,?,?)",
                          (gid, b.name.strip(), b.props_schema or "[]"))
        storage.save_version(gid, "create_entity", f"新增实体类型 {b.name}")
        return storage.one("SELECT * FROM tb_graph_entity WHERE id=?", (eid,))

    def entity_update(self, gid, eid, b):
        self._get_graph(gid)
        storage.run("UPDATE tb_graph_entity SET name=?, props_schema=? WHERE id=? AND graph_id=?",
                    (b.name.strip(), b.props_schema or "[]", eid, gid))
        storage.save_version(gid, "update_entity", f"更新实体类型 {b.name}")
        return storage.one("SELECT * FROM tb_graph_entity WHERE id=?", (eid,))

    def entity_delete(self, gid, eid):
        self._get_graph(gid)
        storage.run("DELETE FROM tb_graph_entity WHERE id=? AND graph_id=?", (eid, gid))
        storage.save_version(gid, "delete_entity", "删除实体类型")

    # ===== 节点 & 属性 =====
    def node_list(self, gid):
        g = self._get_graph(gid)
        backend = g["db_type"]
        nodes = self._neo_nodes(g, gid) if backend == "neo4j" else \
            storage.rows("SELECT * FROM tb_graph_node WHERE graph_id=? ORDER BY id", (gid,))
        entities = storage.rows("SELECT * FROM tb_graph_entity WHERE graph_id=?", (gid,))
        return {"nodes": nodes, "entities": entities, "backend": backend}

    def node_create(self, gid, b):
        g = self._get_graph(gid)
        if not b.name.strip():
            raise HTTPException(400, "节点名称不能为空")
        try:
            json.loads(b.props or "{}")
        except Exception:
            raise HTTPException(400, "属性需为合法 JSON")
        if g["db_type"] == "neo4j":
            cfg = self._gcfg(g)
            props = json.loads(b.props or "{}")
            params = {"name": b.name.strip(), "props": json.dumps(props, ensure_ascii=False), "eid": b.entity_id}
            j = storage.neo4j_exec(cfg,
                "CREATE (n:Graph_%d {name:$name, props:$props, entity_id:$eid}) RETURN id(n) AS id" % gid, params)
            nid = j["results"][0]["data"][0]["row"][0]
        else:
            nid = storage.run("INSERT INTO tb_graph_node(graph_id, entity_id, name, props) VALUES(?,?,?,?)",
                              (gid, b.entity_id, b.name.strip(), b.props or "{}"))
        storage.save_version(gid, "create_node", f"新增节点 {b.name}")
        return {"id": nid, "name": b.name}

    def node_update(self, gid, nid, b):
        g = self._get_graph(gid)
        if g["db_type"] == "neo4j":
            cfg = self._gcfg(g)
            storage.neo4j_exec(cfg,
                "MATCH (n:Graph_%d) WHERE id(n)=$id SET n.name=$name, n.props=$props, n.entity_id=$eid" % gid,
                {"id": int(nid), "name": b.name.strip(),
                 "props": json.dumps(json.loads(b.props or "{}"), ensure_ascii=False), "eid": b.entity_id})
        else:
            storage.run("UPDATE tb_graph_node SET entity_id=?, name=?, props=? WHERE id=? AND graph_id=?",
                        (b.entity_id, b.name.strip(), b.props or "{}", nid, gid))
        storage.save_version(gid, "update_node", f"更新节点 {b.name}")
        return {"id": nid}

    def node_delete(self, gid, nid):
        g = self._get_graph(gid)
        self._node_by_key(g, gid, nid)
        storage.save_version(gid, "delete_node", "删除节点")

    # ===== 关系边 =====
    def edge_list(self, gid):
        g = self._get_graph(gid)
        if g["db_type"] == "neo4j":
            es = self._neo_edges(g, gid)
            nm = {n["id"]: n["name"] for n in self._neo_nodes(g, gid)}
        else:
            es = storage.rows("SELECT * FROM tb_graph_edge WHERE graph_id=? ORDER BY id", (gid,))
            nm = {n["id"]: n["name"] for n in storage.rows("SELECT id, name FROM tb_graph_node WHERE graph_id=?", (gid,))}
        for e in es:
            e["sourceName"] = nm.get(e["source_id"], "?")
            e["targetName"] = nm.get(e["target_id"], "?")
        return es

    def edge_create(self, gid, b):
        g = self._get_graph(gid)
        if not b.rel_type.strip():
            raise HTTPException(400, "关系类型不能为空")
        if g["db_type"] == "neo4j":
            cfg = self._gcfg(g)
            storage.neo4j_exec(cfg,
                "MATCH (a:Graph_%d) WHERE id(a)=$s MATCH (b:Graph_%d) WHERE id(b)=$t "
                "CREATE (a)-[r:%s]->(b) RETURN id(a) AS s, id(b) AS t" % (gid, gid, b.rel_type.strip().replace(" ", "_")),
                {"s": int(b.source_id), "t": int(b.target_id)})
            storage.save_version(gid, "create_edge", f"新增关系 {b.rel_type}")
            return {"rel_type": b.rel_type}
        if not storage.one("SELECT id FROM tb_graph_node WHERE id=? AND graph_id=?", (b.source_id, gid)):
            raise HTTPException(400, "起点节点不存在")
        if not storage.one("SELECT id FROM tb_graph_node WHERE id=? AND graph_id=?", (b.target_id, gid)):
            raise HTTPException(400, "终点节点不存在")
        eid = storage.run("INSERT INTO tb_graph_edge(graph_id, source_id, target_id, rel_type, props) VALUES(?,?,?,?,?)",
                          (gid, b.source_id, b.target_id, b.rel_type.strip(), b.props or "{}"))
        storage.save_version(gid, "create_edge", f"新增关系 {b.rel_type}")
        e = storage.one("SELECT * FROM tb_graph_edge WHERE id=?", (eid,))
        e["sourceName"] = (storage.one("SELECT name FROM tb_graph_node WHERE id=?", (b.source_id,)) or {}).get("name", "?")
        e["targetName"] = (storage.one("SELECT name FROM tb_graph_node WHERE id=?", (b.target_id,)) or {}).get("name", "?")
        return e

    def edge_update(self, gid, eid, b):
        g = self._get_graph(gid)
        if g["db_type"] == "neo4j":
            raise HTTPException(400, "Neo4j 后端关系类型修改请删除后重建")
        storage.run("UPDATE tb_graph_edge SET source_id=?, target_id=?, rel_type=? WHERE id=? AND graph_id=?",
                    (b.source_id, b.target_id, b.rel_type.strip(), eid, gid))
        storage.save_version(gid, "update_edge", f"更新关系 {b.rel_type}")
        return storage.one("SELECT * FROM tb_graph_edge WHERE id=?", (eid,))

    def edge_delete(self, gid, eid):
        g = self._get_graph(gid)
        if g["db_type"] == "neo4j":
            raise HTTPException(400, "Neo4j 后端关系删除请按节点重建或使用版本恢复")
        storage.run("DELETE FROM tb_graph_edge WHERE id=? AND graph_id=?", (eid, gid))
        storage.save_version(gid, "delete_edge", "删除关系")

    # ===== 邻域 =====
    def neighborhood(self, gid, nid, depth=1):
        g = self._get_graph(gid)
        if g["db_type"] == "neo4j":
            cfg = self._gcfg(g)
            storage.neo4j_exec(cfg,
                "MATCH path=(n:Graph_%d)-[*1..%d]-(m:Graph_%d) WHERE id(n)=$id RETURN n, m, relationships(path) AS rels"
                % (gid, max(1, depth), gid), {"id": int(nid)})
            return {"nodes": self._neo_nodes(g, gid), "edges": self._neo_edges(g, gid), "backend": "neo4j"}
        front, seen, edges_all = {nid}, {nid}, storage.rows("SELECT * FROM tb_graph_edge WHERE graph_id=?", (gid,))
        for _ in range(max(1, depth)):
            nxt = set()
            for e in edges_all:
                if e["source_id"] in front:
                    nxt.add(e["target_id"])
                if e["target_id"] in front:
                    nxt.add(e["source_id"])
            seen |= nxt
            front = nxt - front
        nodes = storage.rows("SELECT * FROM tb_graph_node WHERE graph_id=? AND id IN (%s)" % ",".join(map(str, seen)), (gid,))
        es = [e for e in edges_all if e["source_id"] in seen and e["target_id"] in seen]
        return {"nodes": nodes, "edges": es, "backend": "sqlite"}

    # ===== 版本 =====
    def version_list(self, gid):
        self._get_graph(gid)
        return storage.rows("SELECT id, graph_id, version_no, op, note, created_at FROM tb_graph_version "
                            "WHERE graph_id=? ORDER BY version_no DESC", (gid,))

    def version_detail(self, gid, no):
        self._get_graph(gid)
        v = storage.one("SELECT * FROM tb_graph_version WHERE graph_id=? AND version_no=?", (gid, no))
        if not v:
            raise HTTPException(404, "版本不存在")
        return {k: (json.loads(v[k]) if k == "snapshot" else v[k]) for k in
                ("id", "graph_id", "version_no", "op", "note", "created_at", "snapshot")}

    def version_restore(self, gid, no):
        """恢复：将指定版本快照写回当前数据（当前态先自动存一版再覆盖）"""
        self._get_graph(gid)
        v = storage.one("SELECT * FROM tb_graph_version WHERE graph_id=? AND version_no=?", (gid, no))
        if not v:
            raise HTTPException(404, "版本不存在")
        snap = json.loads(v["snapshot"])
        storage.run("DELETE FROM tb_graph_edge WHERE graph_id=?", (gid,))
        storage.run("DELETE FROM tb_graph_node WHERE graph_id=?", (gid,))
        storage.run("DELETE FROM tb_graph_entity WHERE graph_id=?", (gid,))
        for e in snap.get("entities", []):
            storage.run("INSERT INTO tb_graph_entity(id, graph_id, name, props_schema, created_at) VALUES(?,?,?,?,?)",
                        (e["id"], gid, e["name"], e.get("props_schema", "[]"), e.get("created_at")))
        for n in snap.get("nodes", []):
            storage.run("INSERT INTO tb_graph_node(id, graph_id, entity_id, name, props, created_at) VALUES(?,?,?,?,?,?)",
                        (n["id"], gid, n.get("entity_id", 0), n["name"], n.get("props", "{}"), n.get("created_at")))
        for e in snap.get("edges", []):
            storage.run("INSERT INTO tb_graph_edge(id, graph_id, source_id, target_id, rel_type, props, created_at) VALUES(?,?,?,?,?,?,?)",
                        (e["id"], gid, e["source_id"], e["target_id"], e["rel_type"], e.get("props", "{}"), e.get("created_at")))
        storage.save_version(gid, "restore", f"恢复到 v{no}")
