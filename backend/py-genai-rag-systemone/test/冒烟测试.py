# -*- coding: utf-8 -*-
"""SystemOne 判断模型服务（laya + nanojev） — 冒烟测试：/health、/v1/models、接口索引连通性

用法：python3 test/冒烟测试.py   （前置：服务已启动；BASE_URL 可覆盖默认地址）
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38109")
PASS, FAIL = [], []


def get(path, expect=200):
    try:
        with urllib.request.urlopen(BASE + path, timeout=5) as r:
            body = json.loads(r.read())
            ok = r.status == expect
    except urllib.error.HTTPError as e:
        body, ok = {}, e.code == expect
    (PASS if ok else FAIL).append((path, ok))
    print(("✓" if ok else "✗"), path, json.dumps(body, ensure_ascii=False)[:120])


if __name__ == "__main__":
    get("/health")
    get("/v1/models")
    get("/")
    print(f"\n冒烟测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
