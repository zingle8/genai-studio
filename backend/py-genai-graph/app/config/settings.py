"""知识图谱服务配置（迁移自 app/config.py）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-graph"
    service_name: str = "知识图谱服务"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")
    # 图谱业务配置
    db_path: str = os.environ.get("GRAPH_DB", os.path.join(os.path.dirname(__file__), "..", "..", "graph.db"))


settings = Settings()
