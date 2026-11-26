"""推理服务配置（端口 38101）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-infer"
    service_name: str = "推理服务"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")

    # ===== 本地推理（MLX：mlx_lm 纯文本 / mlx_vlm 多模态）=====
    local_model_dir: str = os.environ.get("INFER_MODEL_DIR", "")  # 兼容旧字段（HF transformers）
    local_models_dir: str = os.environ.get("INFER_LOCAL_MODELS_DIR", "")  # mlx-community 根目录；空=默认 local_models/mlx-community
    backend: str = os.environ.get("INFER_BACKEND", "mlx")  # mlx / hf（hf 为旧 transformers 兜底）
    device: str = os.environ.get("INFER_DEVICE", "auto")
    max_new_tokens: int = 512
    temperature: float = 0.7
    # ===== 并发与性能 =====
    max_loaded_models: int = int(os.environ.get("INFER_MAX_LOADED_MODELS", "4"))  # LRU 最大驻留模型数（128GB 内存可全驻留 4 个模型约 55GB）
    max_concurrency_per_model: int = int(os.environ.get("INFER_MAX_CONCURRENCY", "2"))  # 每模型并发推理数
    worker_threads: int = int(os.environ.get("INFER_WORKER_THREADS", "4"))  # 推理线程池大小
    max_global_inflight: int = int(os.environ.get("INFER_MAX_GLOBAL_INFLIGHT", "2"))  # 全局推理闸门：跨模型同时推理上限（>2 会触发 Metal GPU hang）

    # ===== 上游转发（平台模型转发走 jv-genai-router 38100；此处为直连兜底）=====
    upstream_url: str = os.environ.get("INFER_UPSTREAM_URL", "http://localhost:38100")
    upstream_api_key: str = os.environ.get("INFER_UPSTREAM_KEY", "")


settings = Settings()
