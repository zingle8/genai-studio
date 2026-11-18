# project_genai-studio — GenAI Studio 管理平台

> 版本：v0.0（demo 页面开发）
> 更新日期：2026-11-07 前
> 开发完成内容：完成 ai-studio 平台的 demo 平台页面设计的前端页面开发（页面原型参考 `project_ai-platfor/ai-studio/demo`，作为后续正式前端开发的视觉与交互基准）

> 版本：v0.1（规划稿）
> 更新日期：2026-11-07
> 定位：GenAI 平台（AI Studio），覆盖模型推理、RAG、知识库、知识图谱、智能体、MCP、计费与可观测等能力

---

## 1. 项目信息

| 项 | 值 |
|----|----|
| 项目目录名 | `project_genai-studio` |
| 平台名称 | genai-studio 管理平台 |
| 网关平台应用 ID | `app-genai-studio` |
| 网关平台应用名 | genai-studio 管理平台 |
| Java 技术栈 | JDK 17 · Spring Boot 3.2.12 · MyBatis · Maven 多模块（微服务） |
| Python 技术栈 | 单体服务（各模块独立进程，`py-` 前缀） |
| 存储组件 | MySQL 5.7 · PostgreSQL + pgvector · Neo4j · Elasticsearch |
| 模型运行时 | Ollama · 本地其他模型（目录待定，后续确认后整合） |
| 前端 | Vue3（微前端，按后端模块划分应用与代码模块），其余组件后续安装 |
| 网关对接 | 复用 `project_api-gateway` 项目：① 接入与上报——Java 侧 `jv-api-gateway-client-starter`（`com.zimo.gateway:1.0.0`），Python 侧 `py-genai-apigateway-client-sdk`；② **公共能力复用——用户/登录/权限/密钥体系统一调用网关 `jv-api-gateway-user` 模块接口（auth/user/apikey 模块不自建用户库，见 4.5 节）** |

### 目录结构规划

```
project_genai-studio/
├── backend/     # Java 微服务（jv- 前缀，Maven 多模块）
├── python/      # Python 单体服务（py- 前缀，各服务独立目录）
├── frontend/    # Vue3 微前端（按后端模块划分应用）
├── docs/        # 项目文档
├── sql/         # 数据库脚本（MySQL / PG / Neo4j / ES 索引）
├── demo/        # 演示与示例
└── README.md
```

---

## 2. 架构总览

```
┌────────────────────────────────────────────────────────────────┐
│  前端（Vue3 微前端，按后端模块划分应用）                              │
│    app · dashboard · market · docs · chats · prompt · ...       │
├────────────────────────────────────────────────────────────────┤
│  接入层（Java 微服务）                                            │
│    jv-genai-app（门户/BFF）· jv-genai-market（市场）              │
│    jv-genai-docs（开发者文档门户）                                 │
├────────────────────────────────────────────────────────────────┤
│  网关层                                                          │
│    jv-genai-aigateway（AI 网关）                                  │
│    jv-genai-mcpgateway（MCP 网关）                                │
│    jv-genai-agentgateway（Agent 网关）                            │
├────────────────────────────────────────────────────────────────┤
│  业务层                                                          │
│    jv-genai-models · jv-genai-user · jv-genai-prompt             │
│    jv-genai-chats · jv-genai-apikey · jv-genai-billing           │
│    jv-genai-costs · jv-genai-auth · jv-genai-config              │
│    py-genai-knowledgebase · py-genai-graph · py-genai-ontology   │
├────────────────────────────────────────────────────────────────┤
│  AI 能力层（Python 单体服务）                                      │
│    py-genai-infer · py-genai-rag · py-genai-embedding            │
│    py-genai-reranker · py-genai-ocr                              │
├────────────────────────────────────────────────────────────────┤
│  支撑层                                                          │
│    jv-genai-logs · jv-genai-traces（可观测）                       │
│    jv-genai-comm（公共二方库，不独立部署）                            │
├────────────────────────────────────────────────────────────────┤
│  网关平台接入 SDK（非独立服务，作为依赖被各模块引用）                    │
│    jv-genai-apigateway-client-sdk（Java 模块接入与上报）             │
│    py-genai-apigateway-client-sdk（Python 模块接入与上报）           │
├────────────────────────────────────────────────────────────────┤
│  基础设施（本机 / Docker）                                        │
│    MySQL 5.7 · PG+pgvector · Neo4j · ES · Ollama · 本地模型(待定)  │
└────────────────────────────────────────────────────────────────┘
```

