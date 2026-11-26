
# -*- coding: utf-8 -*-
"""本体知识服务存储层（SQLite：本体空间/本体/类/关系规则/映射/数据源）

迁移自 app/storage.py；目录层级对齐 py-genai-rag-reranker 分层结构。
"""
import base64
import sqlite3, json, time, os
from contextvars import ContextVar

DB_PATH = os.environ.get("ONTO_DB", os.path.join(os.path.dirname(__file__), "..", "..", "onto.db"))

# ===== 审计上下文：从请求头 Authorization(JWT) 解析操作人 =====
_operator_ctx = ContextVar("onto_operator", default="system")


def current_operator():
    return _operator_ctx.get()


def _jwt_sub(auth: str) -> str:
    try:
        token = auth.split()[-1]
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        sub = json.loads(base64.urlsafe_b64decode(payload)).get("sub")
        return sub or "system"
    except Exception:
        return "system"


class AuditContextMiddleware:
    """纯 ASGI 中间件：在同一 task 内设置/清理操作人上下文"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode("utf-8", "ignore")
            token = _operator_ctx.set(_jwt_sub(auth))
            try:
                await self.app(scope, receive, send)
            finally:
                _operator_ctx.reset(token)
        else:
            await self.app(scope, receive, send)


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ===== 维度表种子数据：领域分类 + 枚举值（UI 下拉与后端校验共用唯一数据源） =====
DIM_DOMAINS = [
    ("structural",      "结构关系",   "类与类之间的结构关系，保存于 tb_onto_rel.rel_kind", "tb_onto_rel.rel_kind"),
    ("person_relation", "人物关系",   "人物之间的亲属/社会关系，用于家族族谱类本体", "tb_onto_rel.rel_kind"),
    ("belonging",       "所属关系",   "对象归属家族/辈分/组织/地点等的关系", "tb_onto_rel.rel_kind"),
    ("semantic",        "业务语义关系", "关系在业务上的语义分类，用于图展示与检索", "tb_onto_rel.semantic_kind"),
    ("mapping",         "映射关系",   "本体到物理数据的映射类型，保存于 tb_onto_mapping.kind", "tb_onto_mapping.kind"),
    ("event_flow",      "事件流关系", "事件类型之间的时序/因果/触发关系", "tb_onto_event_flow.rel_type"),
    ("temporal",        "时间关系",   "时间点/时间区间之间的关系（Allen 区间代数）及有效期约束", "tb_onto_temporal.rel_type"),
    ("status_relation", "状态关系",   "状态之间的迁移/依赖/互斥，以及对象对状态的依赖", "tb_onto_status_rel.rel_type"),
    ("dependency",      "依赖与规则关系", "规则、版本、对象之间的依赖与约束关系", "tb_onto_link.rel_kind"),
    ("cardinality",     "基数",       "关系两端允许的实例数量，保存于 tb_onto_rel.cardinality", "tb_onto_rel.cardinality"),
    ("version_relation", "版本谱系关系", "本体版本之间的分支/取代/兼容关系", "tb_onto_version_link.rel_kind"),
    ("status",          "生命周期状态", "本体及各对象的发布状态", "各对象 status"),
    ("scope",           "归属范围",   "本体归属领域或个人", "tb_ontology.scope"),
    ("authority",       "权威等级",   "跨本体合并冲突时的优先级", "tb_ontology.authority"),
    ("datasource_type", "数据源类型", "本体绑定的物理数据来源类型", "tb_data_source.type"),
]

DIM_ITEMS = [
    # structural
    ("structural", "inheritance", "继承", "is-a，子类继承父类的属性与关系，对应存量 parent_name", "子类→父类", 1, ""),
    ("structural", "association", "关联", "普通结构连接，无生命周期依赖", "双向/单向", 1, ""),
    ("structural", "composition", "组合", "强拥有，部分随整体创建与销毁", "整体→部分", 1, ""),
    ("structural", "aggregation", "聚合", "弱拥有，部分可独立存在", "整体→部分", 1, ""),
    ("structural", "dependency",  "依赖", "源的变更会影响目标", "依赖方→被依赖方", 1, ""),
    ("structural", "realization", "实现", "类实现接口或契约规则", "实现方→契约", 1, ""),
    # person_relation（人物关系：家族族谱/社会关系）
    ("person_relation", "father_of",       "父亲",     "主体是客体的父亲",           "父→子", 1, "存量值"),
    ("person_relation", "mother_of",       "母亲",     "主体是客体的母亲",           "母→子", 1, "存量值"),
    ("person_relation", "parent_of",       "父母",     "主体是客体的父或母（泛化）", "父母→子女", 1, ""),
    ("person_relation", "son_of",          "儿子",     "主体是客体的儿子",           "子→父母", 1, ""),
    ("person_relation", "daughter_of",     "女儿",     "主体是客体的女儿",           "女→父母", 1, ""),
    ("person_relation", "child_of",        "子女",     "主体是客体的子女（泛化）",   "子女→父母", 1, ""),
    ("person_relation", "spouse_of",       "配偶",     "主体与客体为夫妻",           "双向", 1, "存量值"),
    ("person_relation", "husband_of",      "丈夫",     "主体是客体的丈夫",           "夫→妻", 1, ""),
    ("person_relation", "wife_of",         "妻子",     "主体是客体的妻子",           "妻→夫", 1, ""),
    ("person_relation", "sibling_of",      "兄弟姐妹", "主体与客体为同辈手足",       "双向", 1, "存量值"),
    ("person_relation", "brother_of",      "兄弟",     "主体是客体的兄弟",           "双向", 1, ""),
    ("person_relation", "sister_of",       "姐妹",     "主体是客体的姐妹",           "双向", 1, ""),
    ("person_relation", "grandparent_of",  "祖辈",     "主体是客体的祖父母（泛化）", "祖→孙", 1, "存量值"),
    ("person_relation", "grandfather_of",  "祖父",     "主体是客体的祖父",           "祖→孙", 1, ""),
    ("person_relation", "grandmother_of",  "祖母",     "主体是客体的祖母",           "祖→孙", 1, ""),
    ("person_relation", "grandson_of",     "孙子",     "主体是客体的孙子",           "孙→祖", 1, ""),
    ("person_relation", "granddaughter_of","孙女",     "主体是客体的孙女",           "孙→祖", 1, ""),
    ("person_relation", "uncle_of",        "叔伯",     "主体是客体的叔伯",           "叔伯→侄", 1, ""),
    ("person_relation", "aunt_of",         "姑姨",     "主体是客体的姑姨",           "姑姨→侄", 1, ""),
    ("person_relation", "nephew_of",       "侄子",     "主体是客体的侄子",           "侄→叔伯", 1, ""),
    ("person_relation", "niece_of",        "侄女",     "主体是客体的侄女",           "侄→叔伯", 1, ""),
    ("person_relation", "cousin_of",       "堂表兄弟姐妹", "主体与客体为堂表同辈",   "双向", 1, ""),
    ("person_relation", "ancestor_of",     "祖先",     "主体是客体的直系祖先",       "祖→后", 1, ""),
    ("person_relation", "descendant_of",   "后代",     "主体是客体的直系后代",       "后→祖", 1, ""),
    ("person_relation", "mentor_of",       "师徒",     "主体是客体的师父/导师",      "师→徒", 1, ""),
    ("person_relation", "friend_of",       "朋友",     "主体与客体为朋友",           "双向", 1, ""),
    ("person_relation", "colleague_of",    "同事",     "主体与客体为同事",           "双向", 1, ""),
    # belonging（所属关系：家族/辈分/组织/地点归属）
    ("belonging", "belongs_to",              "属于",     "通用归属关系",                 "对象→所属", 1, "存量值"),
    ("belonging", "belongs_to_family",       "属于家族", "人物属于某家族",               "人→家族", 1, ""),
    ("belonging", "belongs_to_generation",   "属于辈分", "人物属于某辈分，如家族族谱",   "人→辈分", 1, "存量值"),
    ("belonging", "belongs_to_household",    "属于家庭", "人物属于某户/家庭",           "人→家庭", 1, ""),
    ("belonging", "belongs_to_clan",         "属于宗族", "人物属于某宗族/姓氏分支",     "人→宗族", 1, ""),
    ("belonging", "belongs_to_org",          "属于组织", "人物属于某公司/机构",         "人→组织", 1, ""),
    ("belonging", "belongs_to_dept",         "属于部门", "人物属于某部门",               "人→部门", 1, ""),
    ("belonging", "belongs_to_team",         "属于团队", "人物属于某项目团队",           "人→团队", 1, ""),
    ("belonging", "member_of",               "成员",     "个体是某群体的成员",           "成员→群体", 1, ""),
    ("belonging", "leader_of",               "领导",     "主体领导某组织或团队",         "领导→组织", 1, ""),
    ("belonging", "subordinate_of",          "下属",     "主体是某人的下属",             "下属→上级", 1, ""),
    ("belonging", "founder_of",              "创立",     "主体创立了某组织",             "人→组织", 1, ""),
    ("belonging", "owner_of",                "拥有",     "主体拥有某对象或资产",         "拥有者→物", 1, ""),
    ("belonging", "affiliated_with",         "隶属",     "机构之间的隶属/挂靠关系",     "下级→上级", 1, ""),
    ("belonging", "located_in",              "位于",     "对象位于某地点",               "对象→地点", 1, ""),
    ("belonging", "resident_of",             "居住于",   "人物居住于某地",               "人→地点", 1, ""),
    ("belonging", "native_of",               "祖籍",     "人物祖籍某地",                 "人→地点", 1, ""),
    ("belonging", "generation_of",           "辈分包含", "辈分包含成员（反向 belongs_to_generation）", "辈分→人", 1, "存量值"),
    ("belonging", "join_project",            "参与项目", "人员参与项目，如组织管理本体 a1→b1", "人→项目", 1, "存量值"),
    ("belonging", "participant_of",          "参与者",   "对象参与某活动/事件/项目",     "参与者→活动", 1, ""),
    # person_relation 补充（存量 + 常见姻亲/继养）
    ("person_relation", "head_of",           "族长管辖", "族长管辖族人",                 "族长→族人", 1, "存量值"),
    ("person_relation", "inherits_rank",     "继承爵位", "族长爵位继承",                 "继承者→前任", 1, "存量值"),
    ("person_relation", "married_in",        "嫁入",     "人物通过婚姻加入某婚姻/家族", "人→婚姻", 1, "存量值"),
    ("person_relation", "father_in_law_of",  "岳父/公公", "主体是客体的岳父或公公",       "长辈→晚辈", 1, ""),
    ("person_relation", "mother_in_law_of",  "岳母/婆婆", "主体是客体的岳母或婆婆",       "长辈→晚辈", 1, ""),
    ("person_relation", "son_in_law_of",     "女婿",     "主体是客体的女婿",             "女婿→岳家", 1, ""),
    ("person_relation", "daughter_in_law_of","儿媳",     "主体是客体的儿媳",             "儿媳→婆家", 1, ""),
    ("person_relation", "stepfather_of",     "继父",     "主体是客体的继父",             "继父→继子", 1, ""),
    ("person_relation", "stepmother_of",     "继母",     "主体是客体的继母",             "继母→继子", 1, ""),
    ("person_relation", "adopted_child_of",  "养子女",   "主体是客体的养子女",           "养子女→养父母", 1, ""),
    ("person_relation", "twin_of",           "双胞胎",   "主体与客体为双胞胎",           "双向", 1, ""),
    # semantic
    ("semantic", "kinship",     "亲属",    "父子/配偶等亲属语义，如 father_of、spouse_of", "主体→客体", 1, ""),
    ("semantic", "part_of",     "组成",    "部分属于整体", "部分→整体", 1, ""),
    ("semantic", "ownership",   "归属",    "拥有者与被拥有物", "拥有者→物", 1, ""),
    ("semantic", "membership",  "成员",    "个体属于组织或群体", "成员→组织", 1, ""),
    ("semantic", "location",    "位置",    "对象或事件位于某地", "对象→地点", 1, ""),
    ("semantic", "causal",      "因果",    "原因导致结果", "因→果", 1, ""),
    ("semantic", "temporal",    "时序",    "时间先后关系", "先→后", 1, ""),
    ("semantic", "provenance",  "来源派生", "结论派生自证据或数据", "派生→来源", 1, ""),
    ("semantic", "reference",   "引用",    "弱语义引用，不蕴含生命周期依赖", "引用方→被引用方", 1, ""),
    # mapping
    ("mapping", "node",     "实体映射",  "本体类映射到物理表/图节点", "本体→物理", 1, "存量值"),
    ("mapping", "edge",     "关系映射",  "关系映射到外键或边表", "本体→物理", 1, "存量值"),
    ("mapping", "property", "属性映射",  "属性映射到字段", "本体→物理", 0, "待开放"),
    ("mapping", "event",    "事件映射",  "事件类型映射到事件表", "本体→物理", 0, "待开放"),
    ("mapping", "rule",     "规则映射",  "规则映射到校验逻辑或触发器", "本体→物理", 0, "待开放"),
    ("mapping", "alias",    "别名映射",  "同名异义消歧", "本体→物理", 0, "待开放"),
    # event_flow
    ("event_flow", "before",    "早于",       "事件严格先于另一事件",    "前→后", 1, ""),
    ("event_flow", "after",     "晚于",       "事件严格晚于另一事件",    "后→前", 1, ""),
    ("event_flow", "overlaps",  "时间重叠",   "两事件区间部分交叉",      "双向", 1, ""),
    ("event_flow", "during",    "期间",       "事件发生在另一事件期间",  "子→父", 1, ""),
    ("event_flow", "contains",  "包含",       "事件包含另一事件",        "父→子", 1, ""),
    ("event_flow", "meets",     "紧接",       "前事件结束即后事件开始",  "前→后", 1, ""),
    ("event_flow", "causes",    "导致",       "因果驱动，前事件是原因",  "因→果", 1, ""),
    ("event_flow", "triggers",  "触发",       "条件满足后触发事件",      "条件→事件", 1, ""),
    ("event_flow", "enables",   "允许",       "前置事件使后置事件可执行", "允许方→被执行方", 1, ""),
    ("event_flow", "prevents",  "阻止",       "前置事件阻止后置事件",    "阻止方→被阻止方", 1, ""),
    ("event_flow", "part_of",   "子事件",     "组合事件中的子步骤",      "子→父", 1, ""),
    # temporal（时间关系：Allen 区间代数 13 种 + 有效期语义）
    ("temporal", "before",          "早于",     "区间A结束早于区间B开始（不接触）", "A→B", 1, ""),
    ("temporal", "after",           "晚于",     "区间A开始晚于区间B结束",         "A→B", 1, ""),
    ("temporal", "meets",           "紧接",     "A结束时刻等于B开始时刻",         "A→B", 1, ""),
    ("temporal", "met_by",          "被紧接",   "A开始时刻等于B结束时刻",         "A→B", 1, ""),
    ("temporal", "overlaps",        "重叠",     "A开始早于B且部分覆盖B",          "A→B", 1, ""),
    ("temporal", "overlapped_by",   "被重叠",   "B开始早于A且部分覆盖A",          "A→B", 1, ""),
    ("temporal", "during",          "期间",     "A完全位于B的时间区间内",         "A→B", 1, ""),
    ("temporal", "contains",        "包含",     "A的时间区间完全包含B",           "A→B", 1, ""),
    ("temporal", "starts",          "同时开始", "A与B开始时刻相同但A先结束",       "A→B", 1, ""),
    ("temporal", "started_by",      "被同时开始", "B与A开始时刻相同但B先结束",   "A→B", 1, ""),
    ("temporal", "finishes",        "同时结束", "A与B结束时刻相同但A开始更晚",     "A→B", 1, ""),
    ("temporal", "finished_by",     "被同时结束", "B与A结束时刻相同但B开始更晚", "A→B", 1, ""),
    ("temporal", "equal",           "相等",     "A与B时间区间完全相同",           "双向", 1, ""),
    ("temporal", "same_time",       "同时",     "两时间点相同",                   "双向", 1, ""),
    ("temporal", "concurrent_with", "并发",     "时间上并行发生，无先后因果",     "双向", 1, ""),
    ("temporal", "valid_during",    "有效于",   "数据在该时间段内有效（valid_from/to）", "对象→时间段", 1, ""),
    ("temporal", "valid_before",    "先于生效", "对象在另一对象生效之前有效",     "A→B", 1, ""),
    ("temporal", "valid_after",     "后于生效", "对象在另一对象生效之后有效",     "A→B", 1, ""),
    ("temporal", "supersedes_time", "时效取代", "新有效期覆盖旧有效期（同实体）", "新→旧", 1, ""),
    ("temporal", "overlaps_valid",  "有效期重叠", "两对象有效期存在交叉（检查告警）", "双向", 1, ""),
    ("temporal", "starts_at",       "开始时间", "对象/事件的起始时刻（对应 valid_from / start_time 字段）", "对象→时间点", 1, ""),
    ("temporal", "ends_at",         "结束时间", "对象/事件的终止时刻（对应 valid_to / end_time 字段）", "对象→时间点", 1, ""),
    ("temporal", "between",         "介于…之间", "时间点/对象落在指定的起止时间之间（需配置上下界）", "对象→[起,止]", 1, ""),
    # status_relation（状态关系：迁移/依赖/互斥）
    ("status_relation", "transitions_to",    "迁移至",     "状态A可转移到状态B",             "A→B", 1, ""),
    ("status_relation", "requires_state",    "状态前提",   "对象生效要求另一对象处于某状态", "对象→对象状态", 1, ""),
    ("status_relation", "depends_on_state",  "状态依赖",   "本对象状态依赖另一对象状态",     "对象→对象", 1, ""),
    ("status_relation", "gated_by_state",    "状态门控",   "另一对象的状态作为开关门控",     "门控→被门控", 1, ""),
    ("status_relation", "excludes_state",    "状态互斥",   "两个状态不能同时成立",           "双向", 1, ""),
    ("status_relation", "coexists_with",     "状态共存",   "两个状态可以同时成立",           "双向", 1, ""),
    ("status_relation", "precedes_state",    "状态先于",   "状态A必须先于状态B出现",         "A→B", 1, ""),
    ("status_relation", "invalidates",       "使失效",     "进入状态A导致对象B失效",         "A→B", 1, ""),
    ("status_relation", "activates",         "激活",       "状态A触发对象B进入生效状态",     "A→B", 1, ""),
    ("status_relation", "suspends",          "暂停",       "状态A使对象B临时停止",           "A→B", 1, ""),
    ("status_relation", "restores",          "恢复",       "状态A使对象B恢复到先前状态",     "A→B", 1, ""),
    ("status_relation", "supersedes_state",  "状态取代",   "新状态覆盖旧状态定义",           "新→旧", 1, ""),
    ("status_relation", "inherits_state",    "状态继承",   "子类状态定义继承父类",           "子→父", 1, ""),
    ("status_relation", "conflicts_state",   "状态冲突",   "两状态定义存在语义冲突",         "双向", 1, ""),
    # dependency
    ("dependency", "depends_on",    "依赖于",   "当前对象生效依赖另一对象",   "依赖方→被依赖方", 1, ""),
    ("dependency", "derives_from",  "派生自",   "结论或数据来源于另一对象",   "派生→来源", 1, ""),
    ("dependency", "conflicts_with","冲突",    "两个对象语义互斥，不能同时生效", "双向", 1, ""),
    ("dependency", "supersedes",    "取代",     "新版本覆盖旧版本",           "新→旧", 1, ""),
    ("dependency", "replaces",      "替换",     "等价替换，语义不变",         "替代→原", 1, ""),
    ("dependency", "validates",     "校验",     "规则校验某类或属性",         "规则→被校验对象", 1, ""),
    ("dependency", "references",    "引用",     "弱依赖，仅引用不约束",       "引用方→被引用方", 1, ""),
    ("dependency", "blocks",        "阻断",     "不满足则流程不能继续",       "阻断方→被阻断方", 1, ""),
    ("dependency", "enables",       "启用",     "满足后启用另一对象",         "启用方→被启用方", 1, ""),
    ("dependency", "requires",      "必需依赖", "强依赖：缺少则当前对象无法生效（区别于 depends_on 弱依赖）", "依赖方→被依赖方", 1, ""),
    ("dependency", "constrains",    "约束",     "限制另一对象的取值范围或行为", "约束方→被约束方", 1, ""),
    ("dependency", "triggers",      "触发",     "条件满足时触发另一对象执行", "触发方→被触发方", 1, ""),
    ("dependency", "inhibits",      "抑制",     "压制或降低另一对象的生效", "抑制方→被抑制方", 1, ""),
    ("dependency", "guards",        "守卫",     "作为前置守卫条件，通过后才继续", "守卫→被守卫", 1, ""),
    ("dependency", "overrides",     "覆盖",     "运行时覆盖另一对象的定义（区别于版本 supersedes）", "覆盖方→被覆盖方", 1, ""),
    ("dependency", "co_depends_on", "互相依赖", "两个对象互相依赖，形成环需检查", "双向", 1, ""),
    ("dependency", "affects",       "影响",     "源变化会影响目标，弱于 depends_on", "影响方→被影响方", 1, ""),
    ("dependency", "governs",       "支配",     "规则/策略支配某对象的行为", "规则→对象", 1, ""),
    ("dependency", "implements",    "实现契约", "对象实现某接口/契约规则", "实现方→契约", 1, ""),
    ("dependency", "consumes",      "消费",     "对象消费另一对象提供的资源", "消费方→资源", 1, ""),
    ("dependency", "provides",      "提供",     "对象向另一对象提供资源/能力", "提供方→消费方", 1, ""),
    # cardinality
    ("cardinality", "one",          "1..1",     "一对一，存量 one",             "—", 1, "存量值"),
    ("cardinality", "many",         "1..N",     "一对多，存量 many",            "—", 1, "存量值"),
    ("cardinality", "zero_or_one",  "0..1",     "零或一，等价于 one 且 nullable=1", "—", 0, "用 one+nullable 表达"),
    ("cardinality", "zero_or_many", "0..N",     "零或多，等价于 many 且 nullable=1", "—", 0, "用 many+nullable 表达"),
    # version_relation
    ("version_relation", "based_on",        "基于",     "当前版本基于某版本创建",   "新→旧", 1, ""),
    ("version_relation", "supersedes",      "取代",     "当前版本取代前一版本",     "新→旧", 1, ""),
    ("version_relation", "forked_from",     "分叉自",   "从某版本分出独立分支",     "分支→主干", 1, ""),
    ("version_relation", "merges",          "合并自",   "由多个分支合并而来",       "合并→分支", 1, ""),
    ("version_relation", "compatible_with", "兼容",     "跨版本可互操作",           "双向", 1, ""),
    # status
    ("status", "draft",      "草稿",     "编辑中，不对外生效",           "—", 1, ""),
    ("status", "active",     "生效",     "正常可用，默认状态",           "—", 1, "存量值"),
    ("status", "frozen",     "冻结",     "只读锁定，不可编辑",           "—", 1, ""),
    ("status", "deprecated", "废弃",     "不推荐新引用，检查时告警",     "—", 1, ""),
    ("status", "archived",   "归档",     "历史保留，不参与查询",         "—", 1, ""),
    ("status", "disabled",   "停用",     "规则保留定义但不执行",         "—", 1, ""),
    ("status", "broken",     "失效",     "映射指向的物理对象已不存在",   "—", 1, ""),
    # scope
    ("scope", "domain",   "领域本体", "领域级共享本体，对全空间可见", "—", 1, "存量值"),
    ("scope", "personal", "个人本体", "个人私有本体，仅创建者可见",   "—", 1, ""),
    # authority
    ("authority", "normal", "普通",   "默认权威等级",                       "—", 1, "存量值"),
    ("authority", "high",   "高权威", "跨本体合并冲突时优先采用该本体定义", "—", 1, "存量值"),
    # datasource_type
    ("datasource_type", "builtin-demo", "内置示例", "内置演示数据（非真实图谱）", "—", 1, "存量值"),
    ("datasource_type", "graph-ref",    "图谱引用", "引用知识图谱实例（按被引用图谱 db_type 决定 SQL/N4）", "—", 1, "存量值"),
    ("datasource_type", "neo4j",        "Neo4j",    "直连 Neo4j 图数据库", "—", 1, ""),
    ("datasource_type", "sql",          "SQL",      "直连关系数据库",       "—", 1, ""),
]


def _seed_dims(c):
    """维度种子：INSERT OR IGNORE，升级不覆盖用户改过的 label/description"""
    for i, (code, name, desc, applies) in enumerate(DIM_DOMAINS):
        c.execute("INSERT OR IGNORE INTO tb_dim_domain(code,name,description,applies_to,sort_order) VALUES(?,?,?,?,?)",
                  (code, name, desc, applies, i))
    for i, (domain, code, label, desc, direction, supported, extra) in enumerate(DIM_ITEMS):
        c.execute("INSERT OR IGNORE INTO tb_dim_item(domain_code,code,label,description,direction,supported,extra,sort_order) "
                  "VALUES(?,?,?,?,?,?,?,?)",
                  (domain, code, label, desc, direction, supported, extra or '{}', i))


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_onto_space(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_ontology(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, scope TEXT DEFAULT 'domain',
          namespace TEXT DEFAULT '', authority TEXT DEFAULT 'normal', version TEXT DEFAULT 'v1',
          status TEXT DEFAULT 'active', comment TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_onto_class(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          name TEXT NOT NULL, parent_name TEXT DEFAULT '', comment TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_onto_rel(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          name TEXT NOT NULL, subj_class TEXT NOT NULL, obj_class TEXT NOT NULL,
          cardinality TEXT DEFAULT 'many' CHECK(cardinality IN ('one','many')),
          nullable INTEGER DEFAULT 1, inherits_from TEXT DEFAULT '', comment TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_onto_mapping(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          onto_type TEXT NOT NULL, physical_type TEXT NOT NULL, kind TEXT DEFAULT 'node' CHECK(kind IN ('node','edge')));
        CREATE TABLE IF NOT EXISTS tb_data_source(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type TEXT DEFAULT 'builtin-demo',
          config TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_onto_version(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL, version_no INTEGER NOT NULL,
          op TEXT NOT NULL, note TEXT DEFAULT '', snapshot TEXT DEFAULT '{}',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_audit_log(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          module TEXT NOT NULL DEFAULT 'ontology',       -- graph | ontology
          target_type TEXT NOT NULL,                     -- ontology/space/class/rel/mapping/version/datasource/graph
          target_id INTEGER DEFAULT 0,
          target_name TEXT DEFAULT '',
          op TEXT NOT NULL,
          detail TEXT DEFAULT '',
          operator TEXT DEFAULT 'system',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE INDEX IF NOT EXISTS idx_audit_target ON tb_audit_log(module, target_id, id DESC);
        CREATE TABLE IF NOT EXISTS tb_dim_domain(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
          description TEXT DEFAULT '', applies_to TEXT DEFAULT '',
          sort_order INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1,
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_dim_item(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          domain_code TEXT NOT NULL, code TEXT NOT NULL, label TEXT NOT NULL,
          description TEXT DEFAULT '', direction TEXT DEFAULT '',
          supported INTEGER DEFAULT 1, extra TEXT DEFAULT '{}',
          sort_order INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1,
          created_at TEXT DEFAULT (datetime('now','localtime')),
          UNIQUE(domain_code, code));
        CREATE INDEX IF NOT EXISTS idx_dim_item_domain ON tb_dim_item(domain_code, sort_order);
        """)
        _seed_dims(c)
        try:
            c.execute("ALTER TABLE tb_dim_domain ADD COLUMN enabled INTEGER DEFAULT 1")
            c.commit()
        except Exception:
            pass
        # 本体归属空间（对齐知识库 space 模型）
        try:
            c.execute("ALTER TABLE tb_ontology ADD COLUMN space_id INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass


def migrate_ensure_space():
    """本体必须归属本体空间：保证至少一个空间存在，并把未归属的存量本体归入默认空间"""
    if not one("SELECT id FROM tb_onto_space LIMIT 1"):
        run("INSERT INTO tb_onto_space(name, description) VALUES('默认空间','系统自动创建')")
    d = one("SELECT id FROM tb_onto_space ORDER BY id LIMIT 1")
    run("UPDATE tb_ontology SET space_id=? WHERE space_id IS NULL OR space_id=0", (d["id"],))


def rows(sql, args=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def run(sql, args=()):
    with conn() as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid


def one(sql, args=()):
    with conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


def exec_many(sql_list):
    with conn() as c:
        for s, a in sql_list:
            c.execute(s, a)
        c.commit()


# ===== 版本快照（对齐图谱模块 tb_graph_version） =====
def snapshot(oid):
    """本体全量快照：本体定义 + 类 + 关系规则 + 映射"""
    return {
        "ontology": one("SELECT * FROM tb_ontology WHERE id=?", (oid,)),
        "classes": rows("SELECT * FROM tb_onto_class WHERE ontology_id=? ORDER BY id", (oid,)),
        "rels": rows("SELECT * FROM tb_onto_rel WHERE ontology_id=? ORDER BY id", (oid,)),
        "mappings": rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=? ORDER BY id", (oid,)),
    }


def bump_version(oid):
    """本体写操作后递增版本号 v1->v2..."""
    o = one("SELECT version FROM tb_ontology WHERE id=?", (oid,))
    cur = o["version"] if o and o["version"] else "v1"
    try:
        n = int(str(cur).lstrip("v")) + 1
    except Exception:
        n = 2
    new = f"v{n}"
    run("UPDATE tb_ontology SET version=? WHERE id=?", (new, oid))
    return new


def audit(target_type, target_id, target_name, op, detail="", module="ontology"):
    run("INSERT INTO tb_audit_log(module, target_type, target_id, target_name, op, detail, operator) VALUES(?,?,?,?,?,?,?)",
        (module, target_type, target_id or 0, target_name or "", op, detail or "", current_operator()))


def audit_list(target_id=None, limit=200):
    if target_id:
        return rows("SELECT * FROM tb_audit_log WHERE target_id=? ORDER BY id DESC LIMIT ?", (target_id, limit))
    return rows("SELECT * FROM tb_audit_log ORDER BY id DESC LIMIT ?", (limit,))


def save_version(oid, op, note=""):
    """写操作后自动快照（version_no 自增），并同步递增本体版本号、记录审计日志"""
    last = one("SELECT MAX(version_no) m FROM tb_onto_version WHERE ontology_id=?", (oid,))
    no = (last["m"] or 0) + 1
    run("INSERT INTO tb_onto_version(ontology_id, version_no, op, note, snapshot) VALUES(?,?,?,?,?)",
        (oid, no, op, note, json.dumps(snapshot(oid), ensure_ascii=False)))
    bump_version(oid)
    tmap = {"ontology": "ontology", "class": "class", "rel": "rel", "mapping": "mapping"}
    target = next((v for k, v in tmap.items() if k in op), "ontology")
    o = one("SELECT name FROM tb_ontology WHERE id=?", (oid,))
    audit(target, oid, (o or {}).get("name", ""), op, f"v{no} {note}" if note else f"v{no}")
    return no


init_db()
migrate_ensure_space()
