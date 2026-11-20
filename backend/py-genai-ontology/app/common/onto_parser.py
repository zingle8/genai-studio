# -*- coding: utf-8 -*-
"""本体 DSL 解析（正则简化版）：Turtle 风格 与 YAML 双格式，支持 Class 与 Relation 定义"""
import re

import yaml

# 文本格式一（Turtle）：
# <Person> a :Class ; comment "人员" .
# <worksFor> a :Relation ; domain <Person> ; range <Company> ; cardinality "many" ; nullable false .
# 文本格式二（YAML）：
# classes:
#   - name: Person
#     comment: 人员
# rels:
#   - name: worksFor
#     subj: Person
#     obj: Company
#     cardinality: many
#     nullable: true


def parse_ttl(text):
    """解析为 {classes: [{name, comment}], rels: [{name, subj, obj, cardinality, nullable, comment}]}；解析失败抛 ValueError"""
    classes, rels = [], []
    # 拆语句（按 " ." 结尾）
    body = re.sub(r"@prefix[^\n]*\n", "", text or "")
    body = re.sub(r"#[^\n]*", "", body)
    for stmt in re.split(r"\s*\.\s*(?=\S|$)", body):
        stmt = stmt.strip()
        if not stmt:
            continue
        m = re.match(r"<([^>]+)>\s+a\s*:?(Class|Relation)\s*(.*)$", stmt, re.S)
        if not m:
            raise ValueError(f"无法解析语句：{stmt[:60]}…（格式：<名称> a :Class ; 属性… ）")
        name, kind, rest = m.group(1), m.group(2), m.group(3)
        props = {}
        for pm in re.finditer(r"(\w+)\s+(?:\"([^\"]*)\"|<([^>]*)>|(\S+))", rest):
            k, v_str, v_ref, v_raw = pm.group(1), pm.group(2), pm.group(3), pm.group(4)
            props[k] = v_str if v_str is not None else (v_ref if v_ref is not None else v_raw)
        if kind == "Class":
            classes.append({"name": name, "comment": props.get("comment", "")})
        else:
            if "domain" not in props or "range" not in props:
                raise ValueError(f"关系 {name} 缺少 domain 或 range")
            card = props.get("cardinality", "many")
            if card not in ("one", "many"):
                raise ValueError(f"关系 {name} 的 cardinality 只能是 one 或 many，收到 {card}")
            rels.append({
                "name": name, "subj": props["domain"], "obj": props["range"],
                "cardinality": card,
                "nullable": str(props.get("nullable", "true")).lower() != "false",
                "inherits": props.get("inherits", ""),
                "comment": props.get("comment", ""),
            })
    return {"classes": classes, "rels": rels}


def parse_yaml(text):
    """解析 YAML 为与 parse_ttl 相同结构；解析失败抛 ValueError

    格式：
    classes:
      - name: Person
        comment: 人员
        parent: 组织        # 可选，父类
    rels:
      - name: worksFor
        subj: Person        # 或 domain
        obj: Company        # 或 range
        cardinality: many   # one / many（默认 many）
        nullable: true      # 默认 true
        inherits: ''        # 可选，继承关系名
        comment: ''
    """
    try:
        doc = yaml.safe_load(text or "")
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 语法错误：{str(e).splitlines()[0][:120]}")
    if doc is None:
        return {"classes": [], "rels": []}
    if not isinstance(doc, dict):
        raise ValueError("YAML 顶层必须是映射（classes / rels）")
    classes, rels = [], []
    for c in doc.get("classes") or []:
        if not isinstance(c, dict) or not str(c.get("name", "")).strip():
            raise ValueError("classes 每项需含 name 字段")
        classes.append({"name": str(c["name"]).strip(), "comment": str(c.get("comment") or ""),
                        "parent": str(c.get("parent") or c.get("parentName") or "")})
    for r in doc.get("rels") or []:
        if not isinstance(r, dict) or not str(r.get("name", "")).strip():
            raise ValueError("rels 每项需含 name 字段")
        subj = r.get("subj", r.get("domain"))
        obj = r.get("obj", r.get("range"))
        if not subj or not obj:
            raise ValueError(f"关系 {r['name']} 缺少 subj/obj（或 domain/range）")
        card = str(r.get("cardinality", "many"))
        if card not in ("one", "many"):
            raise ValueError(f"关系 {r['name']} 的 cardinality 只能是 one 或 many，收到 {card}")
        rels.append({
            "name": str(r["name"]).strip(), "subj": str(subj).strip(), "obj": str(obj).strip(),
            "cardinality": card,
            "nullable": r.get("nullable", True) is not False and str(r.get("nullable", "true")).lower() != "false",
            "inherits": str(r.get("inherits") or r.get("inheritsFrom") or ""),
            "comment": str(r.get("comment") or ""),
        })
    return {"classes": classes, "rels": rels}


def to_yaml(oid_data):
    """将本体（类+规则）导出为 YAML 文本"""
    doc = {"classes": [], "rels": []}
    for c in oid_data["classes"]:
        item = {"name": c["name"]}
        if c.get("parent_name"):
            item["parent"] = c["parent_name"]
        if c.get("comment"):
            item["comment"] = c["comment"]
        doc["classes"].append(item)
    for r in oid_data["rels"]:
        item = {"name": r["name"], "subj": r["subj_class"], "obj": r["obj_class"],
                "cardinality": r.get("cardinality", "many"), "nullable": bool(r.get("nullable", 1))}
        if r.get("inherits_from"):
            item["inherits"] = r["inherits_from"]
        if r.get("comment"):
            item["comment"] = r["comment"]
        doc["rels"].append(item)
    return yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False)


def to_ttl(oid_data):
    """将本体（类+规则）导出为 Turtle 文本"""
    lines = ["@prefix : <urn:onto:> .", ""]
    for c in oid_data["classes"]:
        seg = f"<{c['name']}> a :Class"
        if c.get("comment"):
            seg += f' ; comment "{c["comment"]}"'
        lines.append(seg + " .")
    for r in oid_data["rels"]:
        seg = (f"<{r['name']}> a :Relation ; domain <{r['subj_class']}> ; "
               f"range <{r['obj_class']}> ; cardinality \"{r['cardinality']}\" ; nullable {'false' if not r['nullable'] else 'true'}")
        if r.get("inherits_from"):
            seg += f" ; inherits <{r['inherits_from']}>"
        if r.get("comment"):
            seg += f' ; comment "{r["comment"]}"'
        lines.append(seg + " .")
    return "\n".join(lines)
