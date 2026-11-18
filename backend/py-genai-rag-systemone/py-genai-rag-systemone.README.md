# py-genai-rag-systemone — SystemOne 判断模型服务（38109）

systemone 目录用于存放 **System One / Judge 类判断模型**（类似 laya、nanojev 等"一眼定夺"的小型决策模型），当前接入两个：

| 模型 | 后端 | 来源 | 接口前缀 | 题型 |
|------|------|------|---------|------|
| laya | MLX（laya-mlx Agent/Router） | ai-infer/py_laya_mlx | `/v1/laya/*` | choice / score / noul |
| nanojev | torch（Qwen3-0.6B + set-attention） | ai-infer/py_nano_jev | `/v1/nanojev/*` | choice / score / boolean |

## 接口
- `POST /v1/laya/decide`（单 state）、`/v1/laya/decide/batch`（串行批量）、`/v1/laya/route`（Router 语言路由）
- `POST /v1/nanojev/decide`（顶层 states 多 state 批量，合并一次前向）
- `GET /health`（两引擎 ready 状态）、`GET /v1/models`、`GET /v1/config`

## 说明
- nanojev 权重复用 `../py-genai-infer/local_models/NanoJev`（checkpoint 兼容 stage1/、variants/<name>/ 布局）
- **暂不要求跑通/接入网关平台**：torch 与 laya-mlx 依赖分别见 requirements.txt 注释（建议 bge-env / laya-env 两个 venv）
- 引擎前向推理的完整实现见 ai-infer 对应模块的 *_engine.py，骨架已预留接入点
