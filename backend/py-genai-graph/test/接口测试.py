# -*- coding: utf-8 -*-
"""知识图谱服务（py-genai-graph） — 接口测试：空间/图谱/实体/节点/边/邻域 全链路用例

用法：python3 test/接口测试.py   （前置：服务已启动）
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38107")
PASS, FAIL = [], []


def req(method, path, payload=None, expect=None, name="", pick=None):
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
    if pick and ok and body.get("code") == 0:
        return pick(body)
    return None


if __name__ == "__main__":
    # 空间：创建 → 列表 → 清理
    sid = req("POST", "/api/graphs/spaces", {"name": "测试空间-接口测试", "description": "自动化用例"}, None,
              "创建测试空间", pick=lambda b: b["data"]["id"])
    req("GET", "/api/graphs/spaces", None, 200, "空间列表")
    # 图谱全链路（自建空间 → 图谱 → 实体 → 节点 → 边 → 邻域 → 版本 → 清理）
    gid = None
    if sid:
        gid = req("POST", "/api/graphs", {"name": "测试图谱-接口测试", "space_id": sid, "db_type": "sqlite"}, None,
                  "创建测试图谱", pick=lambda b: b["data"]["id"])
    if gid:
        req("POST", f"/api/graphs/{gid}/entities", {"name": "人物", "props_schema": "[]"}, None, "新增实体类型：人物")
        eid = req("GET", f"/api/graphs/{gid}/entities", None, 200, "实体列表",
                  pick=lambda b: b["data"][0]["id"])
        n1 = req("POST", f"/api/graphs/{gid}/nodes", {"entity_id": eid, "name": "张三", "props": "{}"}, None,
                 "新增节点：张三", pick=lambda b: b["data"]["id"])
        n2 = req("POST", f"/api/graphs/{gid}/nodes", {"entity_id": eid, "name": "李四", "props": "{}"}, None,
                 "新增节点：李四", pick=lambda b: b["data"]["id"])
        if n1 and n2:
            req("POST", f"/api/graphs/{gid}/edges", {"source_id": n1, "target_id": n2, "rel_type": "好友"}, None,
                "新增关系：张三-好友->李四")
            req("GET", f"/api/graphs/{gid}/neighborhood?nid={n1}&depth=1", None, 200, "邻域查询(1层)")
        req("GET", f"/api/graphs/{gid}/nodes", None, 200, "节点列表")
        req("GET", f"/api/graphs/{gid}/edges", None, 200, "关系列表")
        req("GET", f"/api/graphs/{gid}/versions", None, 200, "版本列表")
        req("POST", f"/api/graphs/{gid}/nodes", {"entity_id": eid, "props": "{}"}, 422, "缺节点名 → 422")
        req("DELETE", f"/api/graphs/{gid}", None, None, "删除测试图谱")
    if sid:
        req("DELETE", f"/api/graphs/spaces/{sid}", None, None, "删除测试空间")
    print(f"\n接口测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
