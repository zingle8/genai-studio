"""laya 判断接口（协议同 ai-infer/py_laya_mlx）"""
from fastapi import APIRouter, HTTPException

from app.common.exceptions import ModelUnavailable
from app.dto import LayaBatchRequest, LayaRequest


def create_router(service):
    router = APIRouter()

    @router.post("/v1/laya/decide")
    async def laya_decide(req: LayaRequest):
        try:
            return service.laya_decide(req)
        except ModelUnavailable as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))

    @router.post("/v1/laya/decide/batch")
    async def laya_decide_batch(req: LayaBatchRequest):
        try:
            return service.laya_decide_batch(req)
        except ModelUnavailable as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))

    @router.post("/v1/laya/route")
    async def laya_route(req: LayaRequest):
        try:
            return service.laya_route(req)
        except ModelUnavailable as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))

    return router
