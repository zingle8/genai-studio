"""SystemOne 判断模型服务配置（端口 38109）

systemone = 判断模型集合（System One / Judge 类）：
- laya    ：迁移自 ai-infer/py_laya_mlx（MLX 后端，laya-mlx Agent/Router）
- nanojev ：迁移自 ai-infer/py_nano_jev（torch 后端，Qwen3-0.6B + set-attention，权重已在 ../py-genai-infer/local_models/NanoJev）
题型统一支持：choice（单选）/ score（2-10 档打分）/ boolean（noul，判断题）
"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-rag-systemone"
    service_name: str = "SystemOne 判断模型服务（laya + nanojev）"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")

    # ===== laya（MLX 侧，env: LAYA_*；来源 ai-infer/py_laya_mlx/laya_config.py）=====
    laya_model_dir: str = os.environ.get("LAYA_MODEL", "models/laya-multilingual-mlx")
    laya_english_model_dir: str = os.environ.get("LAYA_MODEL_EN", "models/laya-mlx")
    laya_dtype: str = "float16"
    laya_router: bool = True
    laya_max_questions: int = 24
    laya_max_batch_items: int = 32

    # ===== nanojev（torch 侧，env: NANOJEV_*；来源 ai-infer/py_nano_jev/nano_jev_config.py）=====
    nanojev_model_dir: str = os.environ.get(
        "NANOJEV_MODEL_DIR", "../py-genai-infer/local_models/NanoJev")
    nanojev_checkpoint: str = os.environ.get("NANOJEV_CHECKPOINT", "best.safetensors")
    nanojev_device: str = os.environ.get("NANOJEV_DEVICE", "auto")
    nanojev_autocast_dtype: str = "bfloat16"
    nanojev_max_length: int = 512
    nanojev_max_states: int = 32
    nanojev_max_questions: int = 64
    nanojev_max_candidates: int = 255


settings = Settings()
