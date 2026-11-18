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

    # ===== 本地推理（HF transformers；local_models/ 下已含 NanoJev 权重供 systemone 复用）=====
    local_model_dir: str = os.environ.get("INFER_MODEL_DIR", "")  # 留空=未配置本地生成模型
    device: str = os.environ.get("INFER_DEVICE", "auto")
    max_new_tokens: int = 512
    temperature: float = 0.7

    # ===== 上游转发（平台模型转发走 jv-genai-router 38100；此处为直连兜底）=====
    upstream_url: str = os.environ.get("INFER_UPSTREAM_URL", "http://localhost:38100")
    upstream_api_key: str = os.environ.get("INFER_UPSTREAM_KEY", "")


settings = Settings()
