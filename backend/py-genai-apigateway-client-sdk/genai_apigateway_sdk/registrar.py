"""服务注册 + 心跳 + 优雅下线（对齐 Java SDK ServiceRegistrar 语义）

- start()：立即注册，后台线程按 heartbeat_interval 周期心跳，失败自动补注册
- stop()：注销 /discovery/services/deregister 并停止线程
"""
import atexit
import logging
import threading
import time
from typing import Optional

import httpx

from .config import GatewayClientConfig

logger = logging.getLogger(__name__)


class ServiceRegistrar:
    def __init__(self, config: GatewayClientConfig) -> None:
        self.config = config
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._registered = False

    def _post(self, url: str, payload: dict, method: str = "POST") -> bool:
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                if method == "DELETE":
                    resp = client.request("DELETE", url, json=payload, headers=self.config.headers())
                else:
                    resp = client.post(url, json=payload, headers=self.config.headers())
                ok = resp.status_code < 400
                if not ok:
                    logger.warning("gateway registrar %s -> %s %s", url, resp.status_code, resp.text[:120])
                return ok
        except Exception as exc:  # noqa: BLE001
            logger.warning("gateway registrar %s failed: %s", url, exc)
            return False

    def register(self) -> bool:
        ok = self._post(self.config.register_url, self.config.instance_payload())
        self._registered = ok
        if ok:
            logger.info("网关注册成功: %s (%s:%s)", self.config.service_id, self.config.ip, self.config.port)
        return ok

    def _loop(self) -> None:
        while not self._stop.wait(self.config.heartbeat_interval):
            ok = self._post(self.config.heartbeat_url, self.config.instance_payload())
            if not ok and not self.register():
                logger.warning("心跳与补注册均失败，下轮重试")

    def start(self) -> None:
        if not self.config.enabled:
            return
        self.register()
        self._thread = threading.Thread(target=self._loop, name="gw-registrar", daemon=True)
        self._thread.start()
        atexit.register(self.stop)  # 进程退出优雅下线（对齐 Java DisposableBean）

    def stop(self) -> None:
        if not self.config.enabled:
            return
        self._stop.set()
        if self._registered:
            self._post(self.config.deregister_url, self.config.instance_payload(), method="DELETE")
            self._registered = False
