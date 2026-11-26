# -*- coding: utf-8 -*-
"""知识图谱服务入口（Application 装配，Spring 风格分层）

结构：controller(接口) / service+impl(业务) / mapper(数据) / dto / config / common
v2：图谱(数据库概念) / 实体类型 / 节点&属性 / 关系 / 版本（自动快照+恢复）
存储后端：postgresql 或 neo4j（图谱配置连接信息，HTTP API 真实读写）
接口与 0.2.0 完全兼容。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.gateway_report import gateway_report
from app.mapper import graph_mapper
from app.config.settings import settings
from app.controller.graph_controller import create_routers
from app.service.impl.graph_service_impl import GraphServiceImpl


def create_app() -> FastAPI:
    service = GraphServiceImpl()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        gateway_report.stop()

    app = FastAPI(title="GenAI Studio - 知识图谱服务", version="0.3.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.add_middleware(graph_mapper.AuditContextMiddleware)
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
                "routes": ["/health", "/api/graphs", "/api/graphs/{gid}/entities",
                           "/api/graphs/{gid}/nodes", "/api/graphs/{gid}/edges",
                           "/api/graphs/{gid}/neighborhood", "/api/graphs/{gid}/versions*"]}

    return app


app = create_app()
