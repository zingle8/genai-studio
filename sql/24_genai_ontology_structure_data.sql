--
-- PostgreSQL database dump
--

\restrict ohN8j7I8C07Rrzztdo8nfdvpPVNoSkgnLfBoUxODLdc61XG7YzYRXas0PRWwL2M

-- Dumped from database version 16.16
-- Dumped by pg_dump version 16.16

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: tb_audit_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_audit_log (
    id integer NOT NULL,
    module text DEFAULT 'ontology'::text NOT NULL,
    target_type text NOT NULL,
    target_id integer DEFAULT 0,
    target_name text DEFAULT ''::text,
    op text NOT NULL,
    detail text DEFAULT ''::text,
    operator text DEFAULT 'system'::text,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_audit_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_audit_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_audit_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_audit_log_id_seq OWNED BY public.tb_audit_log.id;


--
-- Name: tb_data_source; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_data_source (
    id integer NOT NULL,
    name text NOT NULL,
    type text DEFAULT 'builtin-demo'::text,
    config text DEFAULT ''::text,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_data_source_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_data_source_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_data_source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_data_source_id_seq OWNED BY public.tb_data_source.id;


--
-- Name: tb_dim_onto_domain; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_dim_onto_domain (
    id integer NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    description text DEFAULT ''::text,
    applies_to text DEFAULT ''::text,
    sort_order integer DEFAULT 0,
    enabled integer DEFAULT 1,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_dim_onto_domain_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_dim_onto_domain_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_dim_onto_domain_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_dim_onto_domain_id_seq OWNED BY public.tb_dim_onto_domain.id;


--
-- Name: tb_dim_onto_item; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_dim_onto_item (
    id integer NOT NULL,
    domain_code text NOT NULL,
    code text NOT NULL,
    label text NOT NULL,
    description text DEFAULT ''::text,
    direction text DEFAULT ''::text,
    supported integer DEFAULT 1,
    extra text DEFAULT '{}'::text,
    sort_order integer DEFAULT 0,
    enabled integer DEFAULT 1,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_dim_onto_item_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_dim_onto_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_dim_onto_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_dim_onto_item_id_seq OWNED BY public.tb_dim_onto_item.id;


--
-- Name: tb_onto_class; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_onto_class (
    id integer NOT NULL,
    ontology_id integer NOT NULL,
    name text NOT NULL,
    parent_name text DEFAULT ''::text,
    comment text DEFAULT ''::text
);


--
-- Name: tb_onto_class_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_onto_class_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_onto_class_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_onto_class_id_seq OWNED BY public.tb_onto_class.id;


--
-- Name: tb_onto_mapping; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_onto_mapping (
    id integer NOT NULL,
    ontology_id integer NOT NULL,
    onto_type text NOT NULL,
    physical_type text NOT NULL,
    kind text DEFAULT 'node'::text
);


--
-- Name: tb_onto_mapping_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_onto_mapping_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_onto_mapping_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_onto_mapping_id_seq OWNED BY public.tb_onto_mapping.id;


--
-- Name: tb_onto_rel; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_onto_rel (
    id integer NOT NULL,
    ontology_id integer NOT NULL,
    name text NOT NULL,
    subj_class text NOT NULL,
    obj_class text NOT NULL,
    cardinality text DEFAULT 'many'::text,
    nullable integer DEFAULT 1,
    inherits_from text DEFAULT ''::text,
    comment text DEFAULT ''::text
);


--
-- Name: tb_onto_rel_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_onto_rel_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_onto_rel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_onto_rel_id_seq OWNED BY public.tb_onto_rel.id;


--
-- Name: tb_onto_space; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_onto_space (
    id integer NOT NULL,
    name text NOT NULL,
    description text DEFAULT ''::text,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_onto_space_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_onto_space_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_onto_space_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_onto_space_id_seq OWNED BY public.tb_onto_space.id;


--
-- Name: tb_onto_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_onto_version (
    id integer NOT NULL,
    ontology_id integer NOT NULL,
    version_no integer NOT NULL,
    op text NOT NULL,
    note text DEFAULT ''::text,
    snapshot text DEFAULT '{}'::text,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_onto_version_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_onto_version_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_onto_version_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_onto_version_id_seq OWNED BY public.tb_onto_version.id;


--
-- Name: tb_ontology; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tb_ontology (
    id integer NOT NULL,
    name text NOT NULL,
    scope text DEFAULT 'domain'::text,
    namespace text DEFAULT ''::text,
    authority text DEFAULT 'normal'::text,
    version text DEFAULT 'v1'::text,
    status text DEFAULT 'active'::text,
    comment text DEFAULT ''::text,
    space_id integer DEFAULT 0,
    created_at text DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: tb_ontology_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tb_ontology_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tb_ontology_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tb_ontology_id_seq OWNED BY public.tb_ontology.id;


--
-- Name: tb_audit_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_audit_log ALTER COLUMN id SET DEFAULT nextval('public.tb_audit_log_id_seq'::regclass);


--
-- Name: tb_data_source id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_data_source ALTER COLUMN id SET DEFAULT nextval('public.tb_data_source_id_seq'::regclass);


--
-- Name: tb_dim_onto_domain id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_dim_onto_domain ALTER COLUMN id SET DEFAULT nextval('public.tb_dim_onto_domain_id_seq'::regclass);


--
-- Name: tb_dim_onto_item id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_dim_onto_item ALTER COLUMN id SET DEFAULT nextval('public.tb_dim_onto_item_id_seq'::regclass);


--
-- Name: tb_onto_class id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_class ALTER COLUMN id SET DEFAULT nextval('public.tb_onto_class_id_seq'::regclass);


--
-- Name: tb_onto_mapping id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_mapping ALTER COLUMN id SET DEFAULT nextval('public.tb_onto_mapping_id_seq'::regclass);


--
-- Name: tb_onto_rel id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_rel ALTER COLUMN id SET DEFAULT nextval('public.tb_onto_rel_id_seq'::regclass);


--
-- Name: tb_onto_space id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_space ALTER COLUMN id SET DEFAULT nextval('public.tb_onto_space_id_seq'::regclass);


--
-- Name: tb_onto_version id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_version ALTER COLUMN id SET DEFAULT nextval('public.tb_onto_version_id_seq'::regclass);


--
-- Name: tb_ontology id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_ontology ALTER COLUMN id SET DEFAULT nextval('public.tb_ontology_id_seq'::regclass);


--
-- Data for Name: tb_audit_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_audit_log (id, module, target_type, target_id, target_name, op, detail, operator, created_at) FROM stdin;
1	ontology	class	1	o1-组织管理	create_class	v5 新增类 审计测试类	testbrowser	2026-11-23 17:26:02
2	ontology	class	1	o1-组织管理	delete_class	v6 删除类 审计测试类	testbrowser	2026-11-23 17:26:02
3	ontology	graph	14	权限测试-本体创建图谱	create_graph	本体模块创建图谱（图谱模块 graph.db，来源 ontology）	system	2026-11-23 17:33:52
4	ontology	space	11	测试空间-接口测试	create_space	自动化用例	system	2026-11-23 17:33:53
5	ontology	space	11	测试空间-接口测试	delete_space		system	2026-11-23 17:33:53
6	ontology	ontology	10	测试本体-接口测试	create_onto	v1 创建本体 测试本体-接口测试	system	2026-11-23 17:33:53
7	ontology	class	10	测试本体-接口测试	create_class	v2 新增类 部门	system	2026-11-23 17:33:53
8	ontology	rel	10	测试本体-接口测试	create_rel	v3 新增关系 属于	system	2026-11-23 17:33:53
9	ontology	ontology	10	测试本体-接口测试	import	v4 导入yaml：新增 0 类 / 0 规则	system	2026-11-23 17:33:53
10	ontology	ontology	10	测试本体-接口测试	pre_restore	v5 恢复到 v1 前自动保存	system	2026-11-23 17:33:53
11	ontology	ontology	10	测试本体-接口测试	restore	v6 恢复到 v1	system	2026-11-23 17:33:53
12	ontology	ontology	10	测试本体-接口测试	delete_onto	v7 删除本体（删除前快照）	system	2026-11-23 17:33:53
13	ontology	class	1	o1-组织管理	update_class	v1 修改类 c0	system	2026-11-23 15:15:12
14	ontology	class	1	o1-组织管理	update_class	v2 修改类 c0	system	2026-11-23 15:15:24
15	ontology	ontology	1	o1-组织管理	pre_restore	v3 恢复到 v2 前自动保存	system	2026-11-23 15:15:26
16	ontology	ontology	1	o1-组织管理	restore	v4 恢复到 v2	system	2026-11-23 15:15:26
17	ontology	ontology	7	万家家族族谱	create_onto	v1 创建本体 万家家族族谱	system	2026-11-23 15:37:07
18	ontology	class	7	万家家族族谱	create_class	v2 新增类 person	system	2026-11-23 15:37:07
19	ontology	class	7	万家家族族谱	create_class	v3 新增类 male	system	2026-11-23 15:37:07
20	ontology	class	7	万家家族族谱	create_class	v4 新增类 female	system	2026-11-23 15:37:07
21	ontology	class	7	万家家族族谱	create_class	v5 新增类 generation	system	2026-11-23 15:37:07
22	ontology	class	7	万家家族族谱	create_class	v6 新增类 patriarch	system	2026-11-23 15:37:07
23	ontology	class	7	万家家族族谱	create_class	v7 新增类 marriage	system	2026-11-23 15:37:07
24	ontology	class	7	万家家族族谱	create_class	v8 新增类 g1_jia	system	2026-11-23 15:37:07
25	ontology	class	7	万家家族族谱	create_class	v9 新增类 g2_yun	system	2026-11-23 15:37:07
26	ontology	class	7	万家家族族谱	create_class	v10 新增类 g3_qian	system	2026-11-23 15:37:07
27	ontology	class	7	万家家族族谱	create_class	v11 新增类 g4_kun	system	2026-11-23 15:37:07
28	ontology	class	7	万家家族族谱	create_class	v12 新增类 g5_zeng	system	2026-11-23 15:37:07
29	ontology	class	7	万家家族族谱	create_class	v13 新增类 g6_zhang	system	2026-11-23 15:37:07
30	ontology	rel	7	万家家族族谱	create_rel	v14 新增关系 father_of	system	2026-11-23 15:37:07
31	ontology	rel	7	万家家族族谱	create_rel	v15 新增关系 mother_of	system	2026-11-23 15:37:07
32	ontology	rel	7	万家家族族谱	create_rel	v16 新增关系 spouse_of	system	2026-11-23 15:37:07
33	ontology	rel	7	万家家族族谱	create_rel	v17 新增关系 sibling_of	system	2026-11-23 15:37:07
34	ontology	rel	7	万家家族族谱	create_rel	v18 新增关系 grandparent_of	system	2026-11-23 15:37:07
35	ontology	rel	7	万家家族族谱	create_rel	v19 新增关系 belongs_to_generation	system	2026-11-23 15:37:07
36	ontology	rel	7	万家家族族谱	create_rel	v20 新增关系 head_of	system	2026-11-23 15:37:07
37	ontology	rel	7	万家家族族谱	create_rel	v21 新增关系 married_in	system	2026-11-23 15:37:07
38	ontology	rel	7	万家家族族谱	create_rel	v22 新增关系 inherits_rank	system	2026-11-23 15:37:07
39	ontology	rel	7	万家家族族谱	create_rel	v23 新增关系 generation_of	system	2026-11-23 15:37:07
40	ontology	mapping	7	万家家族族谱	create_mapping	v24 绑定映射 person -> 人物	system	2026-11-23 15:40:15
41	ontology	mapping	7	万家家族族谱	create_mapping	v25 绑定映射 male -> 人物	system	2026-11-23 15:40:15
42	ontology	mapping	7	万家家族族谱	create_mapping	v26 绑定映射 female -> 人物	system	2026-11-23 15:40:15
43	ontology	mapping	7	万家家族族谱	create_mapping	v27 绑定映射 generation -> 辈分	system	2026-11-23 15:40:15
44	ontology	mapping	7	万家家族族谱	create_mapping	v28 绑定映射 father_of -> 父子	system	2026-11-23 15:40:15
45	ontology	mapping	7	万家家族族谱	create_mapping	v29 绑定映射 mother_of -> 母子	system	2026-11-23 15:40:15
46	ontology	mapping	7	万家家族族谱	create_mapping	v30 绑定映射 spouse_of -> 夫妻	system	2026-11-23 15:40:15
47	ontology	mapping	7	万家家族族谱	create_mapping	v31 绑定映射 sibling_of -> 兄弟姐妹	system	2026-11-23 15:40:15
48	ontology	mapping	7	万家家族族谱	create_mapping	v32 绑定映射 grandparent_of -> 祖孙	system	2026-11-23 15:40:15
49	ontology	mapping	7	万家家族族谱	create_mapping	v33 绑定映射 belongs_to_generation -> 属于辈分	system	2026-11-23 15:40:15
\.


--
-- Data for Name: tb_data_source; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_data_source (id, name, type, config, created_at) FROM stdin;
1	内置示例·公司数据	builtin-demo	{}	2026-11-17 11:18:12
2	万家家族族谱·实例数据	graph-ref	{"graphId": 9}	2026-11-23 15:40:15
\.


--
-- Data for Name: tb_dim_onto_domain; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_dim_onto_domain (id, code, name, description, applies_to, sort_order, enabled, created_at) FROM stdin;
51	belonging	所属关系	对象归属家族/辈分/组织/地点等的关系	tb_onto_rel.rel_kind	2	1	2026-11-26 20:39:30
2	semantic	业务语义关系	关系在业务上的语义分类，用于图展示与检索	tb_onto_rel.semantic_kind	3	1	2026-11-26 20:35:57
1	structural	结构关系	类与类之间的结构关系，保存于 tb_onto_rel.rel_kind	tb_onto_rel.rel_kind	0	1	2026-11-26 20:35:57
50	person_relation	人物关系	人物之间的亲属/社会关系，用于家族族谱类本体	tb_onto_rel.rel_kind	1	1	2026-11-26 20:39:30
3	mapping	映射关系	本体到物理数据的映射类型，保存于 tb_onto_mapping.kind	tb_onto_mapping.kind	4	1	2026-11-26 20:35:57
4	event_flow	事件流关系	事件类型之间的时序/因果/触发关系	tb_onto_event_flow.rel_type	5	1	2026-11-26 20:35:57
154	time_stauts	时间关系	时间点/时间区间之间的关系（Allen 区间代数）及有效期约束	tb_onto_temporal.rel_type	6	1	2026-11-26 20:53:02
155	status_relation	状态关系	状态之间的迁移/依赖/互斥，以及对象对状态的依赖	tb_onto_status_rel.rel_type	7	1	2026-11-26 20:53:02
5	dependency	依赖与规则关系	规则、版本、对象之间的依赖与约束关系	tb_onto_link.rel_kind	8	1	2026-11-26 20:35:57
517	rule_kind	规则类型	规则自身的种类（约束/推理/触发/校验等）	tb_onto_rule.kind	9	1	2026-11-26 21:08:06
518	rule_relation	规则关系	规则与规则之间的组合/互斥/优先/推导关系	tb_onto_rule_rel.rel_type	10	1	2026-11-26 21:08:06
6	cardinality	基数	关系两端允许的实例数量，保存于 tb_onto_rel.cardinality	tb_onto_rel.cardinality	11	1	2026-11-26 20:35:57
7	version_relation	版本谱系关系	本体版本之间的分支/取代/兼容关系	tb_onto_version_link.rel_kind	12	1	2026-11-26 20:35:57
8	status	生命周期状态	本体及各对象的发布状态	各对象 status	13	1	2026-11-26 20:35:57
119	scope	归属范围	本体归属领域或个人	tb_ontology.scope	14	1	2026-11-26 20:50:43
120	authority	权威等级	跨本体合并冲突时的优先级	tb_ontology.authority	15	1	2026-11-26 20:50:43
121	datasource_type	数据源类型	本体绑定的物理数据来源类型	tb_data_source.type	16	1	2026-11-26 20:50:43
576	data_type	数据类型	属性/字段的数据类型，含日期/时间/日期时间等时间类型	tb_onto_attr.data_type	17	1	2026-11-26 21:28:25
577	nullability	空值约束	定义层：属性是否允许为空（必填/可空/不适用）	tb_onto_attr.required	18	1	2026-11-26 21:28:25
578	value_presence	值存在性	实例层：实际数据的值是否存在（有值/空串/null/默认值）	实例数据校验	19	1	2026-11-26 21:28:25
579	uniqueness	唯一性约束	属性值的唯一性规则（唯一/主键/外键/可重复）	tb_onto_attr.unique	20	1	2026-11-26 21:28:25
\.


--
-- Data for Name: tb_dim_onto_item; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_dim_onto_item (id, domain_code, code, label, description, direction, supported, extra, sort_order, enabled, created_at) FROM stdin;
13	semantic	temporal	时序	时间先后关系	先→后	1	{}	78	1	2026-11-26 20:35:57
3	structural	composition	组合	强拥有，部分随整体创建与销毁	整体→部分	1	{}	2	1	2026-11-26 20:35:57
4	structural	aggregation	聚合	弱拥有，部分可独立存在	整体→部分	1	{}	3	1	2026-11-26 20:35:57
5	structural	dependency	依赖	源的变更会影响目标	依赖方→被依赖方	1	{}	4	1	2026-11-26 20:35:57
6	structural	realization	实现	类实现接口或契约规则	实现方→契约	1	{}	5	1	2026-11-26 20:35:57
7	semantic	kinship	亲属	父子/配偶等亲属语义，如 father_of、spouse_of	主体→客体	1	{}	72	1	2026-11-26 20:35:57
8	semantic	part_of	组成	部分属于整体	部分→整体	1	{}	73	1	2026-11-26 20:35:57
9	semantic	ownership	归属	拥有者与被拥有物	拥有者→物	1	{}	74	1	2026-11-26 20:35:57
10	semantic	membership	成员	个体属于组织或群体	成员→组织	1	{}	75	1	2026-11-26 20:35:57
11	semantic	location	位置	对象或事件位于某地	对象→地点	1	{}	76	1	2026-11-26 20:35:57
12	semantic	causal	因果	原因导致结果	因→果	1	{}	77	1	2026-11-26 20:35:57
14	semantic	provenance	来源派生	结论派生自证据或数据	派生→来源	1	{}	79	1	2026-11-26 20:35:57
15	semantic	reference	引用	弱语义引用，不蕴含生命周期依赖	引用方→被引用方	1	{}	80	1	2026-11-26 20:35:57
16	mapping	node	实体映射	本体类映射到物理表/图节点	本体→物理	1	存量值	81	1	2026-11-26 20:35:57
17	mapping	edge	关系映射	关系映射到外键或边表	本体→物理	1	存量值	82	1	2026-11-26 20:35:57
18	mapping	property	属性映射	属性映射到字段	本体→物理	0	待开放	83	1	2026-11-26 20:35:57
19	mapping	event	事件映射	事件类型映射到事件表	本体→物理	0	待开放	84	1	2026-11-26 20:35:57
20	mapping	rule	规则映射	规则映射到校验逻辑或触发器	本体→物理	0	待开放	85	1	2026-11-26 20:35:57
21	mapping	alias	别名映射	同名异义消歧	本体→物理	0	待开放	86	1	2026-11-26 20:35:57
22	event_flow	before	早于	事件严格先于另一事件	前→后	1	{}	87	1	2026-11-26 20:35:57
23	event_flow	after	晚于	事件严格晚于另一事件	后→前	1	{}	88	1	2026-11-26 20:35:57
24	event_flow	overlaps	时间重叠	两事件区间部分交叉	双向	1	{}	89	1	2026-11-26 20:35:57
25	event_flow	during	期间	事件发生在另一事件期间	子→父	1	{}	90	1	2026-11-26 20:35:57
26	event_flow	contains	包含	事件包含另一事件	父→子	1	{}	91	1	2026-11-26 20:35:57
27	event_flow	meets	紧接	前事件结束即后事件开始	前→后	1	{}	92	1	2026-11-26 20:35:57
28	event_flow	causes	导致	因果驱动，前事件是原因	因→果	1	{}	93	1	2026-11-26 20:35:57
29	event_flow	triggers	触发	条件满足后触发事件	条件→事件	1	{}	94	1	2026-11-26 20:35:57
30	event_flow	enables	允许	前置事件使后置事件可执行	允许方→被执行方	1	{}	95	1	2026-11-26 20:35:57
31	event_flow	prevents	阻止	前置事件阻止后置事件	阻止方→被阻止方	1	{}	96	1	2026-11-26 20:35:57
32	event_flow	part_of	子事件	组合事件中的子步骤	子→父	1	{}	97	1	2026-11-26 20:35:57
34	dependency	derives_from	派生自	结论或数据来源于另一对象	派生→来源	1	{}	140	1	2026-11-26 20:35:57
35	dependency	conflicts_with	冲突	两个对象语义互斥，不能同时生效	双向	1	{}	141	1	2026-11-26 20:35:57
36	dependency	supersedes	取代	新版本覆盖旧版本	新→旧	1	{}	142	1	2026-11-26 20:35:57
37	dependency	replaces	替换	等价替换，语义不变	替代→原	1	{}	143	1	2026-11-26 20:35:57
38	dependency	validates	校验	规则校验某类或属性	规则→被校验对象	1	{}	144	1	2026-11-26 20:35:57
39	dependency	references	引用	弱依赖，仅引用不约束	引用方→被引用方	1	{}	145	1	2026-11-26 20:35:57
40	dependency	blocks	阻断	不满足则流程不能继续	阻断方→被阻断方	1	{}	146	1	2026-11-26 20:35:57
41	dependency	enables	启用	满足后启用另一对象	启用方→被启用方	1	{}	147	1	2026-11-26 20:35:57
42	cardinality	one	1..1	一对一，存量 one	—	1	存量值	180	1	2026-11-26 20:35:57
43	cardinality	many	1..N	一对多，存量 many	—	1	存量值	181	1	2026-11-26 20:35:57
44	cardinality	zero_or_one	0..1	零或一，等价于 one 且 nullable=1	—	0	用 one+nullable 表达	182	1	2026-11-26 20:35:57
45	cardinality	zero_or_many	0..N	零或多，等价于 many 且 nullable=1	—	0	用 many+nullable 表达	183	1	2026-11-26 20:35:57
46	version_relation	based_on	基于	当前版本基于某版本创建	新→旧	1	{}	184	1	2026-11-26 20:35:57
47	version_relation	supersedes	取代	当前版本取代前一版本	新→旧	1	{}	185	1	2026-11-26 20:35:57
48	version_relation	forked_from	分叉自	从某版本分出独立分支	分支→主干	1	{}	186	1	2026-11-26 20:35:57
49	version_relation	merges	合并自	由多个分支合并而来	合并→分支	1	{}	187	1	2026-11-26 20:35:57
50	version_relation	compatible_with	兼容	跨版本可互操作	双向	1	{}	188	1	2026-11-26 20:35:57
51	status	draft	草稿	编辑中，不对外生效	—	1	{}	190	1	2026-11-26 20:35:57
52	status	active	生效	正常可用，默认状态	—	1	存量值	191	1	2026-11-26 20:35:57
53	status	frozen	冻结	只读锁定，不可编辑	—	1	{}	192	1	2026-11-26 20:35:57
54	status	deprecated	废弃	不推荐新引用，检查时告警	—	1	{}	193	1	2026-11-26 20:35:57
55	status	archived	归档	历史保留，不参与查询	—	1	{}	194	1	2026-11-26 20:35:57
2	structural	association	关联	普通结构连接，无生命周期依赖	双向/单向	1	{}	1	1	2026-11-26 20:35:57
351	person_relation	parent_of	父母	主体是客体的父或母（泛化）	父母→子女	1	{}	8	1	2026-11-26 20:39:30
352	person_relation	son_of	儿子	主体是客体的儿子	子→父母	1	{}	9	1	2026-11-26 20:39:30
353	person_relation	daughter_of	女儿	主体是客体的女儿	女→父母	1	{}	10	1	2026-11-26 20:39:30
354	person_relation	child_of	子女	主体是客体的子女（泛化）	子女→父母	1	{}	11	1	2026-11-26 20:39:30
355	person_relation	spouse_of	配偶	主体与客体为夫妻	双向	1	存量值	12	1	2026-11-26 20:39:30
356	person_relation	husband_of	丈夫	主体是客体的丈夫	夫→妻	1	{}	13	1	2026-11-26 20:39:30
357	person_relation	wife_of	妻子	主体是客体的妻子	妻→夫	1	{}	14	1	2026-11-26 20:39:30
358	person_relation	sibling_of	兄弟姐妹	主体与客体为同辈手足	双向	1	存量值	15	1	2026-11-26 20:39:30
359	person_relation	brother_of	兄弟	主体是客体的兄弟	双向	1	{}	16	1	2026-11-26 20:39:30
360	person_relation	sister_of	姐妹	主体是客体的姐妹	双向	1	{}	17	1	2026-11-26 20:39:30
361	person_relation	grandparent_of	祖辈	主体是客体的祖父母（泛化）	祖→孙	1	存量值	18	1	2026-11-26 20:39:30
362	person_relation	grandfather_of	祖父	主体是客体的祖父	祖→孙	1	{}	19	1	2026-11-26 20:39:30
363	person_relation	grandmother_of	祖母	主体是客体的祖母	祖→孙	1	{}	20	1	2026-11-26 20:39:30
364	person_relation	grandson_of	孙子	主体是客体的孙子	孙→祖	1	{}	21	1	2026-11-26 20:39:30
365	person_relation	granddaughter_of	孙女	主体是客体的孙女	孙→祖	1	{}	22	1	2026-11-26 20:39:30
366	person_relation	uncle_of	叔伯	主体是客体的叔伯	叔伯→侄	1	{}	23	1	2026-11-26 20:39:30
367	person_relation	aunt_of	姑姨	主体是客体的姑姨	姑姨→侄	1	{}	24	1	2026-11-26 20:39:30
368	person_relation	nephew_of	侄子	主体是客体的侄子	侄→叔伯	1	{}	25	1	2026-11-26 20:39:30
369	person_relation	niece_of	侄女	主体是客体的侄女	侄→叔伯	1	{}	26	1	2026-11-26 20:39:30
371	person_relation	ancestor_of	祖先	主体是客体的直系祖先	祖→后	1	{}	28	1	2026-11-26 20:39:30
372	person_relation	descendant_of	后代	主体是客体的直系后代	后→祖	1	{}	29	1	2026-11-26 20:39:30
373	person_relation	mentor_of	师徒	主体是客体的师父/导师	师→徒	1	{}	30	1	2026-11-26 20:39:30
374	person_relation	friend_of	朋友	主体与客体为朋友	双向	1	{}	31	1	2026-11-26 20:39:30
375	person_relation	colleague_of	同事	主体与客体为同事	双向	1	{}	32	1	2026-11-26 20:39:30
376	belonging	belongs_to	属于	通用归属关系	对象→所属	1	存量值	33	1	2026-11-26 20:39:30
377	belonging	belongs_to_family	属于家族	人物属于某家族	人→家族	1	{}	34	1	2026-11-26 20:39:30
379	belonging	belongs_to_household	属于家庭	人物属于某户/家庭	人→家庭	1	{}	36	1	2026-11-26 20:39:30
380	belonging	belongs_to_clan	属于宗族	人物属于某宗族/姓氏分支	人→宗族	1	{}	37	1	2026-11-26 20:39:30
381	belonging	belongs_to_org	属于组织	人物属于某公司/机构	人→组织	1	{}	38	1	2026-11-26 20:39:30
382	belonging	belongs_to_dept	属于部门	人物属于某部门	人→部门	1	{}	39	1	2026-11-26 20:39:30
383	belonging	belongs_to_team	属于团队	人物属于某项目团队	人→团队	1	{}	40	1	2026-11-26 20:39:30
384	belonging	member_of	成员	个体是某群体的成员	成员→群体	1	{}	41	1	2026-11-26 20:39:30
385	belonging	leader_of	领导	主体领导某组织或团队	领导→组织	1	{}	42	1	2026-11-26 20:39:30
386	belonging	subordinate_of	下属	主体是某人的下属	下属→上级	1	{}	43	1	2026-11-26 20:39:30
387	belonging	founder_of	创立	主体创立了某组织	人→组织	1	{}	44	1	2026-11-26 20:39:30
388	belonging	owner_of	拥有	主体拥有某对象或资产	拥有者→物	1	{}	45	1	2026-11-26 20:39:30
389	belonging	affiliated_with	隶属	机构之间的隶属/挂靠关系	下级→上级	1	{}	46	1	2026-11-26 20:39:30
390	belonging	located_in	位于	对象位于某地点	对象→地点	1	{}	47	1	2026-11-26 20:39:30
391	belonging	resident_of	居住于	人物居住于某地	人→地点	1	{}	48	1	2026-11-26 20:39:30
392	belonging	native_of	祖籍	人物祖籍某地	人→地点	1	{}	49	1	2026-11-26 20:39:30
696	belonging	generation_of	辈分包含	辈分包含成员（反向 belongs_to_generation）	辈分→人	1	存量值	50	1	2026-11-26 20:49:18
697	belonging	join_project	参与项目	人员参与项目，如组织管理本体 a1→b1	人→项目	1	存量值	51	1	2026-11-26 20:49:18
698	belonging	participant_of	参与者	对象参与某活动/事件/项目	参与者→活动	1	{}	52	1	2026-11-26 20:49:18
699	person_relation	head_of	族长管辖	族长管辖族人	族长→族人	1	存量值	53	1	2026-11-26 20:49:18
700	person_relation	inherits_rank	继承爵位	族长爵位继承	继承者→前任	1	存量值	54	1	2026-11-26 20:49:18
701	person_relation	married_in	嫁入	人物通过婚姻加入某婚姻/家族	人→婚姻	1	存量值	55	1	2026-11-26 20:49:18
702	person_relation	father_in_law_of	岳父/公公	主体是客体的岳父或公公	长辈→晚辈	1	{}	56	1	2026-11-26 20:49:18
703	person_relation	mother_in_law_of	岳母/婆婆	主体是客体的岳母或婆婆	长辈→晚辈	1	{}	57	1	2026-11-26 20:49:18
56	status	disabled	停用	规则保留定义但不执行	—	1	{}	195	1	2026-11-26 20:35:57
57	status	broken	失效	映射指向的物理对象已不存在	—	1	{}	196	1	2026-11-26 20:35:57
350	person_relation	mother_of	母亲	主体是客体的母亲	母→子	1	存量值	7	1	2026-11-26 20:39:30
706	person_relation	stepfather_of	继父	主体是客体的继父	继父→继子	1	{}	60	1	2026-11-26 20:49:18
707	person_relation	stepmother_of	继母	主体是客体的继母	继母→继子	1	{}	61	1	2026-11-26 20:49:18
708	person_relation	adopted_child_of	养子女	主体是客体的养子女	养子女→养父母	1	{}	62	1	2026-11-26 20:49:18
709	person_relation	twin_of	双胞胎	主体与客体为双胞胎	双向	1	{}	63	1	2026-11-26 20:49:18
1522	time_stauts	before	早于	区间A结束早于区间B开始（不接触）	A→B	1	{}	98	1	2026-11-26 20:53:02
1523	time_stauts	after	晚于	区间A开始晚于区间B结束	A→B	1	{}	99	1	2026-11-26 20:53:02
1524	time_stauts	meets	紧接	A结束时刻等于B开始时刻	A→B	1	{}	100	1	2026-11-26 20:53:02
1525	time_stauts	met_by	被紧接	A开始时刻等于B结束时刻	A→B	1	{}	101	1	2026-11-26 20:53:02
1526	time_stauts	overlaps	重叠	A开始早于B且部分覆盖B	A→B	1	{}	102	1	2026-11-26 20:53:02
1527	time_stauts	overlapped_by	被重叠	B开始早于A且部分覆盖A	A→B	1	{}	103	1	2026-11-26 20:53:02
1528	time_stauts	during	期间	A完全位于B的时间区间内	A→B	1	{}	104	1	2026-11-26 20:53:02
1529	time_stauts	contains	包含	A的时间区间完全包含B	A→B	1	{}	105	1	2026-11-26 20:53:02
1530	time_stauts	starts	同时开始	A与B开始时刻相同但A先结束	A→B	1	{}	106	1	2026-11-26 20:53:02
1531	time_stauts	started_by	被同时开始	B与A开始时刻相同但B先结束	A→B	1	{}	107	1	2026-11-26 20:53:02
1532	time_stauts	finishes	同时结束	A与B结束时刻相同但A开始更晚	A→B	1	{}	108	1	2026-11-26 20:53:02
1533	time_stauts	finished_by	被同时结束	B与A结束时刻相同但B开始更晚	A→B	1	{}	109	1	2026-11-26 20:53:02
1534	time_stauts	equal	相等	A与B时间区间完全相同	双向	1	{}	110	1	2026-11-26 20:53:02
1535	time_stauts	same_time	同时	两时间点相同	双向	1	{}	111	1	2026-11-26 20:53:02
1536	time_stauts	concurrent_with	并发	时间上并行发生，无先后因果	双向	1	{}	112	1	2026-11-26 20:53:02
1538	time_stauts	valid_before	先于生效	对象在另一对象生效之前有效	A→B	1	{}	114	1	2026-11-26 20:53:02
1539	time_stauts	valid_after	后于生效	对象在另一对象生效之后有效	A→B	1	{}	115	1	2026-11-26 20:53:02
1540	time_stauts	supersedes_time	时效取代	新有效期覆盖旧有效期（同实体）	新→旧	1	{}	116	1	2026-11-26 20:53:02
1541	time_stauts	overlaps_valid	有效期重叠	两对象有效期存在交叉（检查告警）	双向	1	{}	117	1	2026-11-26 20:53:02
1542	status_relation	transitions_to	迁移至	状态A可转移到状态B	A→B	1	{}	121	1	2026-11-26 20:53:02
1543	status_relation	requires_state	状态前提	对象生效要求另一对象处于某状态	对象→对象状态	1	{}	122	1	2026-11-26 20:53:02
1544	status_relation	depends_on_state	状态依赖	本对象状态依赖另一对象状态	对象→对象	1	{}	123	1	2026-11-26 20:53:02
1545	status_relation	gated_by_state	状态门控	另一对象的状态作为开关门控	门控→被门控	1	{}	124	1	2026-11-26 20:53:02
1546	status_relation	excludes_state	状态互斥	两个状态不能同时成立	双向	1	{}	125	1	2026-11-26 20:53:02
1547	status_relation	coexists_with	状态共存	两个状态可以同时成立	双向	1	{}	126	1	2026-11-26 20:53:02
746	dependency	constrains	约束	限制另一对象的取值范围或行为	约束方→被约束方	1	{}	149	1	2026-11-26 20:49:18
747	dependency	triggers	触发	条件满足时触发另一对象执行	触发方→被触发方	1	{}	150	1	2026-11-26 20:49:18
748	dependency	inhibits	抑制	压制或降低另一对象的生效	抑制方→被抑制方	1	{}	151	1	2026-11-26 20:49:18
749	dependency	guards	守卫	作为前置守卫条件，通过后才继续	守卫→被守卫	1	{}	152	1	2026-11-26 20:49:18
750	dependency	overrides	覆盖	运行时覆盖另一对象的定义（区别于版本 supersedes）	覆盖方→被覆盖方	1	{}	153	1	2026-11-26 20:49:18
751	dependency	co_depends_on	互相依赖	两个对象互相依赖，形成环需检查	双向	1	{}	154	1	2026-11-26 20:49:18
752	dependency	affects	影响	源变化会影响目标，弱于 depends_on	影响方→被影响方	1	{}	155	1	2026-11-26 20:49:18
753	dependency	governs	支配	规则/策略支配某对象的行为	规则→对象	1	{}	156	1	2026-11-26 20:49:18
754	dependency	implements	实现契约	对象实现某接口/契约规则	实现方→契约	1	{}	157	1	2026-11-26 20:49:18
755	dependency	consumes	消费	对象消费另一对象提供的资源	消费方→资源	1	{}	158	1	2026-11-26 20:49:18
756	dependency	provides	提供	对象向另一对象提供资源/能力	提供方→消费方	1	{}	159	1	2026-11-26 20:49:18
1154	scope	domain	领域本体	领域级共享本体，对全空间可见	—	1	存量值	197	1	2026-11-26 20:50:43
1155	scope	personal	个人本体	个人私有本体，仅创建者可见	—	1	{}	198	1	2026-11-26 20:50:43
1156	authority	normal	普通	默认权威等级	—	1	存量值	199	1	2026-11-26 20:50:43
1157	authority	high	高权威	跨本体合并冲突时优先采用该本体定义	—	1	存量值	200	1	2026-11-26 20:50:43
1158	datasource_type	builtin-demo	内置示例	内置演示数据（非真实图谱）	—	1	存量值	201	1	2026-11-26 20:50:43
1159	datasource_type	graph-ref	图谱引用	引用知识图谱实例（按被引用图谱 db_type 决定 SQL/N4）	—	1	存量值	202	1	2026-11-26 20:50:43
1160	datasource_type	neo4j	Neo4j	直连 Neo4j 图数据库	—	1	{}	203	1	2026-11-26 20:50:43
1161	datasource_type	sql	SQL	直连关系数据库	—	1	{}	204	1	2026-11-26 20:50:43
705	person_relation	daughter_in_law_of	儿媳	主体是客体的儿媳	儿媳→婆家	1	{}	59	1	2026-11-26 20:49:18
4432	person_relation	ex_husband_of	前夫	主体是客体的前夫	前夫→前妻	1	规范:husband_of+ended	66	1	2026-11-26 21:03:07
4433	person_relation	divorced_from	离婚	主体与客体已解除婚姻关系	双向	1	{}	67	1	2026-11-26 21:03:07
4434	person_relation	separated_from	分居	主体与客体分居但婚姻未解除	双向	1	{}	68	1	2026-11-26 21:03:07
4435	person_relation	remarried_with	再婚	主体与客体在各自前段婚姻结束后再婚	双向	1	{}	69	1	2026-11-26 21:03:07
4436	person_relation	ex_father_in_law_of	前岳父/公公	主体曾是客体的岳父或公公	长辈→晚辈	1	{}	70	1	2026-11-26 21:03:07
4437	person_relation	ex_mother_in_law_of	前岳母/婆婆	主体曾是客体的岳母或婆婆	长辈→晚辈	1	{}	71	1	2026-11-26 21:03:07
5002	semantic	time_stauts	时序	时间先后关系	先→后	1	{}	78	1	2026-11-26 21:06:20
2050	time_stauts	ends_at	结束时间	对象/事件的终止时刻（对应 valid_to / end_time 字段）	对象→时间点	1	{}	119	1	2026-11-26 20:55:04
2051	time_stauts	between	介于…之间	时间点/对象落在指定的起止时间之间（需配置上下界）	对象→[起,止]	1	{}	120	1	2026-11-26 20:55:04
1548	status_relation	precedes_state	状态先于	状态A必须先于状态B出现	A→B	1	{}	127	1	2026-11-26 20:53:02
1549	status_relation	invalidates	使失效	进入状态A导致对象B失效	A→B	1	{}	128	1	2026-11-26 20:53:02
1550	status_relation	activates	激活	状态A触发对象B进入生效状态	A→B	1	{}	129	1	2026-11-26 20:53:02
1551	status_relation	suspends	暂停	状态A使对象B临时停止	A→B	1	{}	130	1	2026-11-26 20:53:02
1552	status_relation	restores	恢复	状态A使对象B恢复到先前状态	A→B	1	{}	131	1	2026-11-26 20:53:02
1553	status_relation	supersedes_state	状态取代	新状态覆盖旧状态定义	新→旧	1	{}	132	1	2026-11-26 20:53:02
1554	status_relation	inherits_state	状态继承	子类状态定义继承父类	子→父	1	{}	133	1	2026-11-26 20:53:02
1555	status_relation	conflicts_state	状态冲突	两状态定义存在语义冲突	双向	1	{}	134	1	2026-11-26 20:53:02
4501	status_relation	terminates	终止	对象A的生效导致关系B终止，如离婚终止婚姻（配 valid_to）	A→B	1	{}	135	1	2026-11-26 21:03:07
4502	status_relation	terminated_by	被终止	关系B因对象A而终止（terminates 反向）	B→A	1	{}	136	1	2026-11-26 21:03:07
4503	status_relation	expires	到期	有效期届满后关系自动失效	对象→关系	1	{}	137	1	2026-11-26 21:03:07
4504	status_relation	revokes	撤销	显式撤销先前生效的关系/授权	撤销方→被撤销	1	{}	138	1	2026-11-26 21:03:07
5828	rule_kind	constraint	约束规则	限制类/属性/关系的取值或基数，违反则报错	—	1	{}	160	1	2026-11-26 21:08:06
5829	rule_kind	inference	推理规则	IF-THEN 推导出新结论或新关系	—	1	{}	161	1	2026-11-26 21:08:06
5830	rule_kind	trigger	触发规则	条件满足时触发动作或状态变更	—	1	{}	162	1	2026-11-26 21:08:06
5831	rule_kind	validation	校验规则	校验数据合法性（格式/范围/枚举）	—	1	{}	163	1	2026-11-26 21:08:06
5832	rule_kind	derivation	派生规则	由源属性计算出派生属性	—	1	{}	164	1	2026-11-26 21:08:06
5833	rule_kind	access_control	权限规则	控制对象的读写访问权限	—	1	{}	165	1	2026-11-26 21:08:06
5834	rule_kind	quality	质量规则	数据质量标准（完整/一致/唯一）	—	1	{}	166	1	2026-11-26 21:08:06
5835	rule_kind	temporal_rule	时效规则	基于有效时间范围的规则	—	1	{}	167	1	2026-11-26 21:08:06
5836	rule_relation	composes	组合	多条规则组合成一条复合规则	部分→整体	1	{}	168	1	2026-11-26 21:08:06
5837	rule_relation	part_of	子规则	本规则是某复合规则的一部分	子→父	1	{}	169	1	2026-11-26 21:08:06
5838	rule_relation	mutually_exclusive	互斥	两规则不能同时生效	双向	1	{}	170	1	2026-11-26 21:08:06
5839	rule_relation	has_priority	优先级	规则B的优先级高于规则A	低→高	1	{}	171	1	2026-11-26 21:08:06
5840	rule_relation	overrides	覆盖	高优先级规则覆盖低优先级规则	覆盖方→被覆盖方	1	{}	172	1	2026-11-26 21:08:06
5841	rule_relation	derives	推导	本规则由另一规则推导而来	派生→来源	1	{}	173	1	2026-11-26 21:08:06
5842	rule_relation	conflicts	冲突	两规则结论矛盾，需一致性检查告警	双向	1	{}	174	1	2026-11-26 21:08:06
5843	rule_relation	depends_on	依赖	本规则生效依赖另一规则	依赖方→被依赖方	1	{}	175	1	2026-11-26 21:08:06
5844	rule_relation	validates	校验	本规则校验另一规则的输入/输出	校验方→被校验方	1	{}	176	1	2026-11-26 21:08:06
5845	rule_relation	supersedes	取代	新版本规则取代旧版本	新→旧	1	{}	177	1	2026-11-26 21:08:06
5846	rule_relation	refines	细化	本规则是另一规则的细化特例	细化→被细化	1	{}	178	1	2026-11-26 21:08:06
5847	rule_relation	generalizes	泛化	本规则是另一规则的泛化	泛化→被泛化	1	{}	179	1	2026-11-26 21:08:06
3131	status	new	新建	刚创建，尚未正式提交或编辑	—	1	{}	189	1	2026-11-26 20:57:26
2627	datasource_type	postgresql	PostgreSQL	知识图谱 db_type 的实际取值（SQL 关系库）	—	1	alias:sql	205	1	2026-11-26 20:56:39
4431	person_relation	ex_wife_of	前妻	主体是客体的前妻	前妻→前夫	1	规范:wife_of+ended	65	1	2026-11-26 21:03:07
6493	data_type	text	长文本	不限长度文本，如备注、正文	—	1	{}	207	1	2026-11-26 21:28:25
6494	data_type	integer	整数	整数类型	—	1	{}	208	1	2026-11-26 21:28:25
6495	data_type	decimal	小数	定点小数，金额/精度敏感场景	—	1	{}	209	1	2026-11-26 21:28:25
6496	data_type	float	浮点数	单精度浮点	—	1	{}	210	1	2026-11-26 21:28:25
6497	data_type	double	双精度	双精度浮点	—	1	{}	211	1	2026-11-26 21:28:25
6492	data_type	string	字符串	定长/变长文本	—	1	{}	206	1	2026-11-26 21:28:25
6499	data_type	date	日期	仅日期，ISO 8601 YYYY-MM-DD	—	1	ISO8601	213	1	2026-11-26 21:28:25
6505	data_type	year_month	年月	YYYY-MM，如 2026-11	—	1	{}	219	1	2026-11-26 21:28:25
6506	data_type	enum	枚举	从维度表/枚举集中取值	—	1	{}	220	1	2026-11-26 21:28:25
6507	data_type	ref	引用	引用另一个类的实例（外键语义）	—	1	{}	221	1	2026-11-26 21:28:25
6508	data_type	json	JSON	结构化 JSON 对象/数组	—	1	{}	222	1	2026-11-26 21:28:25
6509	data_type	array	数组	同类型值列表	—	1	{}	223	1	2026-11-26 21:28:25
6510	data_type	blob	二进制	字节流/文件	—	1	{}	224	1	2026-11-26 21:28:25
6512	nullability	required	必填	不允许为空，必须提供值	—	1	nullable=0	226	1	2026-11-26 21:28:25
6513	nullability	optional	可选	允许为空，但非空时必须合法	—	1	nullable=1	227	1	2026-11-26 21:28:25
6514	nullability	not_null	非空	显式 NOT NULL 约束	—	1	{}	228	1	2026-11-26 21:28:25
6515	nullability	nullable	可空	显式允许 NULL	—	1	{}	229	1	2026-11-26 21:28:25
6516	nullability	not_applicable	不适用	该属性在特定上下文无意义	—	1	{}	230	1	2026-11-26 21:28:25
6517	nullability	conditionally_required	条件必填	满足特定条件时必填	—	1	{}	231	1	2026-11-26 21:28:25
6518	value_presence	present	有值	字段存在且包含有效值	—	1	{}	232	1	2026-11-26 21:28:25
6519	value_presence	absent	缺失	字段未出现在数据中	—	1	{}	233	1	2026-11-26 21:28:25
6520	value_presence	null	空值NULL	字段存在但值为 NULL	—	1	{}	234	1	2026-11-26 21:28:25
6521	value_presence	empty_string	空字符串	字段存在但为空字符串	—	1	{}	235	1	2026-11-26 21:28:25
6522	value_presence	empty_collection	空集合	字段存在但数组/集合为空	—	1	{}	236	1	2026-11-26 21:28:25
6523	value_presence	defaulted	取默认值	未提供值，采用定义中的默认值	—	1	{}	237	1	2026-11-26 21:28:25
6524	value_presence	unknown	未知	值来源不明或尚未采集	—	1	{}	238	1	2026-11-26 21:28:25
6525	uniqueness	unique	唯一	取值在范围内不重复	—	1	{}	239	1	2026-11-26 21:28:25
6526	uniqueness	non_unique	可重复	允许重复值	—	1	{}	240	1	2026-11-26 21:28:25
6527	uniqueness	primary_key	主键	唯一且非空，标识实体	—	1	{}	241	1	2026-11-26 21:28:25
6528	uniqueness	foreign_key	外键	引用另一实体的主键	—	1	{}	242	1	2026-11-26 21:28:25
6529	uniqueness	business_key	业务键	业务上唯一标识，可能非物理主键	—	1	{}	243	1	2026-11-26 21:28:25
6530	uniqueness	scoped_unique	范围内唯一	在特定范围（如父对象内）唯一	—	1	{}	244	1	2026-11-26 21:28:25
6531	uniqueness	compound_unique	联合唯一	多属性组合唯一	—	1	{}	245	1	2026-11-26 21:28:25
1	structural	inheritance	继承	is-a，子类继承父类的属性与关系，对应存量 parent_name	子类→父类	1	{}	0	1	2026-11-26 20:35:57
349	person_relation	father_of	父亲	主体是客体的父亲	父→子	1	存量值	6	1	2026-11-26 20:39:30
370	person_relation	cousin_of	堂表兄弟姐妹	主体与客体为堂表同辈	双向	1	{}	27	1	2026-11-26 20:39:30
378	belonging	belongs_to_generation	属于辈分	人物属于某辈分，如家族族谱	人→辈分	1	存量值	35	1	2026-11-26 20:39:30
704	person_relation	son_in_law_of	女婿	主体是客体的女婿	女婿→岳家	1	{}	58	1	2026-11-26 20:49:18
4430	person_relation	ex_spouse_of	前配偶	主体与客体曾为配偶，现已终止（泛化）	双向	1	规范:spouse_of+ended	64	1	2026-11-26 21:03:07
1537	time_stauts	valid_during	有效于	数据在该时间段内有效（valid_from/to）	对象→时间段	1	{}	113	1	2026-11-26 20:53:02
2049	time_stauts	starts_at	开始时间	对象/事件的起始时刻（对应 valid_from / start_time 字段）	对象→时间点	1	{}	118	1	2026-11-26 20:55:04
33	dependency	depends_on	依赖于	当前对象生效依赖另一对象	依赖方→被依赖方	1	{}	139	1	2026-11-26 20:35:57
745	dependency	requires	必需依赖	强依赖：缺少则当前对象无法生效（区别于 depends_on 弱依赖）	依赖方→被依赖方	1	{}	148	1	2026-11-26 20:49:18
6498	data_type	boolean	布尔	true/false	—	1	{}	212	1	2026-11-26 21:28:25
6500	data_type	time	时间	仅时刻，ISO 8601 HH:mm:ss，无日期	—	1	ISO8601	214	1	2026-11-26 21:28:25
6501	data_type	datetime	日期时间	日期+时间，无时区，YYYY-MM-DD HH:mm:ss	—	1	ISO8601	215	1	2026-11-26 21:28:25
6502	data_type	timestamp	时间戳	日期+时间+时区，绝对时刻	—	1	ISO8601	216	1	2026-11-26 21:28:25
6503	data_type	duration	时长	时间段，如 P1D / 3 小时	—	1	ISO8601	217	1	2026-11-26 21:28:25
6504	data_type	year	年份	仅年份，如 2026	—	1	{}	218	1	2026-11-26 21:28:25
6511	data_type	uuid	UUID	全局唯一标识符	—	1	{}	225	1	2026-11-26 21:28:25
\.


--
-- Data for Name: tb_onto_class; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_onto_class (id, ontology_id, name, parent_name, comment) FROM stdin;
1	1	c0		部门
2	1	a1		员工
3	1	b1		项目
4	1	c1		外部组织
14	7	person		家族成员，含姓名/性别/出生年/状态/职业
15	7	male		万家男子，名字按辈分字：嘉运乾坤增长
16	7	female		万家女子，命名不限辈分字
17	7	generation		辈分层：嘉→运→乾→坤→增→长（上下六代）
18	7	patriarch		族长/家长，负责家族事务
19	7	marriage		婚姻事件，联结男女双方
20	7	g1_jia		第一代·嘉字辈
21	7	g2_yun		第二代·运字辈
22	7	g3_qian		第三代·乾字辈
23	7	g4_kun		第四代·坤字辈
24	7	g5_zeng		第五代·增字辈
25	7	g6_zhang		第六代·长字辈
\.


--
-- Data for Name: tb_onto_mapping; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_onto_mapping (id, ontology_id, onto_type, physical_type, kind) FROM stdin;
1	1	c0	c0	node
2	1	a1	a1	node
3	1	belongs_to	works_in	edge
5	7	person	人物	node
6	7	male	人物	node
7	7	female	人物	node
8	7	generation	辈分	node
9	7	father_of	父子	edge
10	7	mother_of	母子	edge
11	7	spouse_of	夫妻	edge
12	7	sibling_of	兄弟姐妹	edge
13	7	grandparent_of	祖孙	edge
14	7	belongs_to_generation	属于辈分	edge
\.


--
-- Data for Name: tb_onto_rel; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_onto_rel (id, ontology_id, name, subj_class, obj_class, cardinality, nullable, inherits_from, comment) FROM stdin;
1	1	belongs_to	a1	c0	one	0		
2	1	join_project	a1	b1	many	1		
9	7	father_of	person	person	many	1		父子（父亲→子女）
10	7	mother_of	person	person	many	1		母子（母亲→子女）
11	7	spouse_of	person	person	many	1		夫妻
12	7	sibling_of	person	person	many	1		兄弟姐妹
13	7	grandparent_of	person	person	many	1		祖孙
14	7	belongs_to_generation	person	generation	many	1		人物归属辈分
15	7	head_of	patriarch	person	many	1		族长管辖
16	7	married_in	person	marriage	many	1		婚姻事件参与
17	7	inherits_rank	patriarch	patriarch	many	1		族长继承
18	7	generation_of	generation	person	many	1		辈分包含成员
\.


--
-- Data for Name: tb_onto_space; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_onto_space (id, name, description, created_at) FROM stdin;
1	默认空间	系统自动创建	2026-11-19 22:57:55
5	子墨-本体空间	子墨-本体空间	2026-11-23 15:00:40
7	子墨-本体图谱	家族族谱等本体定义	2026-11-23 15:37:07
9	家族-本体图谱	家族-本体图谱	2026-11-23 15:49:48
\.


--
-- Data for Name: tb_onto_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_onto_version (id, ontology_id, version_no, op, note, snapshot, created_at) FROM stdin;
8	1	1	update_class	修改类 c0	{"ontology": {"id": 1, "name": "o1-组织管理", "scope": "domain", "namespace": "o1-组织管理", "authority": "high", "version": "v1", "status": "active", "comment": "", "created_at": "2026-11-17 12:01:14", "space_id": 1}, "classes": [{"id": 1, "ontology_id": 1, "name": "c0", "parent_name": "", "comment": "部门E2E临时说明"}, {"id": 2, "ontology_id": 1, "name": "a1", "parent_name": "", "comment": "员工"}, {"id": 3, "ontology_id": 1, "name": "b1", "parent_name": "", "comment": "项目"}, {"id": 4, "ontology_id": 1, "name": "c1", "parent_name": "", "comment": "外部组织"}], "rels": [{"id": 1, "ontology_id": 1, "name": "belongs_to", "subj_class": "a1", "obj_class": "c0", "cardinality": "one", "nullable": 0, "inherits_from": "", "comment": ""}, {"id": 2, "ontology_id": 1, "name": "join_project", "subj_class": "a1", "obj_class": "b1", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": ""}], "mappings": [{"id": 1, "ontology_id": 1, "onto_type": "c0", "physical_type": "c0", "kind": "node"}, {"id": 2, "ontology_id": 1, "onto_type": "a1", "physical_type": "a1", "kind": "node"}, {"id": 3, "ontology_id": 1, "onto_type": "belongs_to", "physical_type": "works_in", "kind": "edge"}]}	2026-11-23 15:15:12
9	1	2	update_class	修改类 c0	{"ontology": {"id": 1, "name": "o1-组织管理", "scope": "domain", "namespace": "o1-组织管理", "authority": "high", "version": "v1", "status": "active", "comment": "", "created_at": "2026-11-17 12:01:14", "space_id": 1}, "classes": [{"id": 1, "ontology_id": 1, "name": "c0", "parent_name": "", "comment": "部门"}, {"id": 2, "ontology_id": 1, "name": "a1", "parent_name": "", "comment": "员工"}, {"id": 3, "ontology_id": 1, "name": "b1", "parent_name": "", "comment": "项目"}, {"id": 4, "ontology_id": 1, "name": "c1", "parent_name": "", "comment": "外部组织"}], "rels": [{"id": 1, "ontology_id": 1, "name": "belongs_to", "subj_class": "a1", "obj_class": "c0", "cardinality": "one", "nullable": 0, "inherits_from": "", "comment": ""}, {"id": 2, "ontology_id": 1, "name": "join_project", "subj_class": "a1", "obj_class": "b1", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": ""}], "mappings": [{"id": 1, "ontology_id": 1, "onto_type": "c0", "physical_type": "c0", "kind": "node"}, {"id": 2, "ontology_id": 1, "onto_type": "a1", "physical_type": "a1", "kind": "node"}, {"id": 3, "ontology_id": 1, "onto_type": "belongs_to", "physical_type": "works_in", "kind": "edge"}]}	2026-11-23 15:15:24
10	1	3	pre_restore	恢复到 v2 前自动保存	{"ontology": {"id": 1, "name": "o1-组织管理", "scope": "domain", "namespace": "o1-组织管理", "authority": "high", "version": "v1", "status": "active", "comment": "", "created_at": "2026-11-17 12:01:14", "space_id": 1}, "classes": [{"id": 1, "ontology_id": 1, "name": "c0", "parent_name": "", "comment": "部门"}, {"id": 2, "ontology_id": 1, "name": "a1", "parent_name": "", "comment": "员工"}, {"id": 3, "ontology_id": 1, "name": "b1", "parent_name": "", "comment": "项目"}, {"id": 4, "ontology_id": 1, "name": "c1", "parent_name": "", "comment": "外部组织"}], "rels": [{"id": 1, "ontology_id": 1, "name": "belongs_to", "subj_class": "a1", "obj_class": "c0", "cardinality": "one", "nullable": 0, "inherits_from": "", "comment": ""}, {"id": 2, "ontology_id": 1, "name": "join_project", "subj_class": "a1", "obj_class": "b1", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": ""}], "mappings": [{"id": 1, "ontology_id": 1, "onto_type": "c0", "physical_type": "c0", "kind": "node"}, {"id": 2, "ontology_id": 1, "onto_type": "a1", "physical_type": "a1", "kind": "node"}, {"id": 3, "ontology_id": 1, "onto_type": "belongs_to", "physical_type": "works_in", "kind": "edge"}]}	2026-11-23 15:15:26
11	1	4	restore	恢复到 v2	{"ontology": {"id": 1, "name": "o1-组织管理", "scope": "domain", "namespace": "o1-组织管理", "authority": "high", "version": "v1", "status": "active", "comment": "", "created_at": "2026-11-17 12:01:14", "space_id": 1}, "classes": [{"id": 1, "ontology_id": 1, "name": "c0", "parent_name": "", "comment": "部门"}, {"id": 2, "ontology_id": 1, "name": "a1", "parent_name": "", "comment": "员工"}, {"id": 3, "ontology_id": 1, "name": "b1", "parent_name": "", "comment": "项目"}, {"id": 4, "ontology_id": 1, "name": "c1", "parent_name": "", "comment": "外部组织"}], "rels": [{"id": 1, "ontology_id": 1, "name": "belongs_to", "subj_class": "a1", "obj_class": "c0", "cardinality": "one", "nullable": 0, "inherits_from": "", "comment": ""}, {"id": 2, "ontology_id": 1, "name": "join_project", "subj_class": "a1", "obj_class": "b1", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": ""}], "mappings": [{"id": 1, "ontology_id": 1, "onto_type": "c0", "physical_type": "c0", "kind": "node"}, {"id": 2, "ontology_id": 1, "onto_type": "a1", "physical_type": "a1", "kind": "node"}, {"id": 3, "ontology_id": 1, "onto_type": "belongs_to", "physical_type": "works_in", "kind": "edge"}]}	2026-11-23 15:15:26
12	7	1	create_onto	创建本体 万家家族族谱	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [], "rels": [], "mappings": []}	2026-11-23 15:37:07
13	7	2	create_class	新增类 person	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
14	7	3	create_class	新增类 male	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
15	7	4	create_class	新增类 female	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
16	7	5	create_class	新增类 generation	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
17	7	6	create_class	新增类 patriarch	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
18	7	7	create_class	新增类 marriage	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
19	7	8	create_class	新增类 g1_jia	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
20	7	9	create_class	新增类 g2_yun	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
21	7	10	create_class	新增类 g3_qian	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
22	7	11	create_class	新增类 g4_kun	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
23	7	12	create_class	新增类 g5_zeng	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
24	7	13	create_class	新增类 g6_zhang	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [], "mappings": []}	2026-11-23 15:37:07
25	7	14	create_rel	新增关系 father_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}], "mappings": []}	2026-11-23 15:37:07
26	7	15	create_rel	新增关系 mother_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}], "mappings": []}	2026-11-23 15:37:07
27	7	16	create_rel	新增关系 spouse_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}], "mappings": []}	2026-11-23 15:37:07
28	7	17	create_rel	新增关系 sibling_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}], "mappings": []}	2026-11-23 15:37:07
29	7	18	create_rel	新增关系 grandparent_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}], "mappings": []}	2026-11-23 15:37:07
30	7	19	create_rel	新增关系 belongs_to_generation	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}], "mappings": []}	2026-11-23 15:37:07
31	7	20	create_rel	新增关系 head_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}], "mappings": []}	2026-11-23 15:37:07
32	7	21	create_rel	新增关系 married_in	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}], "mappings": []}	2026-11-23 15:37:07
33	7	22	create_rel	新增关系 inherits_rank	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}], "mappings": []}	2026-11-23 15:37:07
34	7	23	create_rel	新增关系 generation_of	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": []}	2026-11-23 15:37:07
35	7	24	create_mapping	绑定映射 person -> 人物	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}]}	2026-11-23 15:40:15
36	7	25	create_mapping	绑定映射 male -> 人物	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}]}	2026-11-23 15:40:15
37	7	26	create_mapping	绑定映射 female -> 人物	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}]}	2026-11-23 15:40:15
38	7	27	create_mapping	绑定映射 generation -> 辈分	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}]}	2026-11-23 15:40:15
39	7	28	create_mapping	绑定映射 father_of -> 父子	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}, {"id": 9, "ontology_id": 7, "onto_type": "father_of", "physical_type": "父子", "kind": "edge"}]}	2026-11-23 15:40:15
40	7	29	create_mapping	绑定映射 mother_of -> 母子	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}, {"id": 9, "ontology_id": 7, "onto_type": "father_of", "physical_type": "父子", "kind": "edge"}, {"id": 10, "ontology_id": 7, "onto_type": "mother_of", "physical_type": "母子", "kind": "edge"}]}	2026-11-23 15:40:15
41	7	30	create_mapping	绑定映射 spouse_of -> 夫妻	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}, {"id": 9, "ontology_id": 7, "onto_type": "father_of", "physical_type": "父子", "kind": "edge"}, {"id": 10, "ontology_id": 7, "onto_type": "mother_of", "physical_type": "母子", "kind": "edge"}, {"id": 11, "ontology_id": 7, "onto_type": "spouse_of", "physical_type": "夫妻", "kind": "edge"}]}	2026-11-23 15:40:15
42	7	31	create_mapping	绑定映射 sibling_of -> 兄弟姐妹	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}, {"id": 9, "ontology_id": 7, "onto_type": "father_of", "physical_type": "父子", "kind": "edge"}, {"id": 10, "ontology_id": 7, "onto_type": "mother_of", "physical_type": "母子", "kind": "edge"}, {"id": 11, "ontology_id": 7, "onto_type": "spouse_of", "physical_type": "夫妻", "kind": "edge"}, {"id": 12, "ontology_id": 7, "onto_type": "sibling_of", "physical_type": "兄弟姐妹", "kind": "edge"}]}	2026-11-23 15:40:15
43	7	32	create_mapping	绑定映射 grandparent_of -> 祖孙	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}, {"id": 9, "ontology_id": 7, "onto_type": "father_of", "physical_type": "父子", "kind": "edge"}, {"id": 10, "ontology_id": 7, "onto_type": "mother_of", "physical_type": "母子", "kind": "edge"}, {"id": 11, "ontology_id": 7, "onto_type": "spouse_of", "physical_type": "夫妻", "kind": "edge"}, {"id": 12, "ontology_id": 7, "onto_type": "sibling_of", "physical_type": "兄弟姐妹", "kind": "edge"}, {"id": 13, "ontology_id": 7, "onto_type": "grandparent_of", "physical_type": "祖孙", "kind": "edge"}]}	2026-11-23 15:40:15
44	7	33	create_mapping	绑定映射 belongs_to_generation -> 属于辈分	{"ontology": {"id": 7, "name": "万家家族族谱", "scope": "domain", "namespace": "urn:wan-family", "authority": "high", "version": "v1", "status": "active", "comment": "万家六代族谱本体：人物/辈分/亲属关系定义", "created_at": "2026-11-23 15:37:07", "space_id": 7}, "classes": [{"id": 14, "ontology_id": 7, "name": "person", "parent_name": "", "comment": "家族成员，含姓名/性别/出生年/状态/职业"}, {"id": 15, "ontology_id": 7, "name": "male", "parent_name": "", "comment": "万家男子，名字按辈分字：嘉运乾坤增长"}, {"id": 16, "ontology_id": 7, "name": "female", "parent_name": "", "comment": "万家女子，命名不限辈分字"}, {"id": 17, "ontology_id": 7, "name": "generation", "parent_name": "", "comment": "辈分层：嘉→运→乾→坤→增→长（上下六代）"}, {"id": 18, "ontology_id": 7, "name": "patriarch", "parent_name": "", "comment": "族长/家长，负责家族事务"}, {"id": 19, "ontology_id": 7, "name": "marriage", "parent_name": "", "comment": "婚姻事件，联结男女双方"}, {"id": 20, "ontology_id": 7, "name": "g1_jia", "parent_name": "", "comment": "第一代·嘉字辈"}, {"id": 21, "ontology_id": 7, "name": "g2_yun", "parent_name": "", "comment": "第二代·运字辈"}, {"id": 22, "ontology_id": 7, "name": "g3_qian", "parent_name": "", "comment": "第三代·乾字辈"}, {"id": 23, "ontology_id": 7, "name": "g4_kun", "parent_name": "", "comment": "第四代·坤字辈"}, {"id": 24, "ontology_id": 7, "name": "g5_zeng", "parent_name": "", "comment": "第五代·增字辈"}, {"id": 25, "ontology_id": 7, "name": "g6_zhang", "parent_name": "", "comment": "第六代·长字辈"}], "rels": [{"id": 9, "ontology_id": 7, "name": "father_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "父子（父亲→子女）"}, {"id": 10, "ontology_id": 7, "name": "mother_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "母子（母亲→子女）"}, {"id": 11, "ontology_id": 7, "name": "spouse_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "夫妻"}, {"id": 12, "ontology_id": 7, "name": "sibling_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "兄弟姐妹"}, {"id": 13, "ontology_id": 7, "name": "grandparent_of", "subj_class": "person", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "祖孙"}, {"id": 14, "ontology_id": 7, "name": "belongs_to_generation", "subj_class": "person", "obj_class": "generation", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "人物归属辈分"}, {"id": 15, "ontology_id": 7, "name": "head_of", "subj_class": "patriarch", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长管辖"}, {"id": 16, "ontology_id": 7, "name": "married_in", "subj_class": "person", "obj_class": "marriage", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "婚姻事件参与"}, {"id": 17, "ontology_id": 7, "name": "inherits_rank", "subj_class": "patriarch", "obj_class": "patriarch", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "族长继承"}, {"id": 18, "ontology_id": 7, "name": "generation_of", "subj_class": "generation", "obj_class": "person", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": "辈分包含成员"}], "mappings": [{"id": 5, "ontology_id": 7, "onto_type": "person", "physical_type": "人物", "kind": "node"}, {"id": 6, "ontology_id": 7, "onto_type": "male", "physical_type": "人物", "kind": "node"}, {"id": 7, "ontology_id": 7, "onto_type": "female", "physical_type": "人物", "kind": "node"}, {"id": 8, "ontology_id": 7, "onto_type": "generation", "physical_type": "辈分", "kind": "node"}, {"id": 9, "ontology_id": 7, "onto_type": "father_of", "physical_type": "父子", "kind": "edge"}, {"id": 10, "ontology_id": 7, "onto_type": "mother_of", "physical_type": "母子", "kind": "edge"}, {"id": 11, "ontology_id": 7, "onto_type": "spouse_of", "physical_type": "夫妻", "kind": "edge"}, {"id": 12, "ontology_id": 7, "onto_type": "sibling_of", "physical_type": "兄弟姐妹", "kind": "edge"}, {"id": 13, "ontology_id": 7, "onto_type": "grandparent_of", "physical_type": "祖孙", "kind": "edge"}, {"id": 14, "ontology_id": 7, "onto_type": "belongs_to_generation", "physical_type": "属于辈分", "kind": "edge"}]}	2026-11-23 15:40:15
59	1	5	create_class	新增类 审计测试类	{"ontology": {"id": 1, "name": "o1-组织管理", "scope": "domain", "namespace": "o1-组织管理", "authority": "high", "version": "v1", "status": "active", "comment": "", "created_at": "2026-11-17 12:01:14", "space_id": 1}, "classes": [{"id": 1, "ontology_id": 1, "name": "c0", "parent_name": "", "comment": "部门"}, {"id": 2, "ontology_id": 1, "name": "a1", "parent_name": "", "comment": "员工"}, {"id": 3, "ontology_id": 1, "name": "b1", "parent_name": "", "comment": "项目"}, {"id": 4, "ontology_id": 1, "name": "c1", "parent_name": "", "comment": "外部组织"}, {"id": 28, "ontology_id": 1, "name": "审计测试类", "parent_name": "", "comment": ""}], "rels": [{"id": 1, "ontology_id": 1, "name": "belongs_to", "subj_class": "a1", "obj_class": "c0", "cardinality": "one", "nullable": 0, "inherits_from": "", "comment": ""}, {"id": 2, "ontology_id": 1, "name": "join_project", "subj_class": "a1", "obj_class": "b1", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": ""}], "mappings": [{"id": 1, "ontology_id": 1, "onto_type": "c0", "physical_type": "c0", "kind": "node"}, {"id": 2, "ontology_id": 1, "onto_type": "a1", "physical_type": "a1", "kind": "node"}, {"id": 3, "ontology_id": 1, "onto_type": "belongs_to", "physical_type": "works_in", "kind": "edge"}]}	2026-11-23 17:26:02
60	1	6	delete_class	删除类 审计测试类	{"ontology": {"id": 1, "name": "o1-组织管理", "scope": "domain", "namespace": "o1-组织管理", "authority": "high", "version": "v2", "status": "active", "comment": "", "created_at": "2026-11-17 12:01:14", "space_id": 1}, "classes": [{"id": 1, "ontology_id": 1, "name": "c0", "parent_name": "", "comment": "部门"}, {"id": 2, "ontology_id": 1, "name": "a1", "parent_name": "", "comment": "员工"}, {"id": 3, "ontology_id": 1, "name": "b1", "parent_name": "", "comment": "项目"}, {"id": 4, "ontology_id": 1, "name": "c1", "parent_name": "", "comment": "外部组织"}, {"id": 28, "ontology_id": 1, "name": "审计测试类", "parent_name": "", "comment": ""}], "rels": [{"id": 1, "ontology_id": 1, "name": "belongs_to", "subj_class": "a1", "obj_class": "c0", "cardinality": "one", "nullable": 0, "inherits_from": "", "comment": ""}, {"id": 2, "ontology_id": 1, "name": "join_project", "subj_class": "a1", "obj_class": "b1", "cardinality": "many", "nullable": 1, "inherits_from": "", "comment": ""}], "mappings": [{"id": 1, "ontology_id": 1, "onto_type": "c0", "physical_type": "c0", "kind": "node"}, {"id": 2, "ontology_id": 1, "onto_type": "a1", "physical_type": "a1", "kind": "node"}, {"id": 3, "ontology_id": 1, "onto_type": "belongs_to", "physical_type": "works_in", "kind": "edge"}]}	2026-11-23 17:26:02
\.


--
-- Data for Name: tb_ontology; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tb_ontology (id, name, scope, namespace, authority, version, status, comment, space_id, created_at) FROM stdin;
1	o1-组织管理	domain	o1-组织管理	high	v3	active		1	2026-11-17 12:01:14
5	子墨-本体图谱01	domain	子墨-本体图谱01	normal	v1	active	子墨-本体图谱01	5	2026-11-23 15:01:12
7	万家家族族谱	domain	urn:wan-family	high	v1	active	万家六代族谱本体：人物/辈分/亲属关系定义	9	2026-11-23 15:37:07
\.


--
-- Name: tb_audit_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_audit_log_id_seq', 49, true);


--
-- Name: tb_data_source_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_data_source_id_seq', 2, true);


--
-- Name: tb_dim_onto_domain_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_dim_onto_domain_id_seq', 621, true);


--
-- Name: tb_dim_onto_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_dim_onto_item_id_seq', 7023, true);


--
-- Name: tb_onto_class_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_onto_class_id_seq', 25, true);


--
-- Name: tb_onto_mapping_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_onto_mapping_id_seq', 14, true);


--
-- Name: tb_onto_rel_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_onto_rel_id_seq', 18, true);


--
-- Name: tb_onto_space_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_onto_space_id_seq', 9, true);


--
-- Name: tb_onto_version_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_onto_version_id_seq', 60, true);


--
-- Name: tb_ontology_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tb_ontology_id_seq', 7, true);


--
-- Name: tb_audit_log tb_audit_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_audit_log
    ADD CONSTRAINT tb_audit_log_pkey PRIMARY KEY (id);


--
-- Name: tb_data_source tb_data_source_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_data_source
    ADD CONSTRAINT tb_data_source_pkey PRIMARY KEY (id);


--
-- Name: tb_dim_onto_domain tb_dim_onto_domain_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_dim_onto_domain
    ADD CONSTRAINT tb_dim_onto_domain_code_key UNIQUE (code);


--
-- Name: tb_dim_onto_domain tb_dim_onto_domain_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_dim_onto_domain
    ADD CONSTRAINT tb_dim_onto_domain_pkey PRIMARY KEY (id);


--
-- Name: tb_dim_onto_item tb_dim_onto_item_domain_code_code_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_dim_onto_item
    ADD CONSTRAINT tb_dim_onto_item_domain_code_code_key UNIQUE (domain_code, code);


--
-- Name: tb_dim_onto_item tb_dim_onto_item_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_dim_onto_item
    ADD CONSTRAINT tb_dim_onto_item_pkey PRIMARY KEY (id);


--
-- Name: tb_onto_class tb_onto_class_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_class
    ADD CONSTRAINT tb_onto_class_pkey PRIMARY KEY (id);


--
-- Name: tb_onto_mapping tb_onto_mapping_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_mapping
    ADD CONSTRAINT tb_onto_mapping_pkey PRIMARY KEY (id);


--
-- Name: tb_onto_rel tb_onto_rel_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_rel
    ADD CONSTRAINT tb_onto_rel_pkey PRIMARY KEY (id);


--
-- Name: tb_onto_space tb_onto_space_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_space
    ADD CONSTRAINT tb_onto_space_pkey PRIMARY KEY (id);


--
-- Name: tb_onto_version tb_onto_version_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_onto_version
    ADD CONSTRAINT tb_onto_version_pkey PRIMARY KEY (id);


--
-- Name: tb_ontology tb_ontology_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tb_ontology
    ADD CONSTRAINT tb_ontology_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_audit_target ON public.tb_audit_log USING btree (module, target_id, id DESC);


--
-- Name: idx_dim_onto_item_domain; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_dim_onto_item_domain ON public.tb_dim_onto_item USING btree (domain_code, sort_order);


--
-- Name: idx_onto_class; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_onto_class ON public.tb_onto_class USING btree (ontology_id);


--
-- Name: idx_onto_rel; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_onto_rel ON public.tb_onto_rel USING btree (ontology_id);


--
-- Name: idx_onto_version; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_onto_version ON public.tb_onto_version USING btree (ontology_id, version_no);


--
-- PostgreSQL database dump complete
--

\unrestrict ohN8j7I8C07Rrzztdo8nfdvpPVNoSkgnLfBoUxODLdc61XG7YzYRXas0PRWwL2M

