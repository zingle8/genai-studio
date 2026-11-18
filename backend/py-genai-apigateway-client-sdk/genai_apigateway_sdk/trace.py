"""调用日志采集上报（对齐 Java SDK TraceReporter：内存队列 + 后台线程批量 /trace/logs/batch）

含 FastAPI 中间件工厂 install_fastapi_trace()：一行接入请求采集（api/traceId/status/cost/字节数），
traceId 取请求头 traceparent（W3C 格式取第二段），无则本地生成。
"""
import logging
import queue
import threading
import time
import uuid
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

BATCH_SIZE = 20
FLUSH_INTERVAL = 5  # 秒
QUEUE_MAX = 2048


class TraceReporter:
    def __init__(self, config) -> None:
        self.config = config
        self._q: queue.Queue = queue.Queue(maxsize=QUEUE_MAX)
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def record(self, payload: dict) -> None:
        """采集一条调用日志（队列满丢弃最旧，不影响主链路）"""
        body = {
            "appId": self.config.app_id,
            "appName": self.config.app_name,
            "serviceId": self.config.service_id,
            "serviceName": self.config.service_name,
            **payload,
        }
        try:
            self._q.put_nowait(body)
        except queue.Full:
            try:
                self._q.get_nowait()
                self._q.put_nowait(body)
            except Exception:
                pass

    def _flush(self) -> None:
        batch = []
        while True:
            try:
                batch.append(self._q.get(timeout=0.5))
            except queue.Empty:
                pass
            if batch and (len(batch) >= BATCH_SIZE or self._q.empty()):
                try:
                    with httpx.Client(timeout=self.config.timeout) as client:
                        resp = client.post(self.config.trace_batch_url,
                                           json=batch, headers=self.config.headers())
                        if resp.status_code >= 400:
                            logger.warning("trace 上报异常: %s %s", resp.status_code, resp.text[:100])
                except Exception as exc:  # noqa: BLE001
                    logger.warning("trace 上报失败(丢弃 %d 条): %s", len(batch), exc)
                batch = []
            if self._stop.is_set() and self._q.empty():
                break

    def start(self) -> None:
        if not self.config.enabled:
            return
        self._thread = threading.Thread(target=self._flush, name="gw-trace", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)


def install_fastapi_trace(app, reporter: TraceReporter) -> None:
    """FastAPI 一行接入：采集每个 HTTP 请求并上报网关平台（失败不影响业务）"""
    from starlette.middleware.base import BaseHTTPMiddleware

    class _TraceMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            t0 = time.time()
            tp = request.headers.get("traceparent", "")
            trace_id = tp.split("-")[1] if tp.count("-") >= 3 else uuid.uuid4().hex[:32]
            status_code, res_bytes, err_type = 0, 0, ""
            try:
                response = await call_next(request)
                status_code = response.status_code
                clen = response.headers.get("content-length")
                res_bytes = int(clen) if clen and clen.isdigit() else 0
                if status_code >= 500:
                    err_type = "server"
                return response
            except Exception as exc:
                err_type = "exception"
                status_code = 500
                raise
            finally:
                cost_ms = int((time.time() - t0) * 1000)
                try:
                    reporter.record({
                        "traceId": trace_id,
                        "api": request.url.path,
                        "method": request.method,
                        "protocol": "http",
                        "statusCode": status_code,
                        "errType": err_type,
                        "cost": cost_ms,
                        "reqIp": request.client.host if request.client else "",
                    })
                except Exception:
                    pass

    app.add_middleware(_TraceMiddleware)
