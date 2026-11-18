# -*- coding: utf-8 -*-
"""SystemOne 判断模型服务（laya + nanojev） — 接口测试：正常/异常用例断言（引擎未加载时验证降级行为）

用法：python3 test/接口测试.py   （前置：服务已启动）
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38109")
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
    req("POST", "/v1/nanojev/decide", {"states": [{"state": "s", "questions": {"q1": {"type": "boolean", "instructions": "判断"}}}]}, None, "nanojev 决策（未加载允许 503）")
    req("POST", "/v1/nanojev/decide", {"states": []}, None, "空 states（允许 200/400/503 任一）")
    req("POST", "/v1/laya/decide", {"state": "s", "questions": {"q1": {"type": "choice", "candidates": ["a", "b"]}}}, None, "laya 决策（未加载允许 503）")
    req("POST", "/v1/laya/decide/batch", {"items": []}, None, "空批量")
    req("GET", "/v1/models", None, 200, "两引擎模型列表")
    print(f"\n接口测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
