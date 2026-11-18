-- ============================================================
-- 19：模型广场补齐 Ollama 本地模型（base_url localhost:11434，OpenAI 兼容）
--     文本/多模态/OCR → /v1/chat/completions；向量 → /v1/embeddings
-- ============================================================
USE genai_models;

INSERT IGNORE INTO tb_model_info
  (name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, tier, status, description) VALUES
('Ollama-GLM-4.7-Flash',   'glm-4.7-flash:latest',        '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, '本地 Ollama GLM-4.7-Flash（19GB）'),
('Ollama-Qwen3.8',         'qwen3.8:latest',              '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, '本地 Ollama Qwen3.8（17GB）'),
('Ollama-Gemma4-31B',      'gemma4:31b',                  '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, '本地 Ollama Gemma4 31B（19GB）'),
('Ollama-GPT-OSS-20B',     'gpt-oss:20b',                 '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, '本地 Ollama GPT-OSS 20B（13GB）'),
('Ollama-DeepSeek-R1-32B', 'deepseek-r1:32b',             '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '文本生成', '免费', 1, '本地 Ollama DeepSeek-R1 32B 深度推理'),
('Ollama-Qwen3-VL-8B',     'qwen3-vl:8b',                 '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '多模态', '免费', 1, '本地 Ollama Qwen3-VL 视觉理解'),
('Ollama-MiniCPM-V4.6',    'minicpm-v4.6:1b',             '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '多模态', '免费', 1, '本地 Ollama MiniCPM-V 4.6 多模态'),
('Ollama-MiniCPM-O4.5',    'openbmb/minicpm-o4.5:8b',     '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', '多模态', '免费', 1, '本地 Ollama MiniCPM-O 4.5 全模态'),
('Ollama-MiniCPM-OCR',     'openbmb/minicpm-ocr1.0:q4_0', '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', 'OCR', '免费', 1, '本地 Ollama MiniCPM-OCR 文字识别'),
('Ollama-GLM-OCR',         'glm-ocr:bf16',                '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/chat/completions","format":"openai"}]', 'OCR', '免费', 1, '本地 Ollama GLM-OCR 文字识别'),
('Ollama-Qwen3-Embedding', 'qwen3-embedding:0.6b',        '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/embeddings","format":"openai"}]', '向量', '免费', 1, '本地 Ollama Qwen3-Embedding 向量化'),
('Ollama-Nomic-Embed',     'nomic-embed-text:v1.5',       '本地 Ollama', 'Ollama', 'openai', 'http://localhost:11434', '', '[{"path":"/v1/embeddings","format":"openai"}]', '向量', '免费', 1, '本地 Ollama Nomic-Embed 向量化');

-- 本地 py 服务模型统一为免费档（与 Ollama 本地一致：不计费）
UPDATE tb_model_info SET tier = '免费' WHERE vendor = 'GenAI Studio' AND name LIKE 'studio-%';
