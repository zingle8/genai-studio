"""重排序服务配置（迁移自 ai-infer/py_reranker，端口 38104）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-rag-reranker"
    service_name: str = "重排序服务（BGE-Reranker-v2-M3）"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")

    # ===== 推理配置（env: RERANK_*；来源 ai-infer/py_reranker/rerank_config.py）=====
    model_name: str = "bge-reranker-v2-m3"
    model_dir: str = os.environ.get("RERANK_MODEL_DIR", "models/BAAI/bge-reranker-v2-m3")
    device: str = os.environ.get("RERANK_DEVICE", "auto")  # auto / cpu / cuda / mps
    max_documents: int = 500
    max_length: int = 512
    default_normalize: bool = True
    default_batch_size: int = 32


settings = Settings()
