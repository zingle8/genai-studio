-- ============================================================
-- 21：模型广场补齐 MLX 本地模型（base_url 127.0.0.1:38101 → py-genai-infer，避免 Java 解析 localhost 到 IPv6）
--     命名规范：平台对外名 real_name 均为小写 mlx- 前缀，与 Ollama-* 系列对齐
--     infer 侧本地注册表：mlx-别名 → local_models/mlx-community/<目录名>
--     文本/多模态 → /v1/chat/completions（后续叠加 responses/messages）
-- ============================================================
USE genai_models;

INSERT IGNORE INTO tb_model_info
  (name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, tier, status, context_len, description) VALUES
('mlx-glm-4.7-flash',   'mlx-glm-4.7-flash',   '本地 MLX', 'MLX', 'openai', 'http://127.0.0.1:38101', '',
 '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, 202752,
 '本地 MLX GLM-4.7-Flash 4bit（16.9GB，MoE 29.9B，支持 tool/thinking，纯文本 Agent 主战）'),
('mlx-gemma4-26b-a4b',  'mlx-gemma4-26b-a4b',  '本地 MLX', 'MLX', 'openai', 'http://127.0.0.1:38101', '',
 '[{"path":"/v1/chat/completions","format":"openai"}]', '多模态', '免费', 1, 262144,
 '本地 MLX Gemma4 26B A4B IT 4bit（15.4GB，多模态唯一眼睛，走 mlx_vlm）'),
('mlx-gemma4-e4b',      'mlx-gemma4-e4b',      '本地 MLX', 'MLX', 'openai', 'http://127.0.0.1:38101', '',
 '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, 262144,
 '本地 MLX Gemma4 E4B IT 4bit（5.2GB，轻量打杂）'),
('mlx-qwen3.8-27b',     'mlx-qwen3.8-27b',     '本地 MLX', 'MLX', 'openai', 'http://127.0.0.1:38101', '',
 '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, 262144,
 '本地 MLX Qwen3.8 27B 4bit（16.1GB，重武器）');

-- 本地 MLX 模型统一为免费档（与 Ollama 本地一致：不计费）
UPDATE tb_model_info SET tier = '免费' WHERE vendor = 'MLX' AND name LIKE 'mlx-%';

-- GLM 主战模型启用双实例轮询：base_url 逗号分隔多地址，jv-genai-router 按请求原子轮询分发
-- 38101/38102 为两个独立 py-genai-infer 进程（各自全局闸门=1），同模型双进程并发实测安全、吞吐 2.4→4.27 RPS
-- 其余模型仍走单实例 38101
UPDATE tb_model_info SET base_url = 'http://127.0.0.1:38101,http://127.0.0.1:38102'
WHERE name = 'mlx-glm-4.7-flash';
