"""SystemOne 判断模型服务入口（Application 装配）

分层：controller(接口) / service(业务) / engine(模型加载) / dto / config / common
迁移自 ai-infer/py_laya_mlx 与 py_nano_jev 的 application.py，统一挂载到 38109。
暂不要求跑通：依赖缺失时服务可启动，/health 报告各引擎 ready 状态。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.gateway_report import gateway_report
from app.config import settings
from app.engine import LayaEngine, NanoJevEngine
from app.service import SystemOneService


def create_app() -> FastAPI:
    laya = LayaEngine()
    nanojev = NanoJevEngine()
    service = SystemOneService(laya, nanojev)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        nanojev.load()  # torch 侧：权重在 ../py-genai-infer/local_models/NanoJev
        laya.load()     # MLX 侧：依赖 laya-mlx，缺失自动降级
        yield
        gateway_report.stop()

    from app.controller.laya_controller import create_router as laya_router
    from app.controller.nanojev_controller import create_router as nanojev_router
    from app.controller.common_controller import create_router as common_router

    app = FastAPI(title="GenAI Studio - SystemOne 判断模型服务",
                  version="0.1.0", lifespan=lifespan)
    gateway_report.init(settings)
    gateway_report.install(app)
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(laya_router(service))
    app.include_router(nanojev_router(service))
    app.include_router(common_router(service))
    # RAG 管理（管道配置/索引统计/检索测试）
    from app.controller.rag_admin_controller import create_router as rag_admin_router
    app.include_router(rag_admin_router())

    @app.get("/health")
    async def health():
        l, n = laya.describe(), nanojev.describe()
        return {"service": settings.service_id, "status": "ok",
                "models": {"laya": {"ready": l["ready"], "backend": l["backend"],
                                    "router_loaded": l["router_loaded"],
                                    "load_error": l["load_error"]},
                           "nanojev": {"ready": n["ready"], "backend": n["backend"],
                                       "backbone": n["backbone"],
                                       "load_error": n["load_error"]}}}

    @app.get("/")
    async def index():
        return {"service": settings.service_id, "name": settings.service_name,
                "packages": ["controller", "service", "engine", "dto", "config", "common"],
                "routes": ["/health", "/v1/laya/decide", "/v1/laya/decide/batch",
                           "/v1/laya/route", "/v1/nanojev/decide", "/v1/models", "/v1/config"]}

    return app


app = create_app()
