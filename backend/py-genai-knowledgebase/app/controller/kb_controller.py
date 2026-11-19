# -*- coding: utf-8 -*-
"""知识库接口层（controller）：路由定义，业务委托 service（create_routers 工厂，风格同 infer）"""
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.dto.kb_dto import KbIn, PingIn, SpaceIn


def create_routers(service):
    router = APIRouter()

    # ===== 选项与连通性 =====
    @router.get("/api/kb/options")
    async def kb_options():
        return {"code": 0, "data": service.options()}

    @router.post("/api/kb/ping")
    async def kb_ping(b: PingIn):
        r = service.ping(b.db_type, b.db_config)
        ok = r["ok"]
        return {"code": 0 if ok else 1, "data": {"ok": ok}, "message": r["message"]}

    # ===== 知识空间 =====
    @router.get("/api/kb/spaces")
    async def space_list():
        return {"code": 0, "data": service.space_list()}

    @router.post("/api/kb/spaces")
    async def space_create(b: SpaceIn):
        return {"code": 0, "data": service.space_create(b)}

    @router.delete("/api/kb/spaces/{sid}")
    async def space_delete(sid: int):
        service.space_delete(sid)
        return {"code": 0, "data": "deleted"}

    # ===== 知识库 =====
    @router.get("/api/kb/list")
    async def kb_list(space_id: int = 0):
        return {"code": 0, "data": service.kb_list(space_id)}

    @router.post("/api/kb")
    async def kb_create(b: KbIn):
        return {"code": 0, "data": service.kb_create(b)}

    @router.put("/api/kb/{kid}")
    async def kb_update(kid: int, b: KbIn):
        return {"code": 0, "data": service.kb_update(kid, b)}

    @router.delete("/api/kb/{kid}")
    async def kb_delete(kid: int):
        service.kb_delete(kid)
        return {"code": 0, "data": "deleted"}

    # ===== 文档 =====
    @router.post("/api/kb/{kid}/docs")
    async def doc_add(kid: int, name: str = Form(...), text: str = Form(""),
                      file: Optional[UploadFile] = File(None)):
        raw = await file.read() if file is not None else None
        return {"code": 0, "data": service.doc_add(kid, name, text, raw)}

    @router.get("/api/kb/{kid}/docs")
    async def doc_list(kid: int):
        return {"code": 0, "data": service.doc_list(kid)}

    @router.get("/api/kb/{kid}/docs/{did}/chunks")
    async def chunk_list(kid: int, did: int):
        return {"code": 0, "data": service.chunk_list(kid, did)}

    @router.delete("/api/kb/{kid}/docs/{did}")
    async def doc_delete(kid: int, did: int):
        service.doc_delete(kid, did)
        return {"code": 0, "data": "deleted"}

    # ===== 检索 =====
    @router.get("/api/kb/{kid}/search")
    async def kb_search(kid: int, q: str, top_k: int = 5):
        if not q.strip():
            raise HTTPException(400, "q 不能为空")
        r = service.search(kid, q, top_k)
        return {"code": 0, "data": r["hits"], "total": len(r["hits"]), "backend": r["backend"]}

    @router.get("/api/kb/{kid}/semantic_search")
    async def kb_semantic_search(kid: int, q: str, top_k: int = 5):
        """语义检索：bge-m3 向量 + 余弦相似度（依赖向量服务 38103）"""
        if not q.strip():
            raise HTTPException(400, "q 不能为空")
        r = service.semantic_search(kid, q, top_k)
        return {"code": 0, "data": r["hits"], "total": len(r["hits"]), "backend": r["backend"]}

    return router
