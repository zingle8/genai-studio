"""推理服务路由（OpenAI 兼容；经 jv-genai-router 转入）"""
import json
import time
import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.common.exceptions import ModelNotLoadedError
from app.dto import ChatRequest


def create_routers(service):
    router = APIRouter()

    @router.post("/v1/chat/completions")
    async def chat_completions(req: ChatRequest):
        if not req.messages:
            raise HTTPException(400, "messages 不能为空")
        try:
            if req.stream:
                async def sse():
                    last_stat = {}
                    async for chunk in service.chat_stream(req):
                        if "_error" in chunk:
                            yield f"data: {json.dumps({'error': chunk['_error']})}\n\n"
                            continue
                        if "_stat" in chunk:
                            last_stat = chunk.pop("_stat")
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                    # 末帧带 usage（router 的 parseUsage 从这里抓 token 计费）
                    yield ("data: " + json.dumps({
                        "id": "chatcmpl-" + uuid.uuid4().hex[:24],
                        "object": "chat.completion.chunk", "created": int(time.time()),
                        "model": req.model,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                        "usage": {"prompt_tokens": last_stat.get("prompt_tokens", 0),
                                  "completion_tokens": last_stat.get("completion_tokens", 0),
                                  "total_tokens": last_stat.get("prompt_tokens", 0) + last_stat.get("completion_tokens", 0)},
                    }) + "\n\n")
                    yield "data: [DONE]\n\n"
                return StreamingResponse(sse(), media_type="text/event-stream",
                                         headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
            return await service.chat(req)
        except KeyError as e:
            raise HTTPException(404, str(e))
        except ModelNotLoadedError as e:
            raise HTTPException(503, str(e))

    @router.post("/chat/completions")
    async def chat_completions_alias(req: ChatRequest):
        """兼容无 /v1 前缀的调用（与 jv-genai-router 转发路径对齐）"""
        return await chat_completions(req)

    @router.get("/v1/models")
    async def list_models():
        from app.model_registry import list_specs
        return {"object": "list", "data": [
            {"id": s.alias, "object": "model", "owned_by": "MLX",
             "capabilities": s.capabilities, "description": s.description}
            for s in list_specs()]}

    @router.get("/v1/config")
    async def config():
        return {"backend": "mlx", "engines": service.manager.describe_all(),
                "concurrency": service.manager.stats()}

    @router.get("/v1/stats")
    async def stats():
        return service.manager.stats()

    return router
