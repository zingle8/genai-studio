# -*- coding: utf-8 -*-
"""本体知识服务入口（Application 装配，Spring 风格分层）

分层：controller(接口) / service(业务) / mapper(数据) / dto / config / common
能力：本体空间 / 本体 / 类 / 关系规则 / 映射 CRUD、Turtle+YAML 双格式导入导出、
一致性检查、图数据源与本体视图投影。
接口与拆分前完全兼容。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.gateway_report import gateway_report
from app.config.settings import settings
from app.controller.onto_controller import create_routers
from app.mapper import onto_mapper  # 导入即建表 + 存量空间迁移
from app.service import onto_service


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        gateway_report.stop()

    app = FastAPI(title="GenAI Studio - 本体知识服务", version="0.3.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service=onto_service))

    @app.get("/health")
    async def health():
        return {"service": settings.service_id, "status": "ok"}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "packages": ["controller", "service", "mapper", "dto", "config", "common"],
                "routes": ["/health", "/api/onto/spaces", "/api/onto/ontologies",
                           "/api/onto/{oid}/full", "/api/onto/classes*", "/api/onto/rels*",
                           "/api/onto/mappings*", "/api/onto/import", "/api/onto/{oid}/export",
                           "/api/onto/{oid}/check", "/api/onto/datasources", "/api/onto/graph-data",
                           "/api/onto/{oid}/view-graph"]}

    return app


app = create_app()
