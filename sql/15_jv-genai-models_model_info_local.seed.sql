-- ============================================================
-- 本地模型登记种子数据（模型统一转发架构）
-- 链路：调用方 → jv-genai-router(38100, 按 base_url+url_paths 动态转发)
--       → 本地 Python 推理服务（38101/38103/38104/38109）
-- 外部云端模型由管理面（前端 ModelAdmin / jv-genai-models 38086）按需录入，
-- 录入后 router 即时生效（每请求实时查库，无缓存），无需重启任何服务。
-- ============================================================
USE genai_models;

-- 本地普通生成模型（py-genai-infer 38101：本地加载与推理执行器）
INSERT IGNORE INTO tb_model_info
  (name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, status, description) VALUES
('studio-chat', '', '本地', 'GenAI Studio', 'openai', 'http://localhost:38101', '',
 '[{"path":"/v1/chat/completions","format":"openai"},{"path":"/chat/completions","format":"openai"}]',
 '文本生成', 1, '本地生成模型（本地加载推理；未加载时网关返回 503）');

-- 本地向量模型（py-genai-rag-embedding 38103：BGE-M3 dense/sparse/colbert）
INSERT IGNORE INTO tb_model_info
  (name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, status, description) VALUES
('studio-embedding', '', '本地', 'GenAI Studio', 'openai', 'http://localhost:38103', '',
 '[{"path":"/v1/embeddings","format":"openai"},{"path":"/v1/sparse_embeddings","format":"openai"},{"path":"/v1/colbert_embeddings","format":"openai"},{"path":"/v1/hybrid_embeddings","format":"openai"}]',
 '向量', 1, 'BGE-M3 向量生成（dense/sparse/colbert 三件套）');

-- 本地重排模型（py-genai-rag-reranker 38104：BGE-Reranker-v2-M3）
INSERT IGNORE INTO tb_model_info
  (name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, status, description) VALUES
('studio-reranker', '', '本地', 'GenAI Studio', 'openai', 'http://localhost:38104', '',
 '[{"path":"/v1/rerank","format":"openai"}]',
 '重排', 1, 'BGE-Reranker 重排序服务');

-- 本地判断模型（py-genai-rag-systemone 38109：laya MLX + nanojev torch）
INSERT IGNORE INTO tb_model_info
  (name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, status, description) VALUES
('studio-laya', '', '本地', 'GenAI Studio', 'openai', 'http://localhost:38109', '',
 '[{"path":"/v1/laya/decide","format":"openai"},{"path":"/v1/laya/decide/batch","format":"openai"},{"path":"/v1/laya/route","format":"openai"}]',
 '判断', 1, 'Laya 判断模型（MLX，choice/score/boolean 三题型）'),
('studio-nanojev', '', '本地', 'GenAI Studio', 'openai', 'http://localhost:38109', '',
 '[{"path":"/v1/nanojev/decide","format":"openai"}]',
 '判断', 1, 'NanoJev 判断模型（torch，多 state 合并前向）');
