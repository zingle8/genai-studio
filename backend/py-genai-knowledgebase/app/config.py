"""服务配置（后续可接入 jv-genai-config 配置中心）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-knowledgebase"
    service_name: str = "知识库管理"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    # 网关日志/埋点上报地址（project_api-gateway 平台接收端，按实际环境修改）
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")


settings = Settings()
