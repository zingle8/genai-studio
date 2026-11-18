CREATE DATABASE IF NOT EXISTS genai_models DEFAULT CHARACTER SET utf8mb4;
USE genai_models;
CREATE TABLE IF NOT EXISTS tb_model_info (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL COMMENT '模型名（平台对外名称）',
  real_name VARCHAR(128) DEFAULT '' COMMENT '真实模型名（转发上游厂商时使用的模型 ID）',
  provider VARCHAR(64) DEFAULT '' COMMENT '提供方',
  vendor VARCHAR(64) DEFAULT '' COMMENT '模型厂商（智谱/DeepSeek/OpenAI/Anthropic/Google/本地等）',
  api_format VARCHAR(16) DEFAULT 'openai' COMMENT '接口格式：openai/claude/gemini/other',
  base_url VARCHAR(256) DEFAULT '' COMMENT '模型服务 Base URL（外接转发）',
  api_key VARCHAR(512) DEFAULT '' COMMENT '外接模型 API Key（列表返回时掩码）',
  url_paths TEXT COMMENT '接口路径列表JSON:[{path,format}]，如 /chat/completions(openai)、/v1/messages(claude)',
  category VARCHAR(32) DEFAULT '文本生成' COMMENT '分类',
  tier VARCHAR(16) DEFAULT '标准' COMMENT '模型等级：旗舰/标准/免费（关联 tb_model_price 计费单价）',
  context_len INT NULL COMMENT '上下文长度',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 上架 0 下架',
  description VARCHAR(512) DEFAULT '' COMMENT '模型描述（广场列表/卡片摘要）',
  detail TEXT COMMENT '模型详情（广场详情展示，支持较长的介绍）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型信息';
INSERT IGNORE INTO tb_model_info(name, provider, category, tier, context_len, status, description) VALUES
('GLM-4.7', '智谱 AI', '文本生成', '旗舰', 128000, 1, '旗舰文本生成模型'),
('GLM-4.6', '智谱 AI', '文本生成', '标准', 200000, 1, '长上下文文本模型'),
('GLM-4.5-Air', '智谱 AI', '文本生成', '标准', 128000, 1, '轻量高速文本模型'),
('DeepSeek-V3.2', 'DeepSeek', '文本生成', '旗舰', 128000, 1, '通用大模型'),
('DeepSeek-R1', 'DeepSeek', '文本生成', '旗舰', 128000, 1, '深度推理模型'),
('GLM-4V', '智谱 AI', '多模态', '旗舰', 8192, 1, '视觉理解模型'),
('GLM-4V-Flash', '智谱 AI', '多模态', '免费', 8192, 1, '免费视觉模型'),
('GLM-Embedding-3', '智谱 AI', '向量', '标准', 8192, 1, '文本向量化模型'),
('BGE-Large', '本地', '向量', '免费', 512, 1, '本地部署向量化模型');
