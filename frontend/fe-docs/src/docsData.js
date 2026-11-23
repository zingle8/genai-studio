/**
 * 开发者文档中心 · 结构化内容
 *
 * 数据来源：各服务真实 Controller / DTO（见文末 source 字段）
 * 维护约定：接口变更时同步修改本文件对应 endpoint 的 params / bodyFields / responseFields。
 */

const param = (name, where, type, desc, extra = {}) => ({ name, where, type, desc, required: false, default: '', ...extra })
const req = (name, where, type, desc, extra = {}) => param(name, where, type, desc, { required: true, ...extra })
const field = (name, type, desc) => ({ name, type, desc })

export const docModules = [
  /* ============================ 模型广场 / 模型调用 ============================ */
  {
    id: 'model',
    name: '模型广场 · 模型调用',
    icon: 'M',
    color: '#4D6BFE',
    desc: '通过统一路由网关调用模型广场已上架的模型，兼容 OpenAI / Anthropic / Gemini 等上游格式。',
    sections: [
      {
        id: 'model-flow',
        title: '使用教程：调用流程与鉴权',
        kind: 'tutorial',
        lead: '「模型广场」负责模型的上架与管理，真正发起调用的是数据面服务 jv-genai-router。调用方只需要知道平台的「对外模型名」和一把 API Key，网关会自动完成鉴权、余额校验、限流、模型名替换、上游转发与计费记账。',
        steps: [
          {
            title: '1. 确认模型已上架并取得对外名称',
            body: '进入「模型广场」，找到目标模型，确认状态为「已上架」，复制其「模型名称」。该名称就是后续请求体中的 model 字段值（不是上游真实模型名）。也可以调用 GET /v1/models 拉取当前全部可用模型及其扩展信息。',
            code: 'curl https://<网关地址>/v1/models'
          },
          {
            title: '2. 创建 API Key 并自检',
            body: '在「API Key」页面新建密钥，保存 sk- 开头的完整字符串。Key 绑定了可用模型白名单以及 rpm（每分钟请求数）、tpm（每分钟 token 数）、cc（并发数）配额。创建后可用 GET /v1/me 确认身份与配额。',
            code: 'curl https://<网关地址>/v1/me \\\n  -H "Authorization: Bearer sk-xxxxxxxx"'
          },
          {
            title: '3. 发起模型调用',
            body: '使用 OpenAI SDK 或任意 HTTP 客户端，把 base_url 指向网关地址，api_key 填入上一步的 Key，model 填入平台对外名称。请求体其余字段按所选上游格式原样填写，网关会透传。',
            code: `from openai import OpenAI

client = OpenAI(
    base_url="https://<网关地址>/v1",
    api_key="sk-xxxxxxxx",
)
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "你好，介绍一下你自己"}],
    stream=False,
)
print(resp.choices[0].message.content)`
          },
          {
            title: '4. 查看用量与调用日志',
            body: '调用成功后，网关按模型等级（tier）单价 × 实际 token 用量扣减余额，并写入调用统计 tb_usage_log 与内容日志 tb_relay_log（两者通过 trace_id 对齐）。可在「用量统计」「调用日志」页面查看。',
          }
        ],
        notes: [
          { type: 'info', text: 'model 必须是平台对外名。网关查库后会把请求体中的 model 替换为真实模型名（jv-real-model）再转发给上游。' },
          { type: 'info', text: '所有 POST /v1/** 均为透传，唯一强制字段是 model；messages、stream、temperature、prompt、tools 等按上游格式原样转发。' },
          { type: 'tip', text: '流式请求传 "stream": true，响应为 SSE（text/event-stream），OpenAI SDK 可直接消费；网关仍会在流结束后聚合 usage 记账。' },
          { type: 'warn', text: '上游鉴权由平台配置，调用方只需提供自己的平台 API Key，不要把上游密钥放在请求里。' }
        ]
      },
      {
        id: 'model-errors',
        title: '使用教程：错误码与限流',
        kind: 'tutorial',
        lead: '转发前网关会依次执行鉴权 → 余额 → 限流 → 模型配置校验。失败时返回 OpenAI error 格式：{"error":{"message":"...","type":"invalid_request_error","code":<HTTP状态码>}}。',
        table: {
          heads: ['状态码', '含义', '常见原因', '处理建议'],
          rows: [
            ['400', '请求参数错误', '缺少 model、模型未配置 Base URL、路径未开放', '检查请求体 model 字段与模型上架配置'],
            ['401', '未鉴权', '缺少 Authorization 头或 Key 无效', '补充 Authorization: Bearer sk-...'],
            ['402', '余额不足', '账户余额 ≤ 0', '前往「充值」页面充值'],
            ['403', '模型无权访问', 'Key 白名单不包含所请求的模型', '在 API Key 配置中放开对应模型'],
            ['404', '模型不存在或已下架', 'model 名称写错或已下架', '通过 GET /v1/models 重新获取可用名称'],
            ['429', '触发限流', '超过 rpm / tpm / cc 配额', '降低调用频率或提升 Key 配额'],
            ['502', '上游调用失败', '上游服务不可达或超时', '稍后重试；若持续失败查看调用日志 error_msg']
          ]
        }
      },
      {
        id: 'model-api',
        title: '接口参考：模型调用 API',
        kind: 'api',
        lead: '以下接口由 jv-genai-router 提供。探测类接口免登录（GET /v1/models）或仅需 Key 自检（GET /v1/me），调用类接口均需在 Header 携带平台 API Key。',
        endpoints: [
          {
            id: 'v1-models',
            method: 'GET',
            path: '/v1/models',
            title: '获取可用模型列表',
            desc: '返回全部已上架模型的 OpenAI 兼容列表，并附带平台扩展字段，供调用方探测每个模型可用的接口路径与请求格式。免登录。',
            auth: '免登录',
            params: [],
            responseFields: [
              field('object', 'string', '固定为 "list"'),
              field('data', 'array<Model>', '模型条目数组'),
              field('data[].id', 'string', '平台对外模型名，即请求体 model 字段应填的值'),
              field('data[].object', 'string', '固定为 "model"'),
              field('data[].created', 'number', 'Unix 秒级时间戳'),
              field('data[].owned_by', 'string', '厂商或供应商'),
              field('data[].jv-category', 'string', '平台分类'),
              field('data[].jv-tier', 'string', '模型等级，用于计费单价'),
              field('data[].jv-api-format', 'string', '上游格式：openai / claude / gemini'),
              field('data[].jv-base-url', 'string', '上游 Base URL'),
              field('data[].jv-real-model', 'string', '上游真实模型名'),
              field('data[].jv-url-paths', 'array<{path,format}>', '该模型开放的请求路径及格式；为空时默认 /chat/completions')
            ],
            responseExample: `{
  "object": "list",
  "data": [
    {
      "id": "gpt-4o-mini",
      "object": "model",
      "created": 1763880000,
      "owned_by": "OpenAI",
      "jv-category": "文本",
      "jv-tier": "T2",
      "jv-api-format": "openai",
      "jv-base-url": "https://api.openai.com/v1",
      "jv-real-model": "gpt-4o-mini",
      "jv-url-paths": [{ "path": "/chat/completions", "format": "openai" }]
    }
  ]
}`
          },
          {
            id: 'v1-me',
            method: 'GET',
            path: '/v1/me',
            title: 'API Key 自检',
            desc: '返回当前 Key 的名称、归属、可用模型白名单和限流配额。缺失或无效 Key 返回 401。',
            auth: 'Header: Authorization: Bearer <API Key>（必填）',
            params: [
              req('Authorization', 'header', 'string', '平台 API Key，格式 Bearer sk-...')
            ],
            responseFields: [
              field('object', 'string', '固定为 "me"'),
              field('name', 'string', 'Key 名称'),
              field('key_id', 'string/number', 'Key ID'),
              field('owner', 'string', '所属用户/owner'),
              field('models', 'array<string>', '允许调用的模型名白名单；空数组表示不限制'),
              field('rpm', 'number', '每分钟请求数上限'),
              field('tpm', 'number', '每分钟 token 数上限'),
              field('cc', 'number', '最大并发数')
            ],
            responseExample: `{
  "object": "me",
  "name": "默认密钥",
  "key_id": 3,
  "owner": "admin",
  "models": ["gpt-4o-mini", "qwen-plus"],
  "rpm": 60,
  "tpm": 120000,
  "cc": 4
}`
          },
          {
            id: 'v1-chat',
            method: 'POST',
            path: '/v1/chat/completions',
            title: '对话补全（OpenAI 兼容）',
            desc: '最常用的模型调用入口。请求体为原始 JSON 透传，网关强制要求 model 字段，其余字段按上游 OpenAI 格式填写并原样转发。响应格式与上游一致，支持 stream:true 的 SSE 流式返回。',
            auth: 'Header: Authorization: Bearer <API Key>（必填）',
            params: [
              req('Authorization', 'header', 'string', '平台 API Key'),
              req('model', 'body', 'string', '平台对外模型名，必须与 /v1/models 中的 id 一致'),
              req('messages', 'body', 'array', '对话消息数组，每项含 role 与 content（content 可为字符串或多模态分段数组）'),
              param('stream', 'body', 'boolean', '是否流式返回', { default: 'false' }),
              param('temperature', 'body', 'number', '采样温度，按上游能力支持'),
              param('top_p', 'body', 'number', '核采样参数'),
              param('max_tokens', 'body', 'number', '最大生成 token 数'),
              param('tools', 'body', 'array', '工具定义（function calling）'),
              param('tool_choice', 'body', 'string/object', '工具选择策略')
            ],
            requestExample: `curl https://<网关地址>/v1/chat/completions \\
  -H "Authorization: Bearer sk-xxxxxxxx" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": "你是一个助手"},
      {"role": "user", "content": "用一句话介绍向量数据库"}
    ],
    "temperature": 0.7,
    "stream": false
  }'`,
            responseFields: [
              field('id', 'string', '本次补全 ID'),
              field('object', 'string', '"chat.completion"'),
              field('model', 'string', '实际使用的模型'),
              field('choices[].message.role', 'string', '固定 "assistant"'),
              field('choices[].message.content', 'string', '模型回复文本'),
              field('choices[].finish_reason', 'string', '停止原因：stop / length / tool_calls'),
              field('usage.prompt_tokens', 'number', '输入 token 数'),
              field('usage.completion_tokens', 'number', '输出 token 数'),
              field('usage.total_tokens', 'number', '总 token 数（计费依据）')
            ],
            responseExample: `{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "model": "gpt-4o-mini",
  "choices": [{
    "index": 0,
    "message": {"role": "assistant", "content": "向量数据库是专门存储和检索高维向量的数据库。"},
    "finish_reason": "stop"
  }],
  "usage": {"prompt_tokens": 28, "completion_tokens": 21, "total_tokens": 49}
}`,
            notes: [
              '网关会把 model 替换为 jv-real-model 后转发，响应中的 model 由上游返回。',
              '同一转发入口还开放：/v1/messages（Claude 格式）、/v1/responses、/v1/responses/compact、/v1/completions、/v1/embeddings，以及 /chat/completions。具体可用路径以 /v1/models 返回的 jv-url-paths 为准。',
              'Claude 格式请求可附带 anthropic-version（默认 2023-06-01）；openai 格式可透传 OpenAI-Beta、Accept 头。'
            ]
          }
        ]
      }
    ],
    source: 'backend/jv-genai-router/.../controller/ModelListController.java, RelayController.java'
  },

  /* ============================ 知识库 KB ============================ */
  {
    id: 'kb',
    name: '知识库 KB',
    icon: 'K',
    color: '#00A870',
    desc: '把文档切块、向量化并存入知识库，通过关键词或语义检索为 RAG 应用提供上下文。',
    sections: [
      {
        id: 'kb-flow',
        title: '使用教程：从零搭建知识库',
        kind: 'tutorial',
        lead: '知识库以「空间 → 知识库 → 文档 → 分块」四层组织。一个空间下可建多个知识库；文档上传后按 chunk_mode 与 chunk_len 切块，语义检索使用 bge-m3 向量。所有接口统一返回 {"code":0,"data":...}。',
        steps: [
          {
            title: '1. 新建空间',
            body: '空间用于隔离不同业务或租户的知识库。调用 POST /api/kb/spaces 创建，拿到 space_id。',
            code: 'POST /api/kb/spaces\n{ "name": "产品文档空间", "description": "面向客服的知识库" }'
          },
          {
            title: '2. 新建知识库',
            body: '调用 POST /api/kb，指定所属 space_id、切块模式与长度、embedding 模型等。创建成功后返回知识库 id（kid），后续文档与检索接口都依赖它。',
            code: `POST /api/kb
{
  "name": "产品手册",
  "space_id": 1,
  "kb_type": "doc",
  "chunk_mode": "paragraph",
  "chunk_len": 500,
  "embedding_model": "bge-m3"
}`
          },
          {
            title: '3. 上传文档',
            body: '调用 POST /api/kb/{kid}/docs，以 multipart/form-data 上传文件，或直接传 text 文本。上传后系统自动切块并写入索引。',
            code: `curl -X POST "http://<kb服务>/api/kb/1/docs" \\
  -F "name=使用说明.md" \\
  -F "text=这里是文档正文..."`
          },
          {
            title: '4. 检索验证',
            body: '关键词检索用 GET /api/kb/{kid}/search?q=...；语义检索用 GET /api/kb/{kid}/semantic_search?q=...（需配置 embedding 模型）。跨库聚合用 GET /api/kb/search_multi。',
            code: 'GET /api/kb/1/semantic_search?q=如何重置密码&top_k=5'
          }
        ],
        notes: [
          { type: 'info', text: 'chunk_mode 常用值：paragraph（按段落）、fixed（定长）；chunk_len 默认 500。' },
          { type: 'tip', text: '不确定可选值时调用 GET /api/kb/options 获取数据库类型、切块模式、模型列表等下拉项。' },
          { type: 'info', text: 'POST /api/kb/ping 可用来自测数据库连接配置（db_type + db_config），创建知识库前先 ping 可避免配置错误。' }
        ]
      },
      {
        id: 'kb-api',
        title: '接口参考：知识库 API',
        kind: 'api',
        lead: '服务：py-genai-knowledgebase（FastAPI）。路径前缀 /api/kb。除上传文档使用 multipart/form-data 外，其余均为 JSON 或 query 参数。',
        endpoints: [
          {
            id: 'kb-options',
            method: 'GET', path: '/api/kb/options', title: '获取可选项',
            desc: '返回 db_type、切块模式、embedding/reranker 模型等前端下拉选项。',
            auth: '登录态（平台 JWT）', params: [],
            responseExample: '{ "code": 0, "data": { "db_types": ["sqlite"], "chunk_modes": ["paragraph", "fixed"], "embedding_models": ["bge-m3"] } }'
          },
          {
            id: 'kb-ping',
            method: 'POST', path: '/api/kb/ping', title: '测试数据库连接',
            desc: '用给定的数据库类型与配置做一次连通性测试。',
            auth: '登录态（平台 JWT）',
            params: [
              req('db_type', 'body', 'string', '数据库类型，如 sqlite'),
              param('db_config', 'body', 'string', '数据库连接配置', { default: '""' })
            ],
            requestExample: 'POST /api/kb/ping\n{ "db_type": "sqlite", "db_config": "" }'
          },
          {
            id: 'kb-spaces',
            method: 'GET / POST', path: '/api/kb/spaces', title: '空间列表 / 新建空间',
            desc: 'GET 返回全部空间；POST 新建空间。',
            auth: '登录态（平台 JWT）',
            params: [
              req('name', 'body(POST)', 'string', '空间名称'),
              param('description', 'body(POST)', 'string', '空间说明', { default: '""' })
            ],
            requestExample: 'POST /api/kb/spaces\n{ "name": "产品文档空间", "description": "面向客服" }',
            responseExample: '{ "code": 0, "data": [{ "id": 1, "name": "产品文档空间", "description": "面向客服" }] }'
          },
          {
            id: 'kb-space-del',
            method: 'DELETE', path: '/api/kb/spaces/{sid}', title: '删除空间',
            desc: '按空间 id 删除空间。', auth: '登录态（平台 JWT）',
            params: [req('sid', 'path', 'number', '空间 ID')]
          },
          {
            id: 'kb-list',
            method: 'GET', path: '/api/kb/list', title: '知识库列表',
            desc: '列出知识库，可按空间过滤。', auth: '登录态（平台 JWT）',
            params: [param('space_id', 'query', 'number', '空间 ID，0 表示全部', { default: '0' })]
          },
          {
            id: 'kb-create',
            method: 'POST', path: '/api/kb', title: '新建知识库',
            desc: '创建知识库并配置切块与向量化参数。', auth: '登录态（平台 JWT）',
            params: [
              req('name', 'body', 'string', '知识库名称'),
              param('description', 'body', 'string', '说明', { default: '""' }),
              param('space_id', 'body', 'number', '所属空间 ID', { default: '0' }),
              param('db_type', 'body', 'string', '数据库类型', { default: 'sqlite' }),
              param('db_config', 'body', 'string', '数据库配置', { default: '""' }),
              param('kb_type', 'body', 'string', '知识库类型', { default: 'doc' }),
              param('chunk_mode', 'body', 'string', '切块模式', { default: 'paragraph' }),
              param('chunk_len', 'body', 'number', '切块长度', { default: '500' }),
              param('embedding_model', 'body', 'string', 'Embedding 模型，语义检索需要', { default: '""' }),
              param('reranker_model', 'body', 'string', 'Reranker 模型', { default: '""' })
            ],
            requestExample: `POST /api/kb
{
  "name": "产品手册",
  "space_id": 1,
  "chunk_mode": "paragraph",
  "chunk_len": 500,
  "embedding_model": "bge-m3"
}`
          },
          {
            id: 'kb-update',
            method: 'PUT / DELETE', path: '/api/kb/{kid}', title: '更新 / 删除知识库',
            desc: 'PUT 使用与新建相同的 KbIn 结构整体更新；DELETE 删除知识库。',
            auth: '登录态（平台 JWT）',
            params: [req('kid', 'path', 'number', '知识库 ID'), ...['name', 'description', 'space_id', 'db_type', 'db_config', 'kb_type', 'chunk_mode', 'chunk_len', 'embedding_model', 'reranker_model'].map(n => param(n, 'body(PUT)', 'any', '同新建知识库字段'))]
          },
          {
            id: 'kb-doc-add',
            method: 'POST', path: '/api/kb/{kid}/docs', title: '添加文档',
            desc: '以 multipart/form-data 上传文件或直接提交文本。上传后自动切块入库。',
            auth: '登录态（平台 JWT）',
            params: [
              req('kid', 'path', 'number', '知识库 ID'),
              req('name', 'form', 'string', '文档名称'),
              param('text', 'form', 'string', '文档正文；与 file 二选一', { default: '""' }),
              param('file', 'form', 'file', '上传文件（UploadFile，可选）')
            ],
            requestExample: `curl -X POST "http://<kb服务>/api/kb/1/docs" \\
  -F "name=使用说明.md" \\
  -F "file=@./使用说明.md"`
          },
          {
            id: 'kb-doc-list',
            method: 'GET', path: '/api/kb/{kid}/docs', title: '文档列表',
            desc: '分页列出知识库中的文档。', auth: '登录态（平台 JWT）',
            params: [
              req('kid', 'path', 'number', '知识库 ID'),
              param('page', 'query', 'number', '页码', { default: '1' }),
              param('size', 'query', 'number', '每页条数', { default: '10' })
            ]
          },
          {
            id: 'kb-chunks',
            method: 'GET', path: '/api/kb/{kid}/docs/{did}/chunks', title: '查看文档分块',
            desc: '查看指定文档被切分后的分块内容，用于验证切块效果。',
            auth: '登录态（平台 JWT）',
            params: [req('kid', 'path', 'number', '知识库 ID'), req('did', 'path', 'number', '文档 ID')]
          },
          {
            id: 'kb-doc-del',
            method: 'DELETE', path: '/api/kb/{kid}/docs/{did}', title: '删除文档',
            desc: '删除文档及其分块。', auth: '登录态（平台 JWT）',
            params: [req('kid', 'path', 'number', '知识库 ID'), req('did', 'path', 'number', '文档 ID')]
          },
          {
            id: 'kb-search',
            method: 'GET', path: '/api/kb/{kid}/search', title: '关键词检索',
            desc: '在单个知识库内做关键词检索。', auth: '登录态（平台 JWT）',
            params: [
              req('kid', 'path', 'number', '知识库 ID'),
              req('q', 'query', 'string', '检索关键词'),
              param('top_k', 'query', 'number', '返回条数', { default: '5' })
            ],
            requestExample: 'GET /api/kb/1/search?q=重置密码&top_k=5'
          },
          {
            id: 'kb-sem-search',
            method: 'GET', path: '/api/kb/{kid}/semantic_search', title: '语义检索',
            desc: '使用 bge-m3 向量做语义相似度检索，需知识库配置 embedding_model。',
            auth: '登录态（平台 JWT）',
            params: [
              req('kid', 'path', 'number', '知识库 ID'),
              req('q', 'query', 'string', '检索问题'),
              param('top_k', 'query', 'number', '返回条数', { default: '5' })
            ],
            requestExample: 'GET /api/kb/1/semantic_search?q=忘记密码怎么办&top_k=5'
          },
          {
            id: 'kb-search-multi',
            method: 'GET', path: '/api/kb/search_multi', title: '跨空间 / 跨库聚合检索',
            desc: '按空间、知识库范围聚合检索。space_id=0 且 kb_id=0 表示全平台；指定空间后仅检索该空间下的知识库。',
            auth: '登录态（平台 JWT）',
            params: [
              req('q', 'query', 'string', '检索关键词或问题'),
              param('space_id', 'query', 'number', '空间 ID，0 表示全部', { default: '0' }),
              param('kb_id', 'query', 'number', '知识库 ID，0 表示全部', { default: '0' }),
              param('top_k', 'query', 'number', '返回条数', { default: '5' }),
              param('mode', 'query', 'string', '检索模式：kw 关键词 / sem 语义', { default: 'kw' })
            ],
            requestExample: 'GET /api/kb/search_multi?q=报销流程&space_id=1&top_k=8&mode=sem'
          }
        ]
      }
    ],
    source: 'backend/py-genai-knowledgebase/app/controller/kb_controller.py, dto/kb_dto.py'
  },

  /* ============================ 知识图谱 ============================ */
  {
    id: 'graph',
    name: '知识图谱',
    icon: 'G',
    color: '#7B5CFF',
    desc: '以实体类型 / 节点 / 边组织领域知识，支持邻域查询、版本快照与操作审计。',
    sections: [
      {
        id: 'graph-concept',
        title: '使用教程：核心概念与建模流程',
        kind: 'tutorial',
        lead: '一张图谱归属于一个「空间」。图谱内先定义「实体类型」（如人物、家族、公司），再创建具体「节点」（实体实例）和「边」（关系）。节点与边的属性以 JSON 字符串保存，可承载状态、辈分、实体类型等业务字段。',
        steps: [
          {
            title: '1. 创建空间与图谱',
            body: '先调用 POST /api/graphs/spaces 建空间，再调用 POST /api/graphs 创建图谱，传入 space_id、名称和数据库配置。',
            code: `POST /api/graphs
{ "name": "万家族谱", "space_id": 1, "db_type": "sqlite", "description": "家族人物关系" }`
          },
          {
            title: '2. 定义实体类型',
            body: '调用 POST /api/graphs/{gid}/entities 定义类型，并通过 props_schema（JSON 字符串）声明属性结构。',
            code: `POST /api/graphs/9/entities
{ "name": "人物", "props_schema": "[{\\"key\\":\\"辈分\\",\\"type\\":\\"string\\"}]" }`
          },
          {
            title: '3. 导入节点与边',
            body: '用 POST /api/graphs/{gid}/nodes 创建节点（entity_id 指向实体类型，props 为 JSON 字符串）；用 POST /api/graphs/{gid}/edges 创建边（source_id、target_id、rel_type）。',
            code: `POST /api/graphs/9/nodes
{ "entity_id": 2, "name": "万治国", "props": "{\\"辈分\\":\\"第一代\\",\\"状态\\":\\"在世\\"}" }

POST /api/graphs/9/edges
{ "source_id": 10, "target_id": 11, "rel_type": "父子", "props": "{}" }`
          },
          {
            title: '4. 邻域查询与可视化',
            body: '调用 GET /api/graphs/{gid}/neighborhood?nid=10&depth=2 获取以某节点为中心的多跳邻域；前端「知识图谱」页提供分群放射布局与节点/边详情。需要查看多起点时传 nids=10,11。',
            code: 'GET /api/graphs/9/neighborhood?nids=10,11&depth=2'
          }
        ],
        notes: [
          { type: 'info', text: 'props / props_schema 均为 JSON 字符串（不是对象），例如 "{\\"辈分\\":\\"第二代\\"}"。' },
          { type: 'tip', text: '每次写操作都会自动递增 tb_graph.version 并生成版本快照；可在「版本」tab 查看与恢复。' },
          { type: 'info', text: '所有写操作会记录到审计日志，可通过 GET /api/graphs/audit?gid=9 查询操作人、时间与详情。' }
        ]
      },
      {
        id: 'graph-api',
        title: '接口参考：知识图谱 API',
        kind: 'api',
        lead: '服务：py-genai-graph（FastAPI）。统一响应格式 {"code":0,"data":...}。空间 / 图谱 / 实体 / 节点 / 边均为标准 CRUD，另提供邻域、版本与审计接口。',
        endpoints: [
          {
            id: 'graph-spaces',
            method: 'GET / POST', path: '/api/graphs/spaces', title: '空间列表 / 新建空间',
            desc: 'POST body 为 SpaceIn。', auth: '登录态（平台 JWT）',
            params: [req('name', 'body(POST)', 'string', '空间名称'), param('description', 'body(POST)', 'string', '说明', { default: '""' })]
          },
          {
            id: 'graph-space-del', method: 'DELETE', path: '/api/graphs/spaces/{sid}', title: '删除空间',
            desc: '按 ID 删除图谱空间。', auth: '登录态（平台 JWT）',
            params: [req('sid', 'path', 'number', '空间 ID')]
          },
          {
            id: 'graph-list',
            method: 'GET / POST', path: '/api/graphs', title: '图谱列表 / 新建图谱',
            desc: 'POST body 为 GraphIn。', auth: '登录态（平台 JWT）',
            params: [
              req('name', 'body(POST)', 'string', '图谱名称'),
              param('space_id', 'body(POST)', 'number', '所属空间', { default: '0' }),
              param('db_type', 'body(POST)', 'string', '数据库类型', { default: 'sqlite' }),
              param('db_config', 'body(POST)', 'string', '数据库配置', { default: '""' }),
              param('description', 'body(POST)', 'string', '说明', { default: '""' })
            ],
            requestExample: 'POST /api/graphs\n{ "name": "万家族谱", "space_id": 1, "db_type": "sqlite" }'
          },
          {
            id: 'graph-update',
            method: 'PUT / DELETE', path: '/api/graphs/{gid}', title: '更新 / 删除图谱',
            desc: 'PUT 使用 GraphIn 整体更新；写操作会递增版本号并记录审计。',
            auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID'), req('name', 'body(PUT)', 'string', '图谱名称')]
          },
          {
            id: 'graph-audit',
            method: 'GET', path: '/api/graphs/audit', title: '审计日志',
            desc: '查询图谱的操作记录，包括操作人、时间、对象、操作类型和详情。',
            auth: '登录态（平台 JWT）',
            params: [
              param('gid', 'query', 'number', '图谱 ID，0 表示全部', { default: '0' }),
              param('limit', 'query', 'number', '返回条数上限', { default: '200' })
            ],
            responseExample: '{ "code": 0, "data": [{ "id": 12, "operator": "admin", "target_name": "万家族谱", "op": "update", "detail": "图谱信息更新", "created_at": "2026-11-23 10:12:00" }] }'
          },
          {
            id: 'graph-entities',
            method: 'GET / POST', path: '/api/graphs/{gid}/entities', title: '实体类型列表 / 新建',
            desc: 'POST body 为 EntityIn。', auth: '登录态（平台 JWT）',
            params: [
              req('gid', 'path', 'number', '图谱 ID'),
              req('name', 'body(POST)', 'string', '实体类型名称'),
              param('props_schema', 'body(POST)', 'string', '属性结构 JSON 字符串', { default: '"[]"' })
            ]
          },
          {
            id: 'graph-entity-update',
            method: 'PUT / DELETE', path: '/api/graphs/{gid}/entities/{eid}', title: '更新 / 删除实体类型',
            desc: 'PUT body 为 EntityIn。', auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID'), req('eid', 'path', 'number', '实体类型 ID')]
          },
          {
            id: 'graph-nodes',
            method: 'GET / POST', path: '/api/graphs/{gid}/nodes', title: '节点列表 / 新建',
            desc: 'POST body 为 NodeIn。列表接口返回节点及其属性 JSON。',
            auth: '登录态（平台 JWT）',
            params: [
              req('gid', 'path', 'number', '图谱 ID'),
              param('entity_id', 'body(POST)', 'number', '所属实体类型 ID', { default: '0' }),
              req('name', 'body(POST)', 'string', '节点名称'),
              param('props', 'body(POST)', 'string', '属性 JSON 字符串，可放状态/辈分等', { default: '"{}"' })
            ],
            requestExample: 'POST /api/graphs/9/nodes\n{ "entity_id": 2, "name": "万治国", "props": "{\\"辈分\\":\\"第一代\\"}" }'
          },
          {
            id: 'graph-node-update',
            method: 'PUT / DELETE', path: '/api/graphs/{gid}/nodes/{nid}', title: '更新 / 删除节点',
            desc: 'PUT body 为 NodeIn。', auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID'), req('nid', 'path', 'number', '节点 ID')]
          },
          {
            id: 'graph-edges',
            method: 'GET / POST', path: '/api/graphs/{gid}/edges', title: '边列表 / 新建',
            desc: 'POST body 为 EdgeIn。', auth: '登录态（平台 JWT）',
            params: [
              req('gid', 'path', 'number', '图谱 ID'),
              req('source_id', 'body(POST)', 'number', '起点节点 ID'),
              req('target_id', 'body(POST)', 'number', '终点节点 ID'),
              req('rel_type', 'body(POST)', 'string', '关系类型，如 父子 / 配偶 / 同事'),
              param('props', 'body(POST)', 'string', '边属性 JSON 字符串', { default: '"{}"' })
            ]
          },
          {
            id: 'graph-edge-update',
            method: 'PUT / DELETE', path: '/api/graphs/{gid}/edges/{eid}', title: '更新 / 删除边',
            desc: 'PUT body 为 EdgeIn。', auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID'), req('eid', 'path', 'number', '边 ID')]
          },
          {
            id: 'graph-neighborhood',
            method: 'GET', path: '/api/graphs/{gid}/neighborhood', title: '邻域查询',
            desc: '从一个或多个节点出发查询 N 跳邻域，返回子图节点与边。至少指定 nid 或 nids 之一。',
            auth: '登录态（平台 JWT）',
            params: [
              req('gid', 'path', 'number', '图谱 ID'),
              param('nid', 'query', 'number', '起点节点 ID', { default: '0' }),
              param('nids', 'query', 'string', '多起点，逗号分隔，如 10,11', { default: '""' }),
              param('depth', 'query', 'number', '查询深度，范围 1~7', { default: '1' })
            ],
            requestExample: 'GET /api/graphs/9/neighborhood?nids=10,11&depth=2'
          },
          {
            id: 'graph-versions',
            method: 'GET', path: '/api/graphs/{gid}/versions', title: '版本列表',
            desc: '列出该图谱的所有版本快照。', auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID')]
          },
          {
            id: 'graph-version-detail',
            method: 'GET', path: '/api/graphs/{gid}/versions/{no}', title: '版本详情',
            desc: '查看某个版本快照的完整内容。', auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID'), req('no', 'path', 'string', '版本号，如 v1')]
          },
          {
            id: 'graph-version-restore',
            method: 'POST', path: '/api/graphs/{gid}/versions/{no}/restore', title: '恢复版本',
            desc: '将图谱恢复到指定版本快照。', auth: '登录态（平台 JWT）',
            params: [req('gid', 'path', 'number', '图谱 ID'), req('no', 'path', 'string', '目标版本号')]
          }
        ]
      }
    ],
    source: 'backend/py-genai-graph/app/controller/graph_controller.py, dto/graph_dto.py'
  },

  /* ============================ 本体图谱 ============================ */
  {
    id: 'onto',
    name: '本体图谱',
    icon: 'O',
    color: '#ED7B2F',
    desc: '定义领域概念（类）、关系规则与物理模型映射，并可把图谱实例数据按本体映射投影为「数据关系图」。',
    sections: [
      {
        id: 'onto-flow',
        title: '使用教程：本体建模与数据关系图',
        kind: 'tutorial',
        lead: '本体由「类（Class）」「关系规则（Rel）」「映射（Mapping）」三部分组成。本体定义保存在本体库（onto.db）；实际的图实例数据保存在图谱库（graph.db），本体通过「图数据源」引用它，并按映射规则把物理数据投影成数据关系视图。两者不是同一份数据。',
        steps: [
          {
            title: '1. 创建空间与本体',
            body: '调用 POST /api/onto/spaces 建空间，再调用 POST /api/onto/ontologies 创建本体，填写 name、scope、namespace 等。',
            code: `POST /api/onto/ontologies
{
  "name": "万家家族本体",
  "space_id": 1,
  "scope": "domain",
  "namespace": "http://example.com/family#"
}`
          },
          {
            title: '2. 定义类与关系规则',
            body: '用 POST /api/onto/classes 添加类（可指定 parentName 形成层级）；用 POST /api/onto/rels 添加关系规则，声明主体类、客体类、基数与可空性。',
            code: `POST /api/onto/classes
{ "ontologyId": 5, "name": "人物", "parentName": "", "comment": "家族成员" }

POST /api/onto/rels
{ "ontologyId": 5, "name": "父子", "subjClass": "人物", "objClass": "人物", "cardinality": "many" }`
          },
          {
            title: '3. 配置映射并绑定图数据源',
            body: '用 POST /api/onto/mappings 建立本体类型到物理类型的映射（kind 为 node 或 edge）。再用 POST /api/onto/datasources 注册图数据源（type 如 neo4j / graph-db），指向图谱库中的具体图谱。',
            code: `POST /api/onto/mappings
{ "ontologyId": 5, "ontoType": "人物", "physicalType": "人物", "kind": "node" }

POST /api/onto/datasources
{ "name": "万家图谱·graph.db", "type": "graph-db", "config": { "gid": 9 } }`
          },
          {
            title: '4. 查看数据关系图与版本审计',
            body: '调用 GET /api/onto/{oid}/view-graph?ds=<数据源ID> 获取按本体映射投影的视图；前端「数据关系图」tab 以分群放射布局展示。每次写操作都会递增本体版本号并写入审计日志（GET /api/onto/audit?oid=5）。',
            code: 'GET /api/onto/5/view-graph?ds=3'
          }
        ],
        notes: [
          { type: 'warn', text: '本体定义（onto.db）与图实例数据（graph.db）是两份数据。打开本体后，数据关系图会自动匹配名称相近的图数据源；若显示的是公司示例，请在工具条手动切换到对应数据源。' },
          { type: 'info', text: 'GET /api/onto/graph-spaces 返回图谱模块的空间列表，用于在本体侧新建图谱时选择归属。' },
          { type: 'tip', text: '支持 Turtle / YAML 导入导出：POST /api/onto/import 与 GET /api/onto/{oid}/export?format=ttl。' }
        ]
      },
      {
        id: 'onto-api',
        title: '接口参考：本体图谱 API',
        kind: 'api',
        lead: '服务：py-genai-ontology（FastAPI）。统一响应格式 {"code":0,"data":...}。本体侧的写操作会自动递增版本号并写审计日志。',
        endpoints: [
          {
            id: 'onto-audit', method: 'GET', path: '/api/onto/audit', title: '审计日志',
            desc: '查询本体相关操作记录。', auth: '登录态（平台 JWT）',
            params: [
              param('oid', 'query', 'number', '本体 ID，0 表示全部', { default: '0' }),
              param('limit', 'query', 'number', '返回条数上限', { default: '200' })
            ]
          },
          {
            id: 'onto-spaces', method: 'GET / POST', path: '/api/onto/spaces', title: '空间列表 / 新建空间',
            desc: 'POST body 为 SpaceIn。', auth: '登录态（平台 JWT）',
            params: [req('name', 'body(POST)', 'string', '空间名称'), param('comment', 'body(POST)', 'string', '备注', { default: '""' })]
          },
          {
            id: 'onto-space-del', method: 'DELETE', path: '/api/onto/spaces/{sid}', title: '删除空间',
            desc: '按 ID 删除本体空间。', auth: '登录态（平台 JWT）',
            params: [req('sid', 'path', 'number', '空间 ID')]
          },
          {
            id: 'onto-list', method: 'GET / POST', path: '/api/onto/ontologies', title: '本体列表 / 新建本体',
            desc: 'POST body 为 OntoIn。', auth: '登录态（平台 JWT）',
            params: [
              req('name', 'body(POST)', 'string', '本体名称'),
              param('space_id', 'body(POST)', 'number', '所属空间', { default: '0' }),
              param('scope', 'body(POST)', 'string', '作用域', { default: 'domain' }),
              param('namespace', 'body(POST)', 'string', '命名空间', { default: '""' }),
              param('authority', 'body(POST)', 'string', '权限级别', { default: 'normal' }),
              param('comment', 'body(POST)', 'string', '备注', { default: '""' })
            ],
            requestExample: 'POST /api/onto/ontologies\n{ "name": "万家家族本体", "space_id": 1, "scope": "domain" }'
          },
          {
            id: 'onto-update', method: 'PUT / DELETE', path: '/api/onto/ontologies/{oid}', title: '更新 / 删除本体',
            desc: 'PUT body 为 OntoIn。', auth: '登录态（平台 JWT）',
            params: [req('oid', 'path', 'number', '本体 ID')]
          },
          {
            id: 'onto-full', method: 'GET', path: '/api/onto/{oid}/full', title: '本体全量详情',
            desc: '一次返回本体基本信息、类、关系规则与映射。', auth: '登录态（平台 JWT）',
            params: [req('oid', 'path', 'number', '本体 ID')]
          },
          {
            id: 'onto-class-add', method: 'POST', path: '/api/onto/classes', title: '新增类',
            desc: 'POST body 为 ClassIn。', auth: '登录态（平台 JWT）',
            params: [
              req('ontologyId', 'body', 'number', '所属本体 ID'),
              req('name', 'body', 'string', '类名称'),
              param('parentName', 'body', 'string', '父类名称', { default: '""' }),
              param('comment', 'body', 'string', '说明', { default: '""' })
            ]
          },
          {
            id: 'onto-class-update', method: 'PUT / DELETE', path: '/api/onto/classes/{cid}', title: '更新 / 删除类',
            desc: 'PUT body 为 ClassIn。', auth: '登录态（平台 JWT）',
            params: [req('cid', 'path', 'number', '类 ID')]
          },
          {
            id: 'onto-rel-add', method: 'POST', path: '/api/onto/rels', title: '新增关系规则',
            desc: 'POST body 为 RelIn。', auth: '登录态（平台 JWT）',
            params: [
              req('ontologyId', 'body', 'number', '所属本体 ID'),
              req('name', 'body', 'string', '关系名称'),
              req('subjClass', 'body', 'string', '主体类名'),
              req('objClass', 'body', 'string', '客体类名'),
              param('cardinality', 'body', 'string', '基数：one / many', { default: 'many' }),
              param('nullable', 'body', 'boolean', '是否可空', { default: 'true' }),
              param('inheritsFrom', 'body', 'string', '继承的关系名', { default: '""' }),
              param('comment', 'body', 'string', '说明', { default: '""' })
            ]
          },
          {
            id: 'onto-rel-update', method: 'PUT / DELETE', path: '/api/onto/rels/{rid}', title: '更新 / 删除关系规则',
            desc: 'PUT body 为 RelIn。', auth: '登录态（平台 JWT）',
            params: [req('rid', 'path', 'number', '关系 ID')]
          },
          {
            id: 'onto-map-add', method: 'POST', path: '/api/onto/mappings', title: '新增映射',
            desc: 'POST body 为 MapIn，把本体类型映射到物理类型。', auth: '登录态（平台 JWT）',
            params: [
              req('ontologyId', 'body', 'number', '所属本体 ID'),
              req('ontoType', 'body', 'string', '本体类型名'),
              req('physicalType', 'body', 'string', '物理类型名'),
              param('kind', 'body', 'string', '映射种类：node / edge', { default: 'node' })
            ]
          },
          {
            id: 'onto-map-del', method: 'DELETE', path: '/api/onto/mappings/{mid}', title: '删除映射',
            desc: '按 ID 删除映射。', auth: '登录态（平台 JWT）',
            params: [req('mid', 'path', 'number', '映射 ID')]
          },
          {
            id: 'onto-import', method: 'POST', path: '/api/onto/import', title: '导入本体',
            desc: '导入 Turtle 或 YAML 文本。', auth: '登录态（平台 JWT）',
            params: [
              req('ontologyId', 'body', 'number', '目标本体 ID'),
              req('text', 'body', 'string', '本体定义文本'),
              param('format', 'body', 'string', '格式：ttl / yaml', { default: 'ttl' })
            ]
          },
          {
            id: 'onto-export', method: 'GET', path: '/api/onto/{oid}/export', title: '导出本体',
            desc: '按指定格式导出本体定义。', auth: '登录态（平台 JWT）',
            params: [
              req('oid', 'path', 'number', '本体 ID'),
              param('format', 'query', 'string', '导出格式：ttl / yaml', { default: 'ttl' })
            ]
          },
          {
            id: 'onto-check', method: 'GET', path: '/api/onto/{oid}/check', title: '一致性检查',
            desc: '检查本体内部冲突、孤立类等一致性问题。', auth: '登录态（平台 JWT）',
            params: [req('oid', 'path', 'number', '本体 ID')]
          },
          {
            id: 'onto-versions', method: 'GET', path: '/api/onto/{oid}/versions', title: '版本列表',
            desc: '列出本体版本快照。', auth: '登录态（平台 JWT）',
            params: [req('oid', 'path', 'number', '本体 ID')]
          },
          {
            id: 'onto-version-detail', method: 'GET', path: '/api/onto/{oid}/versions/{no}', title: '版本详情',
            desc: '查看指定版本快照内容。', auth: '登录态（平台 JWT）',
            params: [req('oid', 'path', 'number', '本体 ID'), req('no', 'path', 'string', '版本号')]
          },
          {
            id: 'onto-version-restore', method: 'POST', path: '/api/onto/{oid}/versions/{no}/restore', title: '恢复版本',
            desc: '把本体恢复到指定版本。', auth: '登录态（平台 JWT）',
            params: [req('oid', 'path', 'number', '本体 ID'), req('no', 'path', 'string', '版本号')]
          },
          {
            id: 'onto-graph-spaces', method: 'GET', path: '/api/onto/graph-spaces', title: '图谱空间列表',
            desc: '返回图谱模块的空间列表，供本体侧创建图谱时选择归属。', auth: '登录态（平台 JWT）', params: []
          },
          {
            id: 'onto-graph-create', method: 'POST', path: '/api/onto/graphs', title: '本体侧创建图谱',
            desc: '在本体侧创建图谱，数据落在图谱库并标记来源为 ontology（图谱侧只读）。',
            auth: '登录态（平台 JWT）',
            params: [
              req('name', 'body', 'string', '图谱名称'),
              param('space_id', 'body', 'number', '图谱空间 ID', { default: '0' }),
              param('db_type', 'body', 'string', '数据库类型', { default: 'sqlite' }),
              param('db_config', 'body', 'string', '数据库配置', { default: '""' }),
              param('description', 'body', 'string', '说明', { default: '""' })
            ]
          },
          {
            id: 'onto-datasources', method: 'GET / POST', path: '/api/onto/datasources', title: '图数据源列表 / 新增',
            desc: '注册或列出图数据源，本体通过数据源引用 graph.db 中的图谱实例。',
            auth: '登录态（平台 JWT）',
            params: [
              param('name', 'body(POST)', 'string', '数据源名称'),
              param('type', 'body(POST)', 'string', '数据源类型', { default: 'neo4j' }),
              param('config', 'body(POST)', 'object', '连接配置，如 { "gid": 9 }', { default: '{}' })
            ],
            requestExample: 'POST /api/onto/datasources\n{ "name": "万家图谱·graph.db", "type": "graph-db", "config": { "gid": 9 } }'
          },
          {
            id: 'onto-graph-data', method: 'GET', path: '/api/onto/graph-data', title: '按数据源取图数据',
            desc: '返回指定图数据源的原始图数据（节点与边）。', auth: '登录态（平台 JWT）',
            params: [param('ds', 'query', 'number', '数据源 ID', { default: '1' })]
          },
          {
            id: 'onto-view-graph',
            method: 'GET', path: '/api/onto/{oid}/view-graph', title: '本体投影视图（数据关系图）',
            desc: '按本体的 class / mapping 规则，把指定数据源的物理数据投影成数据关系视图，返回可视化的节点与边（含状态、属性等）。',
            auth: '登录态（平台 JWT）',
            params: [
              req('oid', 'path', 'number', '本体 ID'),
              param('ds', 'query', 'number', '图数据源 ID', { default: '1' })
            ],
            requestExample: 'GET /api/onto/5/view-graph?ds=3',
            notes: [
              '前端「数据关系图」tab 会自动匹配本体名相近的数据源，并在工具条标注来源（如 graph.db · 图谱 #9）。',
              '视图按 props.辈分 / props.实体类型 等字段分群，以圆形 hub + 同心环放射布局展示。'
            ]
          }
        ]
      }
    ],
    source: 'backend/py-genai-ontology/app/controller/onto_controller.py, dto/onto_dto.py, service/onto_service.py'
  },

  /* ============================ 开发者中心 · API Key ============================ */
  {
    id: 'apikey',
    name: '开发者中心 · API Key',
    icon: 'K',
    color: '#4D6BFE',
    desc: '创建与管理平台 API Key（sk-...），配置模型白名单、有效期与调用配额。',
    sections: [
      {
        id: 'apikey-flow',
        title: '使用教程：创建与管理 API Key',
        kind: 'tutorial',
        lead: 'API Key 是调用模型数据面（/v1/**）的凭据，本身也是被管理的资源。在「开发者中心 → API Key」页面可以创建、启停、轮转、延期和删除密钥，并配置可用模型白名单、有效期与 rpm/tpm/cc 配额。管理接口由前端在 Authorization 头透传当前登录用户的 token；不要把 sk- Key 当作管理接口的凭据。',
        steps: [
          {
            title: '1. 创建密钥',
            body: '调用 POST /api/apikeys，至少填写 name。创建成功后响应中会返回一次完整的 apiKey（sk- 前缀 + 48 位十六进制），请立即保存——列表接口只返回掩码形式，之后无法再查看完整值。',
            code: `POST /api/apikeys
{
  "name": "客服机器人",
  "owner": "admin",
  "expiryType": "date",
  "expiryDate": "2027-01-01",
  "models": ["gpt-4o-mini", "qwen-plus"],
  "rpm": 60, "tpm": 120000, "cc": 4,
  "remark": "生产环境使用"
}`
          },
          {
            title: '2. 在模型中调用',
            body: '把完整 Key 放到 Authorization: Bearer <apiKey> 头中调用 /v1/chat/completions 等数据面接口。可用 GET /v1/me 自检 Key 的名称、模型白名单与配额。',
            code: `curl https://<网关地址>/v1/me \\
  -H "Authorization: Bearer sk-xxxxxxxx"`
          },
          {
            title: '3. 维护与轮换',
            body: 'GET /api/apikeys 列表返回掩码 Key；POST /api/apikeys/{id}/rotate 生成新 Key 并使旧 Key 立即失效；POST /api/apikeys/{id}/renew 延期一年；PUT /api/apikeys/{id} 可修改白名单、配额、启停状态或设为永久有效。'
          }
        ],
        notes: [
          { type: 'warn', text: '完整 Key 仅在创建和轮转时返回一次，请妥善保存。列表中的 apiKey 形如 sk-xxxxxx...xxxx，不可用于调用。' },
          { type: 'info', text: 'models 传空数组表示不限制模型；rpm / tpm / cc 只有 >0 的值才会保存，否则为不限制。' },
          { type: 'tip', text: 'GET /api/apikeys/usable 返回当前用户可用（status=1 且未过期）的完整 Key 列表，体验中心等内部页面用它自动填充，不要暴露给外部调用方。' }
        ]
      },
      {
        id: 'apikey-api',
        title: '接口参考：API Key API',
        kind: 'api',
        lead: '服务：jv-genai-apikey（Spring Boot，端口 38091），路径前缀 /api/apikeys。统一响应包装 {"code":0,"message":"ok","data":...}。请求体为 JSON 对象。',
        endpoints: [
          {
            id: 'key-list', method: 'GET', path: '/api/apikeys', title: '密钥列表（掩码）',
            desc: '分页查询 API Key，返回的 apiKey 为掩码形式。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('owner', 'query', 'string', '按 owner 过滤'),
              param('keyword', 'query', 'string', '按名称 / Key / keyId 模糊匹配'),
              param('page', 'query', 'number', '页码', { default: '1' }),
              param('size', 'query', 'number', '每页条数', { default: '50' })
            ],
            responseFields: [
              field('total', 'number', '总条数'),
              field('list[].id', 'number', '记录 ID'),
              field('list[].name', 'string', '密钥名称'),
              field('list[].keyId', 'string', '业务 Key ID，格式 kid + 8 位数字'),
              field('list[].apiKey', 'string', '掩码 Key，如 sk-xxxxxx...xxxx'),
              field('list[].owner', 'string', '归属用户'),
              field('list[].expiryDate', 'string', '过期日期 yyyy-MM-dd，null 为永久'),
              field('list[].models', 'array<string>', '模型白名单'),
              field('list[].fields', 'array<string>', '开放字段'),
              field('list[].org', 'object', '归属组织 {company,dept,business}'),
              field('list[].rpm / tpm / cc', 'number', '限流配额'),
              field('list[].status', 'number', '1 启用 / 0 停用'),
              field('list[].lastUsedAt', 'string', '最后使用时间'),
              field('list[].createdAt', 'string', '创建时间')
            ]
          },
          {
            id: 'key-usable', method: 'GET', path: '/api/apikeys/usable', title: '当前用户可用密钥',
            desc: '返回状态为启用且未过期的 Key 完整值，最多 100 条。供内部页面自动填充使用。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [param('owner', 'query', 'string', '按 owner 过滤')],
            notes: ['此接口返回完整 Key，仅供受信任的内部前端使用，不要对外暴露。']
          },
          {
            id: 'key-create', method: 'POST', path: '/api/apikeys', title: '创建密钥',
            desc: '新建 API Key，完整 Key 仅本次返回。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              req('name', 'body', 'string', '密钥名称，不能为空'),
              param('owner', 'body', 'string', '归属用户'),
              param('expiryType', 'body', 'string', '传 never 或留空表示永不过期；传 date 时按 expiryDate 设置', { default: 'never' }),
              param('expiryDate', 'body', 'string', '过期日期 yyyy-MM-dd，仅 expiryType=date 时生效'),
              param('models', 'body', 'array/string', '模型白名单，空表示不限制'),
              param('fields', 'body', 'array/string', '开放字段'),
              param('org', 'body', 'object', '{company,dept,business}'),
              param('rpm', 'body', 'number', '每分钟请求数上限，>0 才保存'),
              param('tpm', 'body', 'number', '每分钟 token 数上限，>0 才保存'),
              param('cc', 'body', 'number', '最大并发数，>0 才保存'),
              param('remark', 'body', 'string', '备注')
            ],
            requestExample: `POST /api/apikeys
{
  "name": "客服机器人",
  "expiryType": "date", "expiryDate": "2027-01-01",
  "models": ["gpt-4o-mini"], "rpm": 60, "tpm": 120000, "cc": 4
}`,
            responseExample: '{ "code": 0, "data": { "id": 12, "name": "客服机器人", "keyId": "kid20261123", "apiKey": "sk-3f9a...c21b", "status": 1 } }'
          },
          {
            id: 'key-update', method: 'PUT', path: '/api/apikeys/{id}', title: '更新密钥',
            desc: '修改名称、白名单、配额、备注、启停状态或设为永久有效。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              req('id', 'path', 'number', '记录 ID'),
              param('name / owner / models / fields / org / rpm / tpm / cc / remark', 'body', 'any', '同创建接口字段'),
              param('status', 'body', 'number', '1 启用 / 0 停用'),
              param('expiryNever', 'body', 'boolean', '传 true 时把过期时间置空，永久有效', { default: 'false' })
            ],
            notes: ['expiryNever 只在 PUT 生效；创建时永久有效使用 expiryType=never。']
          },
          {
            id: 'key-rotate', method: 'POST', path: '/api/apikeys/{id}/rotate', title: '轮转密钥',
            desc: '生成新 Key 并使旧 Key 立即失效，同时清空最后使用时间。不存在时返回 404。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [req('id', 'path', 'number', '记录 ID')],
            responseExample: '{ "code": 0, "data": { "id": 12, "apiKey": "sk-新密钥（完整，仅本次返回）" } }'
          },
          {
            id: 'key-renew', method: 'POST', path: '/api/apikeys/{id}/renew', title: '延期一年',
            desc: '在原过期日（若已过期则今天）基础上延长一年。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [req('id', 'path', 'number', '记录 ID')],
            responseExample: '{ "code": 0, "data": { "id": 12, "expiryDate": "2027-11-23" } }'
          },
          {
            id: 'key-delete', method: 'DELETE', path: '/api/apikeys/{id}', title: '删除密钥',
            desc: '永久删除密钥，删除后使用该 Key 的调用将返回 401。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [req('id', 'path', 'number', '记录 ID')]
          }
        ]
      }
    ],
    source: 'backend/jv-genai-apikey/.../controller/ApiKeyController.java'
  },

  /* ============================ 开发者中心 · 账单 ============================ */
  {
    id: 'billing',
    name: '开发者中心 · 账单',
    icon: 'B',
    color: '#00A870',
    desc: '查询余额、本月消费与充值汇总，查看订单列表并发起充值。',
    sections: [
      {
        id: 'billing-flow',
        title: '使用教程：余额与充值',
        kind: 'tutorial',
        lead: '模型调用按模型等级单价 × token 用量实时扣费，扣费记录写入账单。余额位于余额表（固定 id=1），订单分为 topup（充值）与 consume（消费）两类，列表只返回 status=success 的订单。',
        steps: [
          {
            title: '1. 查看余额概览',
            body: '调用 GET /api/billing/summary 获取余额、本月消费、本月充值和今日消费。前端「账单」页顶部大卡即来自此接口。',
            code: 'GET /api/billing/summary'
          },
          {
            title: '2. 查看订单明细',
            body: 'GET /api/billing/orders 支持按 type（topup / consume）过滤与分页。更细的筛选可用 GET /api/billing/recharges（充值记录）与 GET /api/billing/consumes（消费账单），均支持 from / to 日期区间。'
          },
          {
            title: '3. 充值',
            body: 'POST /api/billing/topup 为模拟支付，提交后立即入账并生成订单号（R + 时间戳 + 3 位随机数）。amount 必须 >0 且 ≤ 1,000,000。',
            code: `POST /api/billing/topup
{ "amount": 100, "channel": "alipay", "remark": "测试充值" }`
          }
        ],
        notes: [
          { type: 'info', text: 'channel 可选 alipay / wechat / bank_card / balance，默认 balance。' },
          { type: 'info', text: 'GET /api/billing/monthly 返回按月汇总（充值、消费、净额）；GET /api/billing/channel-stats 返回各充值渠道笔数与金额。' }
        ]
      },
      {
        id: 'billing-api',
        title: '接口参考：账单 API',
        kind: 'api',
        lead: '服务：jv-genai-billing（Spring Boot，端口 38092），路径前缀 /api/billing。统一响应包装 {"code":0,"message":"ok","data":...}。',
        endpoints: [
          {
            id: 'bill-summary', method: 'GET', path: '/api/billing/summary', title: '余额概览',
            desc: '返回余额、本月消费 / 充值、今日消费。',
            auth: '浏览器用户 token（Authorization 头透传）', params: [],
            responseExample: '{ "code": 0, "data": { "balance": 1250.50, "monthConsume": 88.20, "monthTopup": 1000, "todayConsume": 12.30 } }'
          },
          {
            id: 'bill-orders', method: 'GET', path: '/api/billing/orders', title: '订单列表',
            desc: '分页查询订单，可按类型过滤。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('type', 'query', 'string', 'topup 充值 / consume 消费，留空为全部'),
              param('page', 'query', 'number', '页码', { default: '1' }),
              param('size', 'query', 'number', '每页条数', { default: '20' })
            ],
            responseFields: [
              field('total', 'number', '总条数'),
              field('list[].orderNo', 'string', '订单号'),
              field('list[].type', 'string', 'topup / consume'),
              field('list[].amount', 'number', '金额'),
              field('list[].balanceAfter', 'number', '变动后余额'),
              field('list[].channel', 'string', '支付渠道'),
              field('list[].status', 'string', 'success'),
              field('list[].createdAt', 'string', '创建时间')
            ]
          },
          {
            id: 'bill-topup', method: 'POST', path: '/api/billing/topup', title: '发起充值',
            desc: '模拟支付并立即入账。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              req('amount', 'body', 'number', '充值金额，必须 >0 且 ≤ 1,000,000'),
              param('channel', 'body', 'string', 'alipay / wechat / bank_card / balance', { default: 'balance' }),
              param('remark', 'body', 'string', '备注')
            ],
            requestExample: 'POST /api/billing/topup\n{ "amount": 100, "channel": "alipay" }'
          },
          {
            id: 'bill-recharges', method: 'GET', path: '/api/billing/recharges', title: '充值记录',
            desc: '仅返回 type=topup 的成功订单，size 内部钳制 1~100。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('channel', 'query', 'string', '按渠道过滤'),
              param('from / to', 'query', 'string', '日期区间 yyyy-MM-dd，from > to 返回 400'),
              param('page', 'query', 'number', '页码', { default: '1' }),
              param('size', 'query', 'number', '每页条数', { default: '20' })
            ]
          },
          {
            id: 'bill-consumes', method: 'GET', path: '/api/billing/consumes', title: '消费账单',
            desc: '仅返回 type=consume 的成功订单。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('from / to', 'query', 'string', '日期区间 yyyy-MM-dd'),
              param('page', 'query', 'number', '页码', { default: '1' }),
              param('size', 'query', 'number', '每页条数', { default: '20' })
            ]
          },
          {
            id: 'bill-channels', method: 'GET', path: '/api/billing/channel-stats', title: '渠道统计',
            desc: '按充值渠道统计笔数与金额。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [param('from / to', 'query', 'string', '日期区间 yyyy-MM-dd')],
            responseExample: '{ "code": 0, "data": [{ "channel": "alipay", "count": 3, "total": 500 }] }'
          },
          {
            id: 'bill-monthly', method: 'GET', path: '/api/billing/monthly', title: '按月汇总',
            desc: '按 yyyy-MM 分组返回每月充值 / 消费合计与净额。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [param('from / to', 'query', 'string', '日期区间 yyyy-MM-dd')],
            responseFields: [
              field('month', 'string', 'yyyy-MM'),
              field('topupTotal / topupCount', 'number', '充值金额 / 笔数'),
              field('consumeTotal / consumeCount', 'number', '消费金额 / 笔数'),
              field('net', 'number', '净额 = 充值 - 消费')
            ]
          }
        ]
      }
    ],
    source: 'backend/jv-genai-billing/.../controller/BillingController.java'
  },

  /* ============================ 开发者中心 · 成本统计 ============================ */
  {
    id: 'costs',
    name: '开发者中心 · 成本统计',
    icon: 'C',
    color: '#7B5CFF',
    desc: '按日、按模型、按服务分析 token 用量与成本，支持任意区间汇总。',
    sections: [
      {
        id: 'costs-flow',
        title: '使用教程：成本分析',
        kind: 'tutorial',
        lead: '成本数据来自路由网关转发后写入的 tb_cost_daily 表，每次调用按模型等级单价 × token 用量记账。成本统计提供今日/本月概览、按日趋势、按模型分布、按服务分布与区间汇总五种视图。',
        steps: [
          {
            title: '1. 看概览与趋势',
            body: 'GET /api/costs/overview 返回今日与本月的 cost、requests、tokens；GET /api/costs/daily 返回按日趋势，默认近 14 天，可用 days（1~90）或 from/to 指定区间。'
          },
          {
            title: '2. 分析模型与服务分布',
            body: 'GET /api/costs/by-model 按模型统计成本与请求数；GET /api/costs/by-service 按服务统计（仅支持 days 参数，不支持 from/to）。'
          },
          {
            title: '3. 区间汇总',
            body: 'GET /api/costs/summary 需要同时传 from 与 to（yyyy-MM-dd），要求 from ≤ to、不早于一年前、跨度 ≤ 366 天，否则返回 400。',
            code: 'GET /api/costs/summary?from=2026-11-01&to=2026-11-23'
          }
        ],
        notes: [
          { type: 'info', text: '前端「成本统计」页使用 from/to 覆盖 days 参数，因此天数选择由日期区间决定。' },
          { type: 'tip', text: '首页仪表盘也调用 overview / summary / daily / by-model 四个接口渲染概览卡片。' }
        ]
      },
      {
        id: 'costs-api',
        title: '接口参考：成本统计 API',
        kind: 'api',
        lead: '服务：jv-genai-costs（Spring Boot，端口 38093），路径前缀 /api/costs。统一响应包装 {"code":0,"message":"ok","data":...}。',
        endpoints: [
          {
            id: 'cost-overview', method: 'GET', path: '/api/costs/overview', title: '成本概览',
            desc: '返回今日与本月成本、请求数、token 数。',
            auth: '浏览器用户 token（Authorization 头透传）', params: [],
            responseExample: '{ "code": 0, "data": { "today": {"cost":12.3,"requests":48,"tokens":12800}, "month": {"cost":88.2,"requests":312,"tokens":96000} } }'
          },
          {
            id: 'cost-daily', method: 'GET', path: '/api/costs/daily', title: '按日趋势',
            desc: '按天返回成本趋势；from/to 合法区间优先于 days。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('days', 'query', 'number', '近 N 天，范围 1~90', { default: '14' }),
              param('from / to', 'query', 'string', '日期区间 yyyy-MM-dd')
            ],
            responseFields: [
              field('statDate', 'string', '日期 yyyy-MM-dd'),
              field('cost', 'number', '当日成本'),
              field('requests', 'number', '请求数'),
              field('tokens', 'number', 'token 总数')
            ]
          },
          {
            id: 'cost-model', method: 'GET', path: '/api/costs/by-model', title: '按模型分布',
            desc: '按模型聚合成本、请求数与 token 数。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('days', 'query', 'number', '近 N 天，范围 1~90', { default: '30' }),
              param('from / to', 'query', 'string', '日期区间 yyyy-MM-dd')
            ],
            responseExample: '{ "code": 0, "data": [{ "model": "gpt-4o-mini", "cost": 12.5, "requests": 88, "tokens": 24000 }] }'
          },
          {
            id: 'cost-summary', method: 'GET', path: '/api/costs/summary', title: '区间汇总',
            desc: '任意合法区间的成本汇总。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              req('from', 'query', 'string', '开始日期 yyyy-MM-dd'),
              req('to', 'query', 'string', '结束日期 yyyy-MM-dd')
            ],
            responseFields: [
              field('cost', 'number', '区间总成本'),
              field('requests', 'number', '总请求数'),
              field('tokens', 'number', '总 token 数'),
              field('activeDays', 'number', '有调用的天数')
            ],
            notes: ['要求 from ≤ to、不早于一年前、跨度 ≤ 366 天，否则 400。']
          },
          {
            id: 'cost-service', method: 'GET', path: '/api/costs/by-service', title: '按服务分布',
            desc: '按服务 ID 聚合成本与请求数。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [param('days', 'query', 'number', '近 N 天，范围 1~90', { default: '30' })],
            notes: ['此接口不支持 from/to 参数。']
          }
        ]
      }
    ],
    source: 'backend/jv-genai-costs/.../controller/CostController.java'
  },

  /* ============================ 开发者中心 · 使用日志 ============================ */
  {
    id: 'logs',
    name: '开发者中心 · 使用日志',
    icon: 'L',
    color: '#ED7B2F',
    desc: '检索每次模型调用的用量与状态，并通过 traceId 查看完整请求 / 响应内容。',
    sections: [
      {
        id: 'logs-flow',
        title: '使用教程：日志检索与链路追踪',
        kind: 'tutorial',
        lead: '每次模型调用都会写入一条使用日志（tb_usage_log），记录 Key、模型、token、成本、耗时、状态与 IP；同时写入内容日志（tb_relay_log）保存请求体与响应体。两者通过 traceId 对齐，可从使用日志下钻到完整链路。',
        steps: [
          {
            title: '1. 看今日汇总',
            body: 'GET /api/logs/summary 返回今日请求数、成功率、token 数与成本；GET /api/logs/apikeys 返回调用量 Top 50 的 Key。'
          },
          {
            title: '2. 多条件检索',
            body: 'GET /api/logs 支持日期区间、模型、状态、API Key ID 与关键字筛选，分页返回。endDate 含当天（内部按次日 0 点取 <）。',
            code: 'GET /api/logs?startDate=2026-11-23&endDate=2026-11-23&model=gpt-4o-mini&status=success&page=1&size=20'
          },
          {
            title: '3. 查看完整链路',
            body: '从列表行拿到 traceId 后，调用 GET /api/logs/relay/{traceId} 查看请求问题、完整请求体、响应体、状态码、是否流式与错误信息。内容日志单侧截断 64KB。',
            code: 'GET /api/logs/relay/trace-20261123-abc123'
          }
        ],
        notes: [
          { type: 'info', text: 'keyword 模糊匹配 trace_id、api_key_id 与 ip；apiKeyId 为精确匹配。' },
          { type: 'tip', text: 'status 的取值与上游调用结果一致（success / fail），失败记录可在内容日志中查看 errorMsg。' }
        ]
      },
      {
        id: 'logs-api',
        title: '接口参考：使用日志 API',
        kind: 'api',
        lead: '服务：jv-genai-logs（Spring Boot，端口 38094），路径前缀 /api/logs。统一响应包装 {"code":0,"message":"ok","data":...}。',
        endpoints: [
          {
            id: 'log-list', method: 'GET', path: '/api/logs', title: '使用日志检索',
            desc: '多条件分页检索调用日志。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [
              param('startDate / endDate', 'query', 'string', '日期区间 yyyy-MM-dd，endDate 含当天'),
              param('model', 'query', 'string', '按模型过滤'),
              param('status', 'query', 'string', '按状态过滤，如 success / fail'),
              param('apiKeyId', 'query', 'string', '按 API Key ID 精确匹配'),
              param('keyword', 'query', 'string', '模糊匹配 trace_id / api_key_id / ip'),
              param('page', 'query', 'number', '页码', { default: '1' }),
              param('size', 'query', 'number', '每页条数', { default: '20' })
            ],
            responseFields: [
              field('total', 'number', '总条数'),
              field('list[].traceId', 'string', '链路 ID，用于下钻内容日志'),
              field('list[].apiKeyId / apiKeyName', 'string', '调用使用的 Key'),
              field('list[].model', 'string', '模型名'),
              field('list[].serviceId', 'string', '服务标识'),
              field('list[].promptTokens / completionTokens / totalTokens', 'number', 'token 用量'),
              field('list[].cost', 'number', '本次调用成本'),
              field('list[].durationMs', 'number', '耗时毫秒'),
              field('list[].status', 'string', 'success / fail'),
              field('list[].ip', 'string', '调用方 IP'),
              field('list[].createdAt', 'string', '调用时间')
            ]
          },
          {
            id: 'log-summary', method: 'GET', path: '/api/logs/summary', title: '今日汇总',
            desc: '今日请求数、成功率（百分数）、token 数与成本。',
            auth: '浏览器用户 token（Authorization 头透传）', params: [],
            responseExample: '{ "code": 0, "data": { "requests": 128, "successRate": 98.4, "tokens": 56000, "cost": 18.6 } }'
          },
          {
            id: 'log-apikeys', method: 'GET', path: '/api/logs/apikeys', title: 'Key 调用量 Top50',
            desc: '按调用次数排序返回前 50 个 Key。',
            auth: '浏览器用户 token（Authorization 头透传）', params: [],
            responseExample: '{ "code": 0, "data": [{ "id": 3, "name": "客服机器人", "count": 88 }] }'
          },
          {
            id: 'log-relay', method: 'GET', path: '/api/logs/relay/{traceId}', title: '链路详情',
            desc: '按 traceId 查看完整请求 / 响应内容，无匹配返回 null。',
            auth: '浏览器用户 token（Authorization 头透传）',
            params: [req('traceId', 'path', 'string', '使用日志中的 traceId')],
            responseFields: [
              field('question', 'string', '从 messages 最后一条 user 消息提取的当前问题'),
              field('requestBody', 'string', '完整请求体（截断至 64KB）'),
              field('responseBody', 'string', '完整响应体，流式请求为聚合后的 JSON'),
              field('statusCode', 'number', '上游 HTTP 状态码'),
              field('isStream', 'boolean', '是否流式请求'),
              field('errorMsg', 'string', '错误信息，成功时为空')
            ]
          }
        ]
      }
    ],
    source: 'backend/jv-genai-logs/.../controller/LogController.java'
  }
]

export function findDoc(docId) {
  for (const mod of docModules) {
    const sec = mod.sections.find(s => s.id === docId)
    if (sec) return { mod, sec }
  }
  return null
}
