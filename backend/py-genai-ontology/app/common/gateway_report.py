"""网关平台接入适配层：统一走 py-genai-apigateway-client-sdk（注册/心跳/指标/请求采集）

SDK 能力对齐 Java jv-api-gateway-client-starter：服务注册+心跳+优雅下线、主机指标采集、
调用日志批量上报、FastAPI 请求采集中间件、服务发现查询。
协议端点：http://127.0.0.1:28090/api（/discovery/services/*、/discovery/metrics/batch、/trace/logs/batch）
"""
import logging
import sys
from pathlib import Path


def _add_sdk_path() -> None:
    here = Path(__file__).resolve()
    for parent in here.parents:
        sdk = parent / "py-genai-apigateway-client-sdk"
        if sdk.exists() and str(sdk) not in sys.path:
            sys.path.insert(0, str(sdk))
            return


_add_sdk_path()

from genai_apigateway_sdk import GatewayClient  # noqa: E402

logger = logging.getLogger(__name__)

MODULE_PORT = 38105  # 本服务端口（注册信息）


class GatewayReport:
    """SDK 适配：init=注册+心跳+指标+采集启动；install=请求采集中间件；report=业务日志；stop=优雅下线"""

    def __init__(self) -> None:
        self._client: GatewayClient | None = None
        self._app = None

    def init(self, settings) -> None:
        if self._client:
            return
        self._client = GatewayClient(
            service_id=settings.service_id,
            service_name=getattr(settings, "service_name", settings.service_id),
            port=MODULE_PORT,
            server_addr=getattr(settings, "gateway_server_addr", "") or settings.gateway_report_url,
            client_token=getattr(settings, "gateway_client_token", ""),
        )
        self._client.start()
        logger.info("网关平台接入完成: %s -> %s", settings.service_id, self._client.config.server_addr)
        if self._app is not None:
            self._client.install_fastapi(self._app)
            logger.info("请求采集中间件已挂载")

    def install(self, app) -> None:
        """记录 FastAPI 实例并挂载请求采集中间件（init 前调用则延迟到 init 时挂载）"""
        self._app = app
        if self._client is not None:
            self._client.install_fastapi(app)

    async def report(self, payload: dict) -> None:
        """上报一条业务日志/埋点（异步签名兼容旧调用）"""
        if self._client:
            self._client.record_log(payload)

    def stop(self) -> None:
        """优雅下线：冲刷日志队列 + 注销注册"""
        if self._client:
            self._client.stop()
            self._client = None


gateway_report = GatewayReport()
