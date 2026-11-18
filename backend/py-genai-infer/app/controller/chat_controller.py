"""推理服务路由（OpenAI 兼容；经 jv-genai-router 转入，模型不存在/未加载 → 503）"""
from fastapi import APIRouter, HTTPException

from app.common.exceptions import ModelNotLoadedError
from app.dto import ChatRequest


def create_routers(service):
    router = APIRouter()

    @router.post("/v1/chat/completions")
    async def chat_completions(req: ChatRequest):
        if not req.messages:
            raise HTTPException(400, "messages 不能为空")
        try:
            return await service.chat(req)
        except ModelNotLoadedError as e:
            raise HTTPException(503, str(e))

    @router.post("/chat/completions")
    async def chat_completions_alias(req: ChatRequest):
        """兼容无 /v1 前缀的调用（与 jv-genai-router 转发路径对齐）"""
        return await chat_completions(req)

    @router.get("/v1/models")
    async def list_models():
        d = service.engine.describe()
        return {"object": "list", "data": [{"id": "local-infer", "object": "model",
                                            "mode": d["mode"], "ready": d["ready"]}]}

    @router.get("/v1/config")
    async def config():
        return service.engine.describe()

    return router
