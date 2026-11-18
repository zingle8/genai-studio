-- jv-genai-logs：使用日志（MySQL 5.7，来源网关接入 SDK 上报汇聚）
CREATE DATABASE IF NOT EXISTS genai_logs DEFAULT CHARACTER SET utf8mb4;
USE genai_logs;

CREATE TABLE IF NOT EXISTS tb_usage_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  trace_id VARCHAR(64) NOT NULL COMMENT '链路 ID',
  api_key_id VARCHAR(64) DEFAULT '' COMMENT 'API Key ID',
  api_key_name VARCHAR(128) DEFAULT '' COMMENT 'API Key 名称',
  model VARCHAR(64) NOT NULL COMMENT '模型',
  service_id VARCHAR(64) NOT NULL DEFAULT '' COMMENT '来源服务',
  prompt_tokens INT NOT NULL DEFAULT 0,
  completion_tokens INT NOT NULL DEFAULT 0,
  total_tokens INT NOT NULL DEFAULT 0,
  cost DECIMAL(12,4) NOT NULL DEFAULT 0 COMMENT '消费（元）',
  duration_ms INT NOT NULL DEFAULT 0,
  status VARCHAR(16) NOT NULL DEFAULT 'success',
  ip VARCHAR(64) DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_created (created_at),
  KEY idx_model (model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='使用日志';

INSERT IGNORE INTO tb_usage_log(trace_id, api_key_id, api_key_name, model, service_id, prompt_tokens, completion_tokens, total_tokens, cost, duration_ms, status, ip, created_at) VALUES
('tr-20261107-0001', 'kid=10051186', 'zcode-api-key', 'DeepSeek-V3.2', 'jv-genai-chats', 3120, 4820, 7940, 0.2860, 3210, 'success', '10.0.12.8', '2026-11-07 09:01:12'),
('tr-20261107-0002', 'kid=10115627', 'embedding-only', 'GLM-Embedding-3', 'py-genai-embedding', 8200, 0, 8200, 0.0120, 410, 'success', '10.0.12.9', '2026-11-07 09:02:40'),
('tr-20261107-0003', 'kid=10071509', 'prod-main-key', 'DeepSeek-R1', 'jv-genai-agentgateway', 12400, 6100, 18500, 0.9100, 12400, 'success', '10.0.13.2', '2026-11-07 09:05:31'),
('tr-20261107-0004', 'kid=10048231', '默认项目', 'GLM-4.7', 'jv-genai-chats', 2210, 1560, 3770, 0.1500, 1810, 'success', '10.0.12.8', '2026-11-07 09:12:05'),
('tr-20261107-0005', 'kid=10051186', 'zcode-api-key', 'DeepSeek-V3.2', 'jv-genai-chats', 4400, 0, 4400, 0.1100, 60200, 'fail', '10.0.12.8', '2026-11-07 09:15:00'),
('tr-20261107-0006', 'kid=10104512', 'analytics-svc', 'GLM-Embedding-3', 'py-genai-embedding', 15600, 0, 15600, 0.0240, 720, 'success', '10.0.14.5', '2026-11-07 09:18:22'),
('tr-20261107-0007', 'kid=10071509', 'prod-main-key', 'DeepSeek-V3.2', 'jv-genai-chats', 5320, 7240, 12560, 0.4520, 4180, 'success', '10.0.13.2', '2026-11-07 09:25:47'),
('tr-20261106-0031', 'kid=10048231', '默认项目', 'GLM-4.7', 'jv-genai-chats', 1810, 2240, 4050, 0.1660, 2050, 'success', '10.0.12.8', '2026-11-06 15:40:12'),
('tr-20261106-0032', 'kid=10082774', 'test-env-key', 'GLM-4.5-Air', 'jv-genai-chats', 990, 640, 1630, 0.0410, 990, 'fail', '10.0.15.1', '2026-11-06 16:02:33'),
('tr-20261106-0033', 'kid=10051186', 'zcode-api-key', 'DeepSeek-R1', 'jv-genai-agentgateway', 8800, 4200, 13000, 0.6400, 9800, 'success', '10.0.12.8', '2026-11-06 17:28:51');