### 服务形态

| 形态 | 前缀 | 说明 |
|------|------|------|
| Java 微服务 | `jv-` | Spring Boot 3.2.12 + JDK17，独立部署、独立数据库 schema |
| Python 单体服务 | `py-` | AI 能力服务，独立进程部署，通过 SDK 上报网关 |
| 公共二方库 | `jv-genai-comm` | jar 依赖，不独立部署 |
| 接入 SDK | 两个 `*-apigateway-client-sdk` | 非独立服务，被各模块引入 |

---

## 3. 模块清单（共 29 个）

### 3.1 Java 微服务（`jv-` 前缀，20 个）

| # | 服务 ID（模块名） | 服务名（中文名称） | 功能作用 |
|---|------------------|------------------|---------|
| 1 | `jv-genai-app` | 应用服务（门户） | 平台统一入口/前端 BFF，聚合各微服务，提供 REST/GraphQL、页面路由、会话管理 |
| 2 | `jv-genai-comm` | 公共服务 | 跨服务共享公共模块：工具、DTO、异常体系、常量（二方库，不独立部署） |
| 3 | `jv-genai-auth` | 认证授权服务 | **网关平台用户体系对接层（不自建用户库）**：复用网关 `jv-api-gateway-user` 的 `/auth/*`（register/login/logout/info/my-perms）与 `/open/auth/*`（开放认证、token 校验），平台侧做会话与鉴权适配、多租户上下文透传 |
| 4 | `jv-genai-dashboard` | 控制台/仪表盘 | 运营看板、用量统计、资源概览、告警、租户管理后台 |
| 5 | `jv-genai-aigateway` | AI 网关 | 统一模型请求入口：路由、限流、熔断、计费埋点、OpenAI 兼容层 |
| 6 | `jv-genai-mcpgateway` | MCP 网关 | MCP 服务管理：工具/资源/提示词注册、鉴权、调用转发 |
| 7 | `jv-genai-agentgateway` | Agent 网关 | 智能体编排与调用入口：Agent 注册、工具链、多 Agent 协作 |
| 8 | `jv-genai-models` | 模型管理服务 | 模型注册、版本、卡片配置、Provider 管理、评测、上下线 |
| 9 | `jv-genai-config` | 配置中心 | 全局/租户配置下发、参数管理、热更新、Feature Flag |
| 10 | `jv-genai-user` | 用户服务 | **网关平台用户体系对接层（不自建用户库）**：复用网关 `/users`（用户 CRUD/状态/解锁）、`/perm/groups`（权限组/成员/权限绑定）、`/perm/dictionary`（字典），平台侧仅做组织/团队等扩展档案与缓存 |
| 11 | `jv-genai-prompt` | 提示词服务 | Prompt 模板管理、版本、变量、调试、共享 |
| 12 | `jv-genai-chats` | 会话对话服务 | 会话管理、消息存储、上下文记忆、多轮、分享 |
| 13 | `jv-genai-apikey` | API 密钥服务 | **业务模块（自建）**：API Key 生成、轮转、Scope 权限范围、吊销、用量绑定 |
| 14 | `jv-genai-billing` | 计费服务 | 套餐、配额、扣费、账单、支付、订单 |
| 15 | `jv-genai-costs` | 成本核算服务 | 成本归集、单位成本分析、分摊、预算控制 |
| 16 | `jv-genai-logs` | 日志服务 | 统一日志采集、检索、脱敏、分类存储 |
| 17 | `jv-genai-traces` | 链路追踪服务 | 分布式追踪、调用链、性能分析（OpenTelemetry） |
| 18 | `jv-genai-docs` | 文档服务 | 开放 API 文档、SDK、开发者门户 |
| 19 | `jv-genai-market` | 市场服务 | 模型市场、应用/智能体市场、Prompt 市场、插件市场、上架/评分/推荐 |
| 20 | `jv-genai-apigateway-client-sdk` | 网关接入 SDK（Java） | **Java 模块接入和上报**：复用 `jv-api-gateway-client-starter`，供各 Java 微服务统一接入网关平台 |

