# -*- coding: utf-8 -*-
"""本体知识服务接口层（迁移自 app/main.py 路由）

全部路由返回 {"code": 0, "data": ...}；业务逻辑委托 service 层。
"""
from fastapi import APIRouter

from app.dto.onto_dto import ClassIn, ImportIn, MapIn, OntoIn, RelIn, SpaceIn


def create_routers(service) -> APIRouter:
    router = APIRouter()

    # ========== 审计日志（先于 /api/onto/{oid} 模板注册） ==========
    @router.get("/api/onto/audit")
    async def audit_list(oid: int = 0, limit: int = 200):
        return {"code": 0, "data": service.audit_list(oid or None, limit)}

    # ========== 维度表（领域分类 / 枚举，先于 /api/onto/{oid} 模板注册） ==========
    @router.get("/api/onto/dims")
    async def list_dims(enabled_only: int = 1):
        return {"code": 0, "data": service.dim_list(bool(enabled_only))}

    @router.get("/api/onto/dims/{domain}")
    async def list_dim_items(domain: str, enabled_only: int = 1):
        return {"code": 0, "data": service.dim_items(domain, bool(enabled_only))}

    # ========== 本体空间（先于 /api/onto/{oid} 模板注册） ==========
    @router.get("/api/onto/spaces")
    async def list_space():
        return {"code": 0, "data": service.space_list()}

    @router.post("/api/onto/spaces")
    async def create_space(body: SpaceIn):
        return {"code": 0, "data": service.space_create(body)}

    @router.delete("/api/onto/spaces/{sid}")
    async def delete_space(sid: int):
        service.space_delete(sid)
        return {"code": 0}

    # ========== 本体 CRUD ==========
    @router.get("/api/onto/ontologies")
    async def list_onto():
        return {"code": 0, "data": service.onto_list()}

    @router.post("/api/onto/ontologies")
    async def create_onto(body: OntoIn):
        return {"code": 0, "data": service.onto_create(body)}

    @router.put("/api/onto/ontologies/{oid}")
    async def update_onto(oid: int, body: OntoIn):
        service.onto_update(oid, body)
        return {"code": 0}

    @router.delete("/api/onto/ontologies/{oid}")
    async def delete_onto(oid: int):
        service.onto_delete(oid)
        return {"code": 0}

    @router.get("/api/onto/{oid}/full")
    async def onto_full(oid: int):
        return {"code": 0, "data": service.onto_full(oid)}

    # ========== 类 / 关系规则 / 映射 CRUD ==========
    @router.post("/api/onto/classes")
    async def add_class(body: ClassIn):
        service.class_add(body)
        return {"code": 0}

    @router.put("/api/onto/classes/{cid}")
    async def update_class(cid: int, body: ClassIn):
        service.class_update(cid, body)
        return {"code": 0}

    @router.delete("/api/onto/classes/{cid}")
    async def del_class(cid: int):
        service.class_delete(cid)
        return {"code": 0}

    @router.post("/api/onto/rels")
    async def add_rel(body: RelIn):
        service.rel_add(body)
        return {"code": 0}

    @router.put("/api/onto/rels/{rid}")
    async def update_rel(rid: int, body: RelIn):
        service.rel_update(rid, body)
        return {"code": 0}

    @router.delete("/api/onto/rels/{rid}")
    async def del_rel(rid: int):
        service.rel_delete(rid)
        return {"code": 0}

    @router.post("/api/onto/mappings")
    async def add_map(body: MapIn):
        service.map_add(body)
        return {"code": 0}

    @router.delete("/api/onto/mappings/{mid}")
    async def del_map(mid: int):
        service.map_delete(mid)
        return {"code": 0}

    # ========== 导入 / 导出 / 一致性检查（Turtle 与 YAML 双格式） ==========
    @router.post("/api/onto/import")
    async def import_onto(body: ImportIn):
        return {"code": 0, "data": service.import_onto(body)}

    @router.get("/api/onto/{oid}/export")
    async def export_onto(oid: int, format: str = "ttl"):
        return {"code": 0, "data": service.export_onto(oid, format)}

    @router.get("/api/onto/{oid}/check")
    async def check(oid: int):
        return {"code": 0, "data": service.check(oid)}

    # ========== 版本快照 ==========
    @router.get("/api/onto/{oid}/versions")
    async def version_list(oid: int):
        return {"code": 0, "data": service.version_list(oid)}

    @router.get("/api/onto/{oid}/versions/{no}")
    async def version_detail(oid: int, no: int):
        return {"code": 0, "data": service.version_detail(oid, no)}

    @router.post("/api/onto/{oid}/versions/{no}/restore")
    async def version_restore(oid: int, no: int):
        return {"code": 0, "data": service.version_restore(oid, no)}

    # ========== 跨模块图谱（本体创建，来源 ontology；知识图谱侧只读展示） ==========
    @router.get("/api/onto/graph-spaces")
    async def graph_spaces():
        return {"code": 0, "data": service.graph_spaces()}

    @router.post("/api/onto/graphs")
    async def graph_create(body: dict):
        return {"code": 0, "data": service.graph_create(body)}

    # ========== 数据源与图数据 ==========
    @router.get("/api/onto/datasources")
    async def datasources():
        return {"code": 0, "data": service.datasources()}

    @router.post("/api/onto/datasources")
    async def add_datasource(body: dict):
        service.datasource_add(body)
        return {"code": 0}

    @router.get("/api/onto/graph-data")
    async def graph_data(ds: int = 1):
        return {"code": 0, "data": service.graph_data(ds)}

    @router.get("/api/onto/{oid}/view-graph")
    async def view_graph(oid: int, ds: int = 1):
        return {"code": 0, "data": service.view_graph(oid, ds)}

    return router
