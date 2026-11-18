"""主机指标采集上报（对齐 Java SDK MetricsReporter：60s 周期 /discovery/metrics/batch）

采集字段对齐 Java payload：hostname/appId/serviceName/osName/cpuCores/cpuUsage/loadAvg/
memTotal/memUsedPct/procRss/threadCount/fdCount/diskTotal/diskUsedPct/netRxBps/netTxBps/netConn。
依赖 psutil（缺失时跳过采集，不影响服务）。
"""
import logging
import platform
import shutil
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


def _collect_psutil() -> Optional[dict]:
    try:
        import psutil
    except ImportError:
        return None
    proc = psutil.Process()
    disk = shutil.disk_usage("/")
    net1 = psutil.net_io_counters()
    time.sleep(0.5)
    net2 = psutil.net_io_counters()
    dt = 0.5
    conns = 0
    try:
        conns = len(psutil.net_connections())
    except Exception:
        pass
    return {
        "osName": platform.system(),
        "cpuCores": psutil.cpu_count(),
        "cpuUsage": round(psutil.cpu_percent(interval=None), 1),
        "loadAvg": round(psutil.getloadavg()[0], 2) if hasattr(psutil, "getloadavg") else 0,
        "memTotalMB": int(psutil.virtual_memory().total / 1024 / 1024),
        "memUsedPct": psutil.virtual_memory().percent,
        "procRssMB": int(proc.memory_info().rss / 1024 / 1024),
        "threadCount": proc.num_threads(),
        "fdCount": proc.num_fds() if hasattr(proc, "num_fds") else 0,
        "diskTotalGB": round(disk.total / 1024 / 1024 / 1024, 1),
        "diskUsedPct": round(disk.used / disk.total * 100, 1),
        "netRxBps": int((net2.bytes_recv - net1.bytes_recv) / dt),
        "netTxBps": int((net2.bytes_sent - net1.bytes_sent) / dt),
        "netConn": conns,
    }


class MetricsReporter:
    def __init__(self, config) -> None:
        self.config = config
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _report_once(self) -> None:
        data = _collect_psutil()
        if data is None:
            self._stop.set()  # 无 psutil：不采集也不报错
            return
        payload = {
            "hostname": self.config.hostname,
            "appId": self.config.app_id,
            "serviceName": self.config.service_id,
            **data,
        }
        try:
            import httpx
            with httpx.Client(timeout=self.config.timeout) as client:
                resp = client.post(self.config.metrics_batch_url,
                                   json=[payload], headers=self.config.headers())
                if resp.status_code >= 400:
                    logger.warning("metrics 上报异常: %s %s", resp.status_code, resp.text[:100])
        except Exception as exc:  # noqa: BLE001
            logger.warning("metrics 上报失败: %s", exc)

    def _loop(self) -> None:
        while not self._stop.wait(1):
            if int(time.time()) % self.config.metrics_interval == 0:
                self._report_once()
                self._stop.wait(self.config.metrics_interval - 2)

    def start(self) -> None:
        if not self.config.enabled:
            return
        self._thread = threading.Thread(target=self._loop, name="gw-metrics", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
