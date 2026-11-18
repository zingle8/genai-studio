CREATE DATABASE IF NOT EXISTS genai_dashboard DEFAULT CHARACTER SET utf8mb4;
USE genai_dashboard;
CREATE TABLE IF NOT EXISTS tb_platform_service (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  service_id VARCHAR(64) NOT NULL,
  service_name VARCHAR(64) NOT NULL,
  module VARCHAR(64) NOT NULL,
  port INT NOT NULL,
  status VARCHAR(8) DEFAULT 'unknown' COMMENT 'up/down/unknown',
  checked_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台服务清单';
INSERT IGNORE INTO tb_platform_service(service_id, service_name, module, port) VALUES
('jv-genai-auth', '认证授权服务', 'jv-genai-auth', 38081),
('jv-genai-dashboard', '控制台服务', 'jv-genai-dashboard', 38082),
('jv-genai-mcpgateway', 'MCP 网关', 'jv-genai-mcpgateway', 38084),
('jv-genai-agentgateway', 'Agent 网关', 'jv-genai-agentgateway', 38085),
('jv-genai-models', '模型管理服务', 'jv-genai-models', 38086),
('jv-genai-config', '配置中心', 'jv-genai-config', 38087),
('jv-genai-chats', '会话对话服务', 'jv-genai-chats', 38088),
('jv-genai-user', '用户服务', 'jv-genai-user', 38089),
('jv-genai-prompt', '提示词服务', 'jv-genai-prompt', 38090),
('jv-genai-apikey', 'API 密钥服务', 'jv-genai-apikey', 38091),
('jv-genai-billing', '计费服务', 'jv-genai-billing', 38092),
('jv-genai-costs', '成本核算服务', 'jv-genai-costs', 38093),
('jv-genai-logs', '日志服务', 'jv-genai-logs', 38094),
('jv-genai-docs', '文档服务', 'jv-genai-docs', 38097);
