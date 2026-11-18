"""GenAI Studio 网关平台接入 SDK（Python）— 统一入口

对齐 Java SDK（jv-api-gateway-client-starter）的接入与采集能力：
- ServiceRegistrar：服务注册 + 心跳(30s) + 优雅下线（/discovery/services/*）
- MetricsReporter：主机指标采集上报（60s，/discovery/metrics/batch，需 psutil）
- TraceReporter：调用日志内存队列异步批量上报（/trace/logs/batch）+ FastAPI 一行接入

用法（FastAPI 服务 3 行接入）：
    from genai_apigateway_sdk import GatewayClient

    gw = GatewayClient(service_id="py-genai-infer", service_name="推理服务", port=38101)
    gw.install_fastapi(app)          # 请求采集中间件（可选）
    gw.start()                       # lifespan startup：注册 + 心跳 + 指标 + 采集线程
    ...                              # lifespan shutdown：
    gw.stop()                        # 注销 + 冲刷日志

配置经环境变量：GATEWAY_SERVER_ADDR（默认 http://127.0.0.1:28090/api）、
GATEWAY_CLIENT_TOKEN（默认 dev-gateway-token）。
"""
import logging

import httpx

from .config import GatewayClientConfig
from .registrar import ServiceRegistrar
from .metrics import MetricsReporter
from .trace import TraceReporter, install_fastapi_trace

logger = logging.getLogger(__name__)

__all__ = ["GatewayClient", "GatewayClientConfig", "GenaiGatewayClient", "install_fastapi_trace"]


class GatewayClient:
    """网关平台接入统一入口（注册/心跳/指标/采集 一站式管理）"""

    def __init__(self, service_id: str, service_name: str = "", port: int = 0,
                 server_addr: str = "", client_token: str = "", enabled: bool = True) -> None:
        self.config = GatewayClientConfig(
            enabled=enabled,
            service_id=service_id,
            service_name=service_name or service_id,
            port=port,
        )
        if server_addr:
            self.config.server_addr = server_addr.rstrip("/")
        if client_token:
            self.config.client_token = client_token
        self._registrar = ServiceRegistrar(self.config)
        self._metrics = MetricsReporter(self.config)
        self._trace = TraceReporter(self.config)
        self._started = False

    def install_fastapi(self, app) -> None:
        """挂载 FastAPI 请求采集中间件"""
        install_fastapi_trace(app, self._trace)

    def record_log(self, payload: dict) -> None:
        """业务代码主动上报一条日志/埋点（如模型调用耗时）"""
        self._trace.record(payload)

    def discover(self, keyword: str = "", size: int = 50) -> dict:
        """服务发现：查询网关注册中心服务列表（serviceId/ip/port/status）"""
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                resp = client.get(f"{self.config.server_addr}/discovery/services",
                                  params={"keyword": keyword, "size": size},
                                  headers=self.config.headers())
                return resp.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("服务发现查询失败: %s", exc)
            return {}

    def start(self) -> None:
        if self._started:
            return
        self._registrar.start()
        self._metrics.start()
        self._trace.start()
        self._started = True

    def stop(self) -> None:
        if not self._started:
            return
        self._trace.stop()      # 先冲刷日志
        self._metrics.stop()
        self._registrar.stop()  # 最后注销
        self._started = False


class GenaiGatewayClient(GatewayClient):
    """兼容旧接口（v0.1 report_log 语义，内部转走批量采集通道）"""

    def __init__(self, report_url: str = "", app_id: str = "app-genai-studio",
                 app_name: str = "genai-studio管理平台", service_id: str = "",
                 service_name: str = "", timeout: float = 3.0, **kw) -> None:
        super().__init__(service_id=service_id, service_name=service_name or service_id, **kw)

    async def report_log(self, payload: dict) -> None:
        """上报一条日志/埋点（异步签名兼容旧调用）"""
        self.record_log(payload)