### 3.2 Python 单体服务（`py-` 前缀，9 个）

| # | 服务 ID（模块名） | 服务名（中文名称） | 功能作用 |
|---|------------------|------------------|---------|
| 21 | `py-genai-infer` | 推理服务 | Python 对接大模型推理引擎（Ollama 等），流式输出 |
| 22 | `py-genai-rag` | 检索增强服务 | RAG 编排：检索→重排→拼 Prompt→生成 |
| 23 | `py-genai-embedding` | 向量化服务 | 文本/多模态 Embedding 编码（PG+pgvector） |
| 24 | `py-genai-reranker` | 重排序服务 | 候选段落 Rerank 精排 |
| 25 | `py-genai-ontology` | 本体知识服务 | 领域本体/概念模型管理、语义约束 |
| 26 | `py-genai-knowledgebase` | 知识库管理 | 知识库创建、文档上传、分块、索引构建、检索 |
| 27 | `py-genai-graph` | 知识图谱服务 | 图谱存储查询（Neo4j）、实体/关系抽取、推理 |
| 28 | `py-genai-ocr` | 文字识别服务 | OCR/PDF 解析、表格版面识别 |
| 29 | `py-genai-apigateway-client-sdk` | 网关接入 SDK（Python） | **Python 模块接入和上报**：供各 `py-` 服务统一接入网关平台 |

> 各模块的 **服务 ID = 模块名**，**服务名 = 表中中文名称**，统一以应用 ID `app-genai-studio` 接入网关平台。

---

## 4. 核心流程

### 4.1 对话/生成流程（主链路）

```
用户(前端)
  → jv-genai-app（鉴权/会话）
  → jv-genai-chats（会话与上下文）
  → jv-genai-aigateway（路由/限流/计费埋点）
  → [RAG 场景] py-genai-rag
        ├→ py-genai-embedding（向量化）
        ├→ py-genai-knowledgebase / ES / PG+pgvector（检索）
        ├→ py-genai-reranker（精排）
        └→ py-genai-prompt（模板拼装）
  → py-genai-infer（调用 Ollama / 本地模型推理，流式返回）
  → 逐级回传 → jv-genai-chats 落库 → 前端渲染
```

### 4.2 网关平台接入与上报流程

```
各微服务（Java / Python）
  → 引入 jv-genai-apigateway-client-sdk（Java）
     或 py-genai-apigateway-client-sdk（Python）
  → SDK 采集请求日志、埋点、链路数据
  → 上报至 project_api-gateway 平台
     （应用 ID: app-genai-studio，服务 ID/名 = 各子模块）
  → 网关侧汇聚 → jv-genai-logs / jv-genai-traces / dashboard 展示
```

### 4.3 知识库构建流程

```
文档上传 → py-genai-ocr（解析/OCR）→ 分块
  → py-genai-embedding（向量化 → PG+pgvector）
  → 实体/关系抽取 → py-genai-graph（Neo4j）+ py-genai-ontology（本体约束）
  → 索引构建（ES）→ 知识库上线，供 RAG 检索
```

### 4.4 计费与成本流程

```
aigateway 调用埋点（token/次数/模型）
  → jv-genai-billing（配额校验、扣费）
  → jv-genai-costs（成本归集、分摊）
  → jv-genai-dashboard（看板展示）
```

### 4.5 统一登录认证流程（复用网关平台用户体系）

**设计原则：GenAI Studio 不自建用户/登录体系，统一复用网关平台（`project_api-gateway`）的公共能力接口。** 这也是所有平台接入网关的核心原因之一——各平台共用一套用户、权限、密钥等公共模块，避免重复建设。

```
用户(前端 fe-app 登录页)
  → jv-genai-auth（对接层，转发登录请求）
  → 网关平台 jv-api-gateway-user：POST /auth/login（注册 /auth/register）
  → 返回 token + 用户信息 + 权限（GET /auth/info、/auth/my-perms）
  → jv-genai-auth 签发平台侧会话（透传网关 token，携带 app-genai-studio 应用上下文）
  → 后续请求：各 genai 服务校验会话（本地校验 or 调 /open/auth/token/verify）
  → 用户/权限管理：jv-genai-user 代理网关 /users、/perm/*
```

