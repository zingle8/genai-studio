"""重排序服务入口（Application 装配）

分层：controller(接口) / service(业务) / engine(模型加载) / dto / config / common
迁移自 ai-infer/py_reranker/application.py
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.gateway_report import gateway_report
from app.config import settings
from app.engine import RerankEngine
from app.service import RerankService


def create_app() -> FastAPI:
    engine = RerankEngine()
    service = RerankService(engine)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        engine.load()  # 失败不阻塞启动（/health 报告 ready=False）
        yield
        gateway_report.stop()

    from app.controller.rerank_controller import create_routers
    app = FastAPI(title="GenAI Studio - 重排序服务", version="0.1.0", lifespan=lifespan)
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service))

    @app.get("/health")
    async def health():
        d = engine.describe()
        return {"service": settings.service_id, "status": "ok" if d["ready"] else "degraded",
                "model": d["model"], "ready": d["ready"], "device": d["device"],
                "load_error": d["load_error"]}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "packages": ["controller", "service", "engine", "dto", "config", "common"],
                "routes": ["/health", "/v1/rerank", "/v1/models", "/v1/config"]}

    return app


app = create_app()
