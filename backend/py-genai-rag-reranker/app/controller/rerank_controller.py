"""重排服务路由（对齐 ai-infer/py_reranker 各 controller）"""
from fastapi import APIRouter, HTTPException

from app.dto import RerankRequest
from app.common.exceptions import ModelNotLoadedError


def create_routers(service):
    router = APIRouter()

    @router.post("/v1/rerank")
    async def rerank(req: RerankRequest):
        try:
            return service.rerank(req)
        except ModelNotLoadedError as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))

    @router.get("/v1/models")
    async def list_models():
        d = service.engine.describe()
        return {"object": "list", "data": [
            {"id": d["model"], "object": "model", "ready": d["ready"],
             "max_documents": d["max_documents"], "max_length": d["max_length"]}
        ]}

    @router.get("/v1/models/{model_id}")
    async def get_model(model_id: str):
        d = service.engine.describe()
        if model_id != d["model"]:
            raise HTTPException(404, "未知模型: " + model_id)
        return {"id": model_id, "object": "model", **d}

    @router.get("/v1/config")
    async def config():
        return service.engine.describe()

    return router
