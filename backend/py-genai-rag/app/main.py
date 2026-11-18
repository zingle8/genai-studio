"""检索增强服务入口（Application 装配）

分层：controller(接口) / service(业务) / mapper(外部服务访问) / dto / config / common
py_rag 源项目仅文档无代码，此为按其文档实现的编排层。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.gateway_report import gateway_report
from app.config import settings
from app.service.rag_service import RagService


def create_app() -> FastAPI:
    service = RagService()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        gateway_report.stop()

    from app.controller.rag_controller import create_routers
    app = FastAPI(title="GenAI Studio - 检索增强服务", version="0.1.0", lifespan=lifespan)
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service))

    @app.get("/health")
    async def health():
        return {"service": settings.service_id, "status": "ok",
                "embedding_url": settings.embedding_url,
                "reranker_url": settings.reranker_url}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "packages": ["controller", "service", "mapper", "dto", "config", "common"],
                "routes": ["/health", "/v1/chunk", "/v1/retrieve"]}

    return app


app = create_app()
