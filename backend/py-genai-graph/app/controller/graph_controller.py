# -*- coding: utf-8 -*-
"""图谱接口层（controller）：路由定义，业务委托 service（create_routers 工厂，风格同 infer）"""
from fastapi import APIRouter, HTTPException

from app.dto.graph_dto import EdgeIn, EntityIn, GraphIn, NodeIn, SpaceIn, VersionIn


def create_routers(service):
    router = APIRouter()

    # ===== 图谱空间（必须在 /api/graphs/{gid} 模板之前注册） =====
    @router.get("/api/graphs/spaces")
    async def space_list():
        return {"code": 0, "data": service.space_list()}

    @router.post("/api/graphs/spaces")
    async def space_create(b: SpaceIn):
        return {"code": 0, "data": service.space_create(b)}

    @router.delete("/api/graphs/spaces/{sid}")
    async def space_delete(sid: int):
        service.space_delete(sid)
        return {"code": 0, "data": "deleted"}

    # ===== 图谱（数据库概念） =====
    @router.get("/api/graphs")
    async def graph_list():
        return {"code": 0, "data": service.graph_list()}

    @router.post("/api/graphs")
    async def graph_create(b: GraphIn):
        return {"code": 0, "data": service.graph_create(b)}

    @router.put("/api/graphs/{gid}")
    async def graph_update(gid: int, b: GraphIn):
        return {"code": 0, "data": service.graph_update(gid, b)}

    @router.delete("/api/graphs/{gid}")
    async def graph_delete(gid: int):
        service.graph_delete(gid)
        return {"code": 0, "data": "deleted"}

    # ===== 实体类型 =====
    @router.get("/api/graphs/{gid}/entities")
    async def entity_list(gid: int):
        return {"code": 0, "data": service.entity_list(gid)}

    @router.post("/api/graphs/{gid}/entities")
    async def entity_create(gid: int, b: EntityIn):
        return {"code": 0, "data": service.entity_create(gid, b)}

    @router.put("/api/graphs/{gid}/entities/{eid}")
    async def entity_update(gid: int, eid: int, b: EntityIn):
        return {"code": 0, "data": service.entity_update(gid, eid, b)}

    @router.delete("/api/graphs/{gid}/entities/{eid}")
    async def entity_delete(gid: int, eid: int):
        service.entity_delete(gid, eid)
        return {"code": 0, "data": "deleted"}

    # ===== 节点 & 属性 =====
    @router.get("/api/graphs/{gid}/nodes")
    async def node_list(gid: int):
        return {"code": 0, "data": service.node_list(gid)}

    @router.post("/api/graphs/{gid}/nodes")
    async def node_create(gid: int, b: NodeIn):
        return {"code": 0, "data": service.node_create(gid, b)}

    @router.put("/api/graphs/{gid}/nodes/{nid}")
    async def node_update(gid: int, nid: int, b: NodeIn):
        return {"code": 0, "data": service.node_update(gid, nid, b)}

    @router.delete("/api/graphs/{gid}/nodes/{nid}")
    async def node_delete(gid: int, nid: int):
        service.node_delete(gid, nid)
        return {"code": 0, "data": "deleted"}

    # ===== 关系边 =====
    @router.get("/api/graphs/{gid}/edges")
    async def edge_list(gid: int):
        return {"code": 0, "data": service.edge_list(gid)}

    @router.post("/api/graphs/{gid}/edges")
    async def edge_create(gid: int, b: EdgeIn):
        return {"code": 0, "data": service.edge_create(gid, b)}

    @router.put("/api/graphs/{gid}/edges/{eid}")
    async def edge_update(gid: int, eid: int, b: EdgeIn):
        return {"code": 0, "data": service.edge_update(gid, eid, b)}

    @router.delete("/api/graphs/{gid}/edges/{eid}")
    async def edge_delete(gid: int, eid: int):
        service.edge_delete(gid, eid)
        return {"code": 0, "data": "deleted"}

    # ===== 邻域（支持多起点节点 + 1~7 级） =====
    @router.get("/api/graphs/{gid}/neighborhood")
    async def neighborhood(gid: int, nid: int = 0, nids: str = "", depth: int = 1):
        ids = [int(x) for x in nids.split(",") if x.strip().isdigit()]
        if nid:
            ids.append(nid)
        if not ids:
            raise HTTPException(400, "请至少选择一个查询节点")
        if depth < 1 or depth > 7:
            raise HTTPException(400, "层数仅支持 1~7 级")
        return {"code": 0, "data": service.neighborhood(gid, ids, depth)}

    # ===== 版本 =====
    @router.get("/api/graphs/{gid}/versions")
    async def version_list(gid: int):
        return {"code": 0, "data": service.version_list(gid)}

    @router.get("/api/graphs/{gid}/versions/{no}")
    async def version_detail(gid: int, no: int):
        return {"code": 0, "data": service.version_detail(gid, no)}

    @router.post("/api/graphs/{gid}/versions/{no}/restore")
    async def version_restore(gid: int, no: int):
        service.version_restore(gid, no)
        return {"code": 0, "data": "restored"}

    return router
