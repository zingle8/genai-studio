CREATE DATABASE IF NOT EXISTS genai_config DEFAULT CHARACTER SET utf8mb4;
USE genai_config;
CREATE TABLE IF NOT EXISTS tb_app_config (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  config_key VARCHAR(128) NOT NULL,
  config_value VARCHAR(1024) DEFAULT '',
  remark VARCHAR(512) DEFAULT '',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='平台配置';
INSERT IGNORE INTO tb_app_config(config_key, config_value, remark) VALUES
('platform.name', 'GenAI Studio', '平台名称'),
('platform.app-id', 'app-genai-studio', '网关平台应用 ID'),
('model.default', 'GLM-4.7', '默认模型'),
('ollama.base-url', 'http://127.0.0.1:11434', '本地 Ollama 地址'),
('gateway.user-base-url', 'http://localhost:28081/api', '网关用户服务地址'),
('chat.max-history', '20', '会话保留最大消息数');
