"""GenAI Studio 网关平台接入 SDK（Python 版，对齐 jv-api-gateway-client-starter 能力）"""
from .client import GatewayClient, GenaiGatewayClient
from .config import GatewayClientConfig
from .trace import install_fastapi_trace

__all__ = ["GatewayClient", "GenaiGatewayClient", "GatewayClientConfig", "install_fastapi_trace"]
__version__ = "0.2.0"
