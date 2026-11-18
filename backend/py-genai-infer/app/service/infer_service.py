"""推理业务层：只做本地模型的加载与推理（路由收敛后不含转发逻辑）

统一链路：调用方 → jv-genai-router(38100) → 按模型配置转发到本服务 → 本地推理。
本地模型未加载时抛 ModelNotLoadedError（controller 映射 503，由 router 透传给调用方）。
"""
from typing import Any, Dict

from app.common.exceptions import ModelNotLoadedError
from app.engine import InferEngine
from app.mapper import upstream_mapper


class InferService:
    def __init__(self, engine: InferEngine):
        self.engine = engine

    async def chat(self, req) -> Dict[str, Any]:
        out = self.engine.generate_local(req.messages, req.temperature, req.max_tokens)
        return upstream_mapper.wrap_response(req.model, out["content"], out["usage"])
