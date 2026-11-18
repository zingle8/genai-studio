"""nanojev 判断接口（协议同 ai-infer/py_nano_jev）"""
from fastapi import APIRouter, HTTPException

from app.common.exceptions import ModelUnavailable
from app.dto import NanoJevRequest


def create_router(service):
    router = APIRouter()

    @router.post("/v1/nanojev/decide")
    async def nanojev_decide(req: NanoJevRequest):
        try:
            return service.nanojev_decide(req)
        except ModelUnavailable as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))

    return router
