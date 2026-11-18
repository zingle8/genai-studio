"""SystemOne 公共接口：模型列表 / 配置"""
from fastapi import APIRouter


def create_router(service):
    router = APIRouter()

    @router.get("/v1/models")
    async def list_models():
        return service.describe_all()

    @router.get("/v1/config")
    async def config():
        return service.describe_all()

    return router
