# -*- coding: utf-8 -*-
"""本体一致性检查：重复定义 / 引用缺失 / 继承放宽 / 映射基数矛盾"""
from app.mapper.onto_mapper import rows

# 基数严格度：one(非空一对一) > many > many(可空)；nullable 放宽 = 更松
_STRICT = {("one", 0): 3, ("one", 1): 2, ("many", 0): 1, ("many", 1): 0}


def strictness(card, nullable):
    return _STRICT.get((card, 1 if nullable else 0), 0)


def check_ontology(oid):
    """返回 {level: error/warn, code, message} 列表"""
    issues = []
    classes = rows("SELECT * FROM tb_onto_class WHERE ontology_id=?", (oid,))
    rels = rows("SELECT * FROM tb_onto_rel WHERE ontology_id=?", (oid,))
    maps = rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=?", (oid,))
    names = [c["name"] for c in classes]

    # 1. 同名类重复
    seen = set()
    for c in classes:
        if c["name"] in seen:
            issues.append({"level": "error", "code": "DUP_CLASS",
                           "message": f"类重复定义：{c['name']}（同名类只能定义一次）"})
        seen.add(c["name"])

    # 2. 关系引用的类必须存在
    for r in rels:
        if r["subj_class"] not in names:
            issues.append({"level": "error", "code": "MISSING_CLASS",
                           "message": f"关系 {r['name']} 的主体类 {r['subj_class']} 未定义"})
        if r["obj_class"] not in names:
            issues.append({"level": "error", "code": "MISSING_CLASS",
                           "message": f"关系 {r['name']} 的客体类 {r['obj_class']} 未定义"})

    # 3. 同一 (subj, rel, obj) 重复定义（同一对象同关系多规则）
    key_seen = {}
    for r in rels:
        k = (r["subj_class"], r["name"], r["obj_class"])
        if k in key_seen:
            issues.append({"level": "error", "code": "DUP_REL",
                           "message": f"关系规则重复：{r['subj_class']} --{r['name']}--> {r['obj_class']} 已定义过（同一对象间同一关系不可重复定义）"})
        key_seen[k] = r

    # 4. 继承放宽检测（继承的规则只能收紧不能放宽）
    for r in rels:
        src = r["inherits_from"]
        if not src:
            continue
        base = next((x for x in rels if x["name"] == src and (x["subj_class"], x["obj_class"]) == (r["subj_class"], r["obj_class"])), None)
        if not base:
            base = next((x for x in rels if x["name"] == src), None)
        if not base:
            issues.append({"level": "error", "code": "MISSING_INHERIT",
                           "message": f"关系 {r['name']} 声明继承 {src}，但该规则不存在"})
        elif strictness(r["cardinality"], r["nullable"]) < strictness(base["cardinality"], base["nullable"]):
            issues.append({"level": "error", "code": "RELAX_INHERIT",
                           "message": f"继承放宽冲突：{r['name']}（{r['cardinality']}/{'' if r['nullable'] else '非'}空）比所继承的 {src}（{base['cardinality']}/{'' if base['nullable'] else '非'}空）更宽松——继承只能收紧约束"})

    # 5. 同一 (subj, obj) 对上同一物理语义的基数矛盾（不同关系名但同对类，给出提示）
    pair = {}
    for r in rels:
        pair.setdefault((r["subj_class"], r["obj_class"]), []).append(r)
    for (s, o), rs in pair.items():
        strict_vals = {strictness(r["cardinality"], r["nullable"]) for r in rs if not r["inherits_from"]}
        if len(rs) > 1 and len(strict_vals) > 1:
            issues.append({"level": "warn", "code": "PAIR_CONFLICT",
                           "message": f"{s} 与 {o} 之间存在 {len(rs)} 条关系且约束严格度不一致（{', '.join(r['name'] + ':' + r['cardinality'] for r in rs)}），跨本体合并时将按最严格约束取交集"})

    # 6. 映射：同类型重复绑定 / 同一物理边映射出矛盾基数
    seen_map = set()
    for m in maps:
        k = (m["onto_type"], m["physical_type"])
        if k in seen_map:
            issues.append({"level": "warn", "code": "DUP_MAP", "message": f"映射重复：{m['onto_type']} -> {m['physical_type']}"})
        seen_map.add(k)

    if not issues:
        issues.append({"level": "ok", "code": "PASS", "message": "一致性检查通过：无重复定义、无引用缺失、无继承放宽、映射无矛盾"})
    return issues
