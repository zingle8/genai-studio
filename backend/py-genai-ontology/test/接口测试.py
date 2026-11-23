# -*- coding: utf-8 -*-
"""本体知识服务（py-genai-ontology） — 接口测试：空间/本体/类/关系/导入导出 全链路用例

用法：python3 test/接口测试.py   （前置：服务已启动）
"""
import json
import os
import urllib.error
import urllib.request

BASE = os.environ.get("BASE_URL", "http://localhost:38105")
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
    # 空间：创建 → 列表校验 → 清理
    sid = req("POST", "/api/onto/spaces", {"name": "测试空间-接口测试", "comment": "自动化用例"}, None,
              "创建测试空间", pick=lambda b: b["data"]["id"])
    req("GET", "/api/onto/spaces", None, 200, "空间列表")
    if sid:
        req("DELETE", f"/api/onto/spaces/{sid}", None, None, "删除测试空间")
    # 本体：必须归属空间
    req("POST", "/api/onto/ontologies", {"name": "无空间本体", "space_id": 0}, 400, "无空间创建本体 → 400")
    # 本体全链路
    spaces = req("GET", "/api/onto/spaces", None, 200, "取默认空间", pick=lambda b: b["data"][0]["id"])
    oid = None
    if spaces:
        oid = req("POST", "/api/onto/ontologies", {"name": "测试本体-接口测试", "space_id": spaces}, None,
                  "创建测试本体", pick=lambda b: b["data"]["id"])
    if oid:
        req("POST", "/api/onto/classes", {"ontologyId": oid, "name": "部门"}, None, "新增类：部门")
        req("POST", "/api/onto/classes", {"ontologyId": oid, "name": "部门"}, 400, "重复类 → 400")
        req("POST", "/api/onto/rels", {"ontologyId": oid, "name": "属于", "subjClass": "员工",
                                       "objClass": "部门", "cardinality": "many"}, None, "新增关系规则")
        req("POST", "/api/onto/rels", {"ontologyId": oid, "name": "属于", "subjClass": "员工",
                                       "objClass": "部门"}, 400, "重复关系 → 400")
        req("GET", f"/api/onto/{oid}/full", None, 200, "本体全量详情")
        req("GET", f"/api/onto/{oid}/export?format=yaml", None, 200, "YAML 导出")
        req("GET", f"/api/onto/{oid}/export?format=ttl", None, 200, "Turtle 导出")
        req("GET", f"/api/onto/{oid}/export?format=xml", None, 400, "非法导出格式 → 400")
        req("POST", "/api/onto/import", {"ontologyId": oid, "format": "yaml", "text": "classes: []\nrels: []"}, None,
            "YAML 导入（空定义）")
        req("POST", "/api/onto/import", {"ontologyId": oid, "format": "xml", "text": "<x/>"}, 400, "非法导入格式 → 400")
        req("GET", f"/api/onto/{oid}/check", None, 200, "一致性检查")
        vs = req("GET", f"/api/onto/{oid}/versions", None, 200, "版本列表", pick=lambda b: b["data"])
        if vs:
            req("GET", f"/api/onto/{oid}/versions/{vs[-1]['version_no']}", None, 200, "版本详情(含快照)")
            req("POST", f"/api/onto/{oid}/versions/{vs[-1]['version_no']}/restore", None, 200, "恢复版本")
            req("GET", f"/api/onto/{oid}/versions/999", None, 404, "不存在的版本 → 404")
        req("DELETE", f"/api/onto/ontologies/{oid}", None, None, "删除测试本体")
    req("GET", "/api/onto/graph-data", None, 200, "内置示例图数据")
    print(f"\n接口测试：通过 {len(PASS)}，失败 {len(FAIL)}")
    raise SystemExit(1 if FAIL else 0)
