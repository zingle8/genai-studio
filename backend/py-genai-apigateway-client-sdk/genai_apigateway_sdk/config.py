"""网关客户端配置（对齐 Java SDK GatewayClientProperties / zimo.gateway.client.*）"""
import os
import socket
from dataclasses import dataclass


def _local_ip() -> str:
    """本机局域网 IP（UDP connect 技巧，不实际发包）"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@dataclass
class GatewayClientConfig:
    """网关平台接入配置（环境变量可覆盖，命名对齐 Java zimo.gateway.client.*）"""
    enabled: bool = True
    server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")
    app_id: str = "app-genai-studio"
    app_name: str = "genai-studio管理平台"
    service_id: str = ""
    service_name: str = ""
    ip: str = ""
    port: int = 0
    version: str = "0.1.0"
    language: str = "python"
    hostname: str = socket.gethostname()
    heartbeat_interval: int = 30   # 秒，注册成功后周期心跳（失败自动补注册）
    metrics_interval: int = 60     # 秒，主机指标采集周期
    timeout: float = 3.0

    def __post_init__(self) -> None:
        if not self.ip:
            self.ip = _local_ip()

    @property
    def register_url(self) -> str:
        return f"{self.server_addr}/discovery/services/register"

    @property
    def heartbeat_url(self) -> str:
        return f"{self.server_addr}/discovery/services/heartbeat"

    @property
    def deregister_url(self) -> str:
        return f"{self.server_addr}/discovery/services/deregister"

    @property
    def metrics_batch_url(self) -> str:
        return f"{self.server_addr}/discovery/metrics/batch"

    @property
    def trace_batch_url(self) -> str:
        return f"{self.server_addr}/trace/logs/batch"

    def instance_payload(self) -> dict:
        """服务实例注册 payload（对齐 Java ServiceInstanceDTO 字段）"""
        return {
            "appId": self.app_id,
            "appName": self.app_name,
            "serviceId": self.service_id,
            "serviceName": self.service_name,
            "ip": self.ip,
            "hostname": self.hostname,
            "port": self.port,
            "language": self.language,
            "version": self.version,
        }

    def headers(self) -> dict:
        return {"X-Gateway-Client-Token": self.client_token}
