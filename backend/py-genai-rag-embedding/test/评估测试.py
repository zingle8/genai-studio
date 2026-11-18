# -*- coding: utf-8 -*-
"""向量生成服务（BGE-M3） — 评估测试：接口结构校验 + 降级行为验证（业务黄金集待模型就绪后补充）

用法：python3 test/评估测试.py   （前置：服务已启动）
结果请同步记录到 docs/评估测试报告.md
"""
import json
import os
import pathlib
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38103")
PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("✓" if cond else "✗"), name, detail)


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}


if __name__ == "__main__":
    c, b = get("/v1/models"); check("models 含 dim=1024", c == 200 and b["data"][0].get("dim") == 1024)
    c, b = get("/v1/config"); check("config 含 model_dir", c == 200 and "model_dir" in b)
    c, b = get("/health"); check("health 含 load_error 字段", "load_error" in b)
    print(f"\n评估测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
