"""OCR 服务配置（迁移自 app/config.py，Spring 风格分层：config）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-ocr"
    service_name: str = "文字识别服务"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")
    # OCR 业务配置
    upload_dir: str = os.environ.get("OCR_UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    ollama_base: str = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
    db_path: str = os.environ.get("OCR_DB", os.path.join(os.path.dirname(__file__), "..", "..", "ocr.db"))
    default_prompt: str = "识别图片中的全部文字，按原样输出，不要解释。"


settings = Settings()
