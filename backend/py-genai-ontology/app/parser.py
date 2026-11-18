# -*- coding: utf-8 -*-
"""Turtle 风格本体 DSL 解析（正则简化版，支持 Class 与 Relation 定义）"""
import re

# 文本格式：
# <Person> a :Class ; comment "人员" .
# <worksFor> a :Relation ; domain <Person> ; range <Company> ; cardinality "many" ; nullable false .


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
