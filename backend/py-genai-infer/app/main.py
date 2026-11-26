"""推理服务入口（Application 装配）

定位：本地 MLX 模型的加载与推理执行器（mlx_lm 纯文本 / mlx_vlm 多模态）。
统一链路：调用方 → jv-genai-router(38100，按 model_info 配置动态转发) → 本服务本地推理。
模型按 real_name 懒加载，未加载/未注册时返回 503/404。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.gateway_report import gateway_report
from app.config import settings
from app.service import InferService


def create_app() -> FastAPI:
    service = InferService()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        service.shutdown()
        gateway_report.stop()

    from app.controller.chat_controller import create_routers
    app = FastAPI(title="GenAI Studio - 推理服务（本地 MLX 执行器）",
                  version="0.3.0", lifespan=lifespan)
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service))

    @app.get("/health")
    async def health():
        return {"service": settings.service_id, "status": "ok",
                "backend": "mlx", "device": "mlx (Metal)"}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "role": "本地 MLX 模型加载与推理（mlx_lm / mlx_vlm）",
                "routes": ["/health", "/v1/chat/completions", "/chat/completions",
                           "/v1/models", "/v1/config"]}

    return app


app = create_app()
