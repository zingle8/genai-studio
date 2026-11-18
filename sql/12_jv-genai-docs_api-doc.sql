CREATE DATABASE IF NOT EXISTS genai_docs DEFAULT CHARACTER SET utf8mb4;
USE genai_docs;
CREATE TABLE IF NOT EXISTS tb_api_doc (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  module VARCHAR(64) NOT NULL COMMENT '所属模块',
  method VARCHAR(8) NOT NULL,
  path VARCHAR(256) NOT NULL,
  description VARCHAR(512) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='开放 API 文档';
INSERT IGNORE INTO tb_api_doc(module, method, path, description) VALUES
('认证', 'POST', '/api/auth/login', '账号密码登录，返回 token'),
('认证', 'POST', '/api/auth/register', '注册账号（转发网关）'),
('模型', 'GET', '/api/models', '模型列表（分页/关键字）'),
('模型', 'POST', '/api/models', '注册模型'),
('提示词', 'GET', '/api/prompts', '提示词模板列表'),
('提示词', 'POST', '/api/prompts', '创建模板'),
('会话', 'GET', '/api/chats', '会话列表'),
('会话', 'POST', '/api/chats/{id}/messages', '发送消息（演示回复）'),
('API Key', 'GET', '/api/apikeys', 'API Key 列表（掩码展示）'),
('API Key', 'POST', '/api/apikeys', '创建 Key（仅本次返回完整密钥）'),
('计费', 'GET', '/api/billing/summary', '余额与消费汇总'),
('成本', 'GET', '/api/costs/overview', '今日/本月成本总览'),
('日志', 'GET', '/api/logs', '使用日志检索'),
('MCP', 'GET', '/api/mcp', 'MCP 服务列表'),
('Agent', 'GET', '/api/agents', 'Skill/Agent 列表'),
('配置', 'GET', '/api/configs', '平台配置项'),
('运维', 'GET', '/api/ops/services', '平台服务清单'),
('用户', 'GET', '/api/users', '用户列表（代理网关）'),
('权限', 'GET', '/api/perms/groups', '权限组列表（代理网关）');
