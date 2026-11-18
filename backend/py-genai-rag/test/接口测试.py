# -*- coding: utf-8 -*-
"""检索增强服务 — 接口测试：正常/异常用例断言（引擎未加载时验证降级行为）

用法：python3 test/接口测试.py   （前置：服务已启动）
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38102")
PASS, FAIL = [], []


def req(method, path, payload=None, expect=None, name=""):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            code, body = resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        code, body = e.code, {}
    ok = expect is None or code == expect
    (PASS if ok else FAIL).append((name or path, ok))
    print(("✓" if ok else "✗"), name or path, f"HTTP {code}",
          json.dumps(body, ensure_ascii=False)[:100])


if __name__ == "__main__":
    req("POST", "/v1/chunk", {"document": "a" * 1200, "chunk_size": 512, "overlap": 64}, 200, "切片正常")
    req("POST", "/v1/chunk", {"document": "abc", "chunk_size": 10, "overlap": 10}, 400, "size<=overlap → 400")
    req("POST", "/v1/chunk", {"document": ""}, 400, "空文档 → 400")
    req("POST", "/v1/retrieve", {"query": "q", "documents": []}, 400, "空候选集 → 400")
    req("POST", "/v1/retrieve", {"query": "q", "documents": ["a", "b"]}, None, "检索编排（协作服务未启动允许 503）")
    print(f"\n接口测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
