-- jv-genai-costs：成本日聚合（MySQL 5.7，来源 tb_usage_log T+1 聚合）
CREATE DATABASE IF NOT EXISTS genai_costs DEFAULT CHARACTER SET utf8mb4;
USE genai_costs;

CREATE TABLE IF NOT EXISTS tb_cost_daily (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  stat_date DATE NOT NULL COMMENT '统计日期',
  model VARCHAR(64) NOT NULL COMMENT '模型',
  service_id VARCHAR(64) NOT NULL DEFAULT '' COMMENT '来源服务',
  requests INT NOT NULL DEFAULT 0,
  tokens BIGINT NOT NULL DEFAULT 0,
  cost DECIMAL(12,4) NOT NULL DEFAULT 0 COMMENT '成本（元）',
  KEY idx_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='成本日聚合';

INSERT IGNORE INTO tb_cost_daily(stat_date, model, service_id, requests, tokens, cost) VALUES
('2026-10-25', 'DeepSeek-V3.2', 'jv-genai-chats', 1240, 8640000, 42.1100),
('2026-10-26', 'DeepSeek-V3.2', 'jv-genai-chats', 1102, 7920000, 38.6400),
('2026-10-27', 'GLM-4.7', 'jv-genai-agentgateway', 640, 4210000, 26.9000),
('2026-10-28', 'DeepSeek-R1', 'jv-genai-chats', 420, 5130000, 31.2500),
('2026-10-29', 'DeepSeek-V3.2', 'jv-genai-chats', 1310, 9210000, 44.7300),
('2026-10-30', 'GLM-4.7', 'jv-genai-mcpgateway', 380, 2460000, 15.8800),
('2026-10-31', 'DeepSeek-V3.2', 'jv-genai-chats', 980, 6840000, 33.4700),
('2026-11-01', 'DeepSeek-V3.2', 'jv-genai-chats', 1420, 10100000, 49.2600),
('2026-11-02', 'GLM-4.7', 'jv-genai-agentgateway', 720, 4880000, 30.1500),
('2026-11-03', 'DeepSeek-R1', 'jv-genai-chats', 510, 6180000, 37.6600),
('2026-11-04', 'GLM-Embedding-3', 'py-genai-embedding', 3200, 2400000, 6.1200),
('2026-11-05', 'DeepSeek-V3.2', 'jv-genai-chats', 1180, 8350000, 40.8200),
('2026-11-06', 'GLM-4.7', 'jv-genai-chats', 860, 5720000, 35.5400),
('2026-11-07', 'DeepSeek-V3.2', 'jv-genai-chats', 640, 4310000, 21.0600),
('2026-11-07', 'GLM-Embedding-3', 'py-genai-embedding', 1850, 1310000, 3.3400),
('2026-11-07', 'DeepSeek-R1', 'jv-genai-agentgateway', 210, 2630000, 16.0200);
