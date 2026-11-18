"""推理服务入口（Application 装配）

定位：本地普通生成模型的加载与推理执行器。
统一链路：调用方 → jv-genai-router(38100，按 model_info 配置动态转发) → 本服务本地推理。
本地模型未配置/未加载时服务降级启动（/health 报 ready=false），请求返回 503。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.gateway_report import gateway_report
from app.config import settings
from app.engine import InferEngine
from app.service import InferService


def create_app() -> FastAPI:
    engine = InferEngine()
    service = InferService(engine)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        engine.load()  # 未配置本地模型时降级启动，请求返回 503
        yield
        gateway_report.stop()

    from app.controller.chat_controller import create_routers
    app = FastAPI(title="GenAI Studio - 推理服务（本地模型执行器）",
                  version="0.2.0", lifespan=lifespan)
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service))

    @app.get("/health")
    async def health():
        d = engine.describe()
        return {"service": settings.service_id, "status": "ok" if d["ready"] else "degraded",
                "mode": d["mode"], "ready": d["ready"], "device": d["device"],
                "load_error": d["load_error"]}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "role": "本地普通生成模型加载与推理执行器（统一转发由 jv-genai-router 负责）",
                "packages": ["controller", "service", "engine", "mapper", "dto",
                             "config", "common"],
                "routes": ["/health", "/v1/chat/completions", "/chat/completions",
                           "/v1/models", "/v1/config"]}

    return app


app = create_app()