网关平台可复用的公共能力（已确认接口清单，来自 `jv-api-gateway-user`）：

| 能力域 | 网关接口 | GenAI 侧对接模块 |
|--------|---------|----------------|
| 认证 | `/auth/register` `/auth/login` `/auth/logout` `/auth/info` `/auth/my-perms` | `jv-genai-auth` |
| 开放认证 | `/open/auth/register` `/open/auth/login` `/open/auth/logout` `/open/auth/token/verify` | `jv-genai-auth` |
| 用户管理 | `/users`（CRUD、状态、解锁） | `jv-genai-user` |
| 权限/字典 | `/perm/groups`（成员/权限绑定）、`/perm/dictionary` | `jv-genai-user` |

> 注意：`jv-genai-apikey` 是**自建业务模块**（API Key 生成、轮转、Scope、吊销、用量绑定），不依赖网关 `/keys` 接口。

> 后续其他平台（如 `project_ai-platfor` 等）同样以各自 app-id 接入网关平台，即可复用同一套用户/登录/权限/密钥能力，实现"一次建设、多平台复用"。

---

## 5. 技术选型与规范

### 5.1 技术栈（本机 / Docker 已具备）

| 类别 | 组件 | 版本/说明 |
|------|------|----------|
| 语言/运行时 | Java JDK | 17 |
| 后端框架 | Spring Boot | 3.2.12 |
| ORM | MyBatis | — |
| Python Web 框架 | FastAPI | 2026-11-07 已确认（异步高性能，自动 OpenAPI 文档） |
| 数据库 | MySQL | 5.7 |
| 图数据库 | Neo4j | — |
| 搜索引擎 | Elasticsearch | — |
| 向量库 | PostgreSQL + pgvector | — |
| 模型运行时 | Ollama | — |
| 本地模型 | 目录待定 | 后续告知后整合 |
| 前端框架 | Vue3 + qiankun | 微前端基座 fe-app（2026-11-07 已确认），其余依赖后续安装 |

### 5.2 技术选择规范（强约束）

1. **优先使用国外技术框架**，其次再考虑国内组件框架；
2. **新增任何技术框架，必须先经项目所有者确认后才能引入**，防止出现国内外技术垄断、技术冻结与鸿沟问题；
3. 本文档所列技术栈为当前基线，任何增减需更新本文档并经确认。

---

## 6. 前端微前端划分

前端按后端模块对应划分应用与代码模块（Vue3），初步对应关系：

| 前端应用 | 对应后端模块 | 说明 |
|----------|-------------|------|
| `fe-app` | `jv-genai-app` | 门户主应用（壳应用/基座） |
| `fe-dashboard` | `jv-genai-dashboard` | 控制台看板 |
| `fe-chats` | `jv-genai-chats` | 对话界面 |
| `fe-prompt` | `jv-genai-prompt` | Prompt 管理 |
| `fe-models` | `jv-genai-models` | 模型管理 |
| `fe-knowledgebase` | `py-genai-knowledgebase` | 知识库管理 |
| `fe-graph` | `py-genai-graph` | 知识图谱可视化 |
| `fe-market` | `jv-genai-market` | 市场页面 |
| `fe-docs` | `jv-genai-docs` | 开发者文档站 |
| `fe-admin` | `jv-genai-user` / `jv-genai-auth` / `jv-genai-apikey` / `jv-genai-billing` | 管理后台（用户/权限/密钥/计费） |

> 微前端框架已确认采用 **qiankun**（2026-11-07），基座为 `fe-app`。

---

## 7. 待确认事项

| # | 事项 | 状态 |
|---|------|------|
| 1 | 本地其他模型的具体目录 | 待定，等待提供后整合 |
| 2 | 微前端框架选型 | ✅ 已确认：qiankun（2026-11-07） |
| 3 | Python Web 框架选型 | ✅ 已确认：FastAPI（2026-11-07） |
| 4 | `py-genai-apigateway-client-sdk` 对接方式（HTTP 上报 or 网关侧 Python SDK） | 暂按 HTTP 上报实现（SDK 内置 `GenaiGatewayClient`），后续与网关平台联调时确认协议细节 |
| 5 | 网关平台各服务的注册信息（服务 ID/名）清单化 | 规划已定，待系统接入时配置 |

