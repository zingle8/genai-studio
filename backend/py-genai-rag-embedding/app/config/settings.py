"""向量服务配置（迁移自 ai-infer/py_embedding，端口 38103）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-rag-embedding"
    service_name: str = "向量生成服务（BGE-M3）"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")

    # ===== 推理配置（env: EMBEDDING_*；来源 ai-infer/py_embedding/embedding_config.py）=====
    model_name: str = "bge-m3"
    model_dir: str = os.environ.get("EMBEDDING_MODEL_DIR", "models/BAAI/bge-m3")
    device: str = os.environ.get("EMBEDDING_DEVICE", "auto")  # auto / cpu / cuda / mps
    dim: int = 1024
    max_length: int = 8192
    pooling_method: str = "cls"
    default_batch_size: int = 32
    # 简化版攒批参数（完整调度器见 ai-infer embedding_batch_scheduler.py，后续接入）
    max_batch_items: int = 64


settings = Settings()
