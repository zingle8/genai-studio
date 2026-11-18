CREATE DATABASE IF NOT EXISTS genai_mcpgateway DEFAULT CHARACTER SET utf8mb4;
USE genai_mcpgateway;
CREATE TABLE IF NOT EXISTS tb_mcp_server (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  endpoint VARCHAR(256) NOT NULL,
  auth_type VARCHAR(16) DEFAULT 'none' COMMENT 'none/token/oauth',
  status TINYINT NOT NULL DEFAULT 1,
  remark VARCHAR(512) DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MCP 服务注册';
INSERT IGNORE INTO tb_mcp_server(name, endpoint, auth_type, status, remark) VALUES
('天气查询 MCP', 'http://127.0.0.1:8201/mcp/weather', 'none', 1, '演示：城市天气查询工具'),
('数据库查询 MCP', 'http://127.0.0.1:8201/mcp/db', 'token', 1, '受限 SQL 查询工具'),
('文件检索 MCP', 'http://127.0.0.1:8201/mcp/files', 'none', 0, '本地文件检索（未启用）');
