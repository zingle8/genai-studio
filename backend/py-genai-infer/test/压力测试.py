# -*- coding: utf-8 -*-
"""推理服务 — 压力测试：并发请求，统计成功率与 P50/P95/P99 延迟

用法：python3 test/压力测试.py [并发数] [每并发请求数] [路径]
默认：并发 8，每并发 10 次，路径 /health
结果请同步记录到 docs/压力测试报告.md
"""
import sys
import threading
import time
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38101")
workers = int(sys.argv[1]) if len(sys.argv) > 1 else 8
per = int(sys.argv[2]) if len(sys.argv) > 2 else 10
path = sys.argv[3] if len(sys.argv) > 3 else "/health"

latencies, errors, lock = [], [], threading.Lock()


def worker():
    for _ in range(per):
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(BASE + path, timeout=15) as r:
                r.read()
            lat = (time.perf_counter() - t0) * 1000
            with lock:
                latencies.append(lat)
        except Exception as e:  # noqa: BLE001
            with lock:
                errors.append(str(e))


if __name__ == "__main__":
    threads = [threading.Thread(target=worker) for _ in range(workers)]
    t0 = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = (time.perf_counter() - t0) * 1000
    n = len(latencies)
    print(f"目标: {BASE}{path}  并发: {workers}  每并发: {per}")
    print(f"总请求: {workers * per}  成功: {n}  失败: {len(errors)}  总耗时: {total:.0f}ms")
    if n:
        s = sorted(latencies)
        q = lambda p: s[min(int(len(s) * p), len(s) - 1)]  # noqa: E731
        print(f"P50={q(.5):.1f}ms  P95={q(.95):.1f}ms  P99={q(.99):.1f}ms  "
              f"吞吐={n / (total / 1000):.1f} req/s")
    if errors:
        print("失败样例:", errors[:3])
