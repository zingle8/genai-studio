# -*- coding: utf-8 -*-
"""检索增强服务 — 评估测试：接口结构校验 + 降级行为验证（业务黄金集待模型就绪后补充）

用法：python3 test/评估测试.py   （前置：服务已启动）
结果请同步记录到 docs/评估测试报告.md
"""
import json
import os
import pathlib
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38102")
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
    c, b = get("/health"); check("health 含协作地址", c == 200 and "embedding_url" in b and "reranker_url" in b)
    c, b = get("/"); check("索引含包清单", c == 200 and "packages" in b and "mapper" in b["packages"])
    check("无 engine 包（纯编排）", not (pathlib.Path(__file__).parent.parent / "app" / "engine").exists())
    print(f"\n评估测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
