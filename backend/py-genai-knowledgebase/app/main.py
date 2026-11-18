# -*- coding: utf-8 -*-
"""知识库服务入口（Application 装配，Spring 风格分层）

结构：controller(接口) / service+impl(业务) / mapper(数据) / dto / config / common
v2：知识空间 / 知识库（存储 es|pg|内置 + 类型 + 切分 + embedding/reranker）/ 文档 / 检索路由
接口与 0.2.0 完全兼容。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.gateway_report import gateway_report
from app.config.settings import settings
from app.controller.kb_controller import create_routers
from app.service.impl.kb_service_impl import KbServiceImpl


def create_app() -> FastAPI:
    service = KbServiceImpl()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        gateway_report.stop()

    app = FastAPI(title="GenAI Studio - 知识库服务", version="0.3.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service))

    @app.get("/health")
    async def health():
        return {"service": settings.service_id, "status": "ok"}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "packages": ["controller", "service", "impl", "mapper", "dto", "config", "common"],
                "routes": ["/health", "/api/kb/options", "/api/kb/ping", "/api/kb/spaces*",
                           "/api/kb/list", "/api/kb*", "/api/kb/{kid}/docs*", "/api/kb/{kid}/search"]}

    return app


app = create_app()
