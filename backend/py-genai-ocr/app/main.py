# -*- coding: utf-8 -*-
"""OCR 识别服务入口（Application 装配，Spring 风格分层）

结构：controller(接口) / service+impl(业务) / mapper(数据) / dto / config / common
接口与 0.1.0 完全兼容：/health /api/ocr/engines /api/ocr/recognize /api/ocr/tasks*
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.gateway_report import gateway_report
from app.config.settings import settings
from app.controller.ocr_controller import create_routers
from app.service.impl.ocr_service_impl import OcrServiceImpl


def create_app() -> FastAPI:
    service = OcrServiceImpl()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        gateway_report.stop()

    app = FastAPI(title="GenAI Studio - OCR 识别服务", version="0.2.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    gateway_report.init(settings)
    gateway_report.install(app)
    app.include_router(create_routers(service))

    @app.get("/health")
    async def health():
        return {"service": settings.service_id, "status": "ok", "engines": service.detect_engines()}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "packages": ["controller", "service", "impl", "mapper", "dto", "config", "common"],
                "routes": ["/health", "/api/ocr/engines", "/api/ocr/recognize",
                           "/api/ocr/tasks", "/api/ocr/tasks/{tid}", "/api/ocr/tasks/{tid}/image"]}

    return app


app = create_app()
