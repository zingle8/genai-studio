"""RAG 编排路由"""
from fastapi import APIRouter, HTTPException

from app.common.exceptions import UpstreamUnavailable
from app.dto import ChunkRequest, RetrieveRequest


def create_routers(service):
    router = APIRouter()

    @router.post("/v1/chunk")
    async def chunk(req: ChunkRequest):
        try:
            return service.chunk(req)
        except ValueError as e:
            raise HTTPException(400, str(e))

    @router.post("/v1/retrieve")
    async def retrieve(req: RetrieveRequest):
        try:
            return await service.retrieve(req)
        except UpstreamUnavailable as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))

    return router