## 8. 脚手架现状（2026-11-07 已创建）

| 部分 | 位置 | 内容 |
|------|------|------|
| Java 后端 | `backend/` | Maven 父 POM（`com.zimo.genai:genai-studio:1.0.0`，Spring Boot 3.2.12 / JDK17）+ 20 个模块骨架；18 个服务含启动类、`application.yml`（端口 38080-38097、MySQL 5.7 数据源占位、网关接入配置）；`comm` 为二方库（含统一 `Result`）；`apigateway-client-sdk` 已预置对 `com.zimo.gateway:jv-api-gateway-client-starter:1.0.0` 的依赖 |
| Python 服务 | 根目录 `py-*/` | 8 个 FastAPI 单体服务（端口 38101-38108，含 `health` 接口、配置类、网关上报模块、`run.sh`）+ `py-genai-apigateway-client-sdk`（`GenaiGatewayClient`，pyproject 可安装） |
| 前端 | `frontend/` | qiankun 基座 `fe-app`（端口 38200，注册 9 个子应用）+ 9 个 Vue3 子应用（fe-dashboard/fe-chats/fe-prompt/fe-models/fe-knowledgebase/fe-graph/fe-market/fe-docs/fe-admin，端口 38201-38209，含 qiankun 生命周期导出） |

### 启动方式速查

```bash
# Java（需先在 project_api-gateway/backend 中 mvn install 网关 client starter）
cd backend && mvn clean install

# Python 服务（示例：推理服务）
cd py-genai-infer && pip install -r requirements.txt && ./run.sh

# 前端基座 + 子应用
cd frontend/fe-app && npm install && npm run dev   # 基座 38200
cd frontend/fe-dashboard && npm install && npm run dev  # 子应用 38201
```

## 9. 首版已实现模块（2026-11-07，参考 project_ai-platfor/ai-studio/demo 风格）

> 开发计划与整体进度跟踪见：`docs/开发计划与进度.md`

| 模块 | 后端接口 | 前端页面 | 说明 |
|------|---------|---------|------|
| 登录 | `jv-genai-auth`：`/api/auth/login\|register\|logout\|info\|my-perms`（代理网关 `jv-api-gateway-user`） | `fe-app` 登录页（`/login`）+ 工作台（`/home`） | 登录页参考 demo login.html；token/user 存 localStorage |
| API Key | `jv-genai-apikey`：`/api/apikeys` CRUD + `rotate`/`renew`（自建业务模块） | `fe-admin` `/apikey` | DeepSeek 开发者控制台风格：Key 仅创建/轮转时完整展示一次，列表掩码；支持过期时间、可用模型、限流 RPM/TPM/并发、组织归属 |
| 账单 | `jv-genai-billing`：`/api/billing/summary`、`/orders`、`/topup` | `fe-admin` `/billing` | 余额/本月消费/充值统计、订单表、充值弹窗（演示即时到账） |
| 成本统计 | `jv-genai-costs`：`/api/costs/overview`、`/daily`、`/by-model`、`/by-service` | `fe-dashboard` `/costs` | 今日/本月总览卡、按日柱状趋势、按模型占比表 |
| 使用日志 | `jv-genai-logs`：`/api/logs`（分页/多条件）、`/summary` | `fe-dashboard` `/usage-logs` | 时间范围/模型/状态/关键字筛选、分页、今日汇总 |

配套 SQL（MySQL 5.7，含种子数据）：`sql/01_jv-genai-apikey_api-key.sql` 等（命名：执行顺序_服务名_表名.sql，完整清单见 `sql/` 目录）。

前端约定：HTTP 用原生 `fetch`（未引入 axios）；样式复用 demo 的 `assets/css/style.css`（已复制到各子应用 `src/assets/`）；开发期跨服务调用通过各子应用 `vite.config.js` 的 `proxy` 转发（auth→38081、apikeys→38091、billing→38092、costs→38093、logs→38094）。

---

## demo 目录

静态演示/测试文件目录。可用以下命令快速启动本地静态服务（端口 8899）：

```
python3 -m http.server 8899
```

（该命令也存于 `demo/http-server-command.txt`）
