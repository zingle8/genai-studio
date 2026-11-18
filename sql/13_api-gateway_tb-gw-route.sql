-- GenAI Studio 全量服务接入 API 网关平台（路由 + 接口清单）
-- 路由语义：/gw/{key}/** → StripPrefix=1 → PrefixPath=/api → http://127.0.0.1:{port}
USE api_gateway;

DELETE FROM tb_gw_route WHERE path_prefix='/gw/app';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '应用宿主服务', '/gw/app', 'http://127.0.0.1:38080', '/api', 1, 1, 'jv-genai-app');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/auth';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '认证授权服务', '/gw/auth', 'http://127.0.0.1:38081', '/api', 1, 1, 'jv-genai-auth');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/dashboard';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '控制台服务', '/gw/dashboard', 'http://127.0.0.1:38082', '/api', 1, 1, 'jv-genai-dashboard');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/aigateway';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', 'AI 推理网关', '/gw/aigateway', 'http://127.0.0.1:38083', '/api', 1, 1, 'jv-genai-aigateway');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/mcp';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', 'MCP 网关', '/gw/mcp', 'http://127.0.0.1:38084', '/api', 1, 1, 'jv-genai-mcpgateway');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/agent';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', 'Agent 网关', '/gw/agent', 'http://127.0.0.1:38085', '/api', 1, 1, 'jv-genai-agentgateway');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/models';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '模型管理服务', '/gw/models', 'http://127.0.0.1:38086', '/api', 1, 1, 'jv-genai-models');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/config';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '配置中心', '/gw/config', 'http://127.0.0.1:38087', '/api', 1, 1, 'jv-genai-config');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/user';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '用户服务', '/gw/user', 'http://127.0.0.1:38088', '/api', 1, 1, 'jv-genai-user');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/prompt';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '提示词服务', '/gw/prompt', 'http://127.0.0.1:38089', '/api', 1, 1, 'jv-genai-prompt');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/chats';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '会话对话服务', '/gw/chats', 'http://127.0.0.1:38090', '/api', 1, 1, 'jv-genai-chats');
-- 定时任务调度服务（jv-genai-scheduler，2026-11-09 新增）
-- 模型路由转发服务（jv-genai-router，2026-11-10 新增，接口为 /v1/** 直路径，strip 后直转）
DELETE FROM tb_gw_route WHERE path_prefix='/gw/router';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '模型路由转发服务', '/gw/router', 'http://127.0.0.1:38100', '', 1, 1, 'jv-genai-router');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/scheduler';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '定时任务调度服务', '/gw/scheduler', 'http://127.0.0.1:38098', '/api', 1, 1, 'jv-genai-scheduler');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/apikey';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', 'API 密钥服务', '/gw/apikey', 'http://127.0.0.1:38091', '/api', 1, 1, 'jv-genai-apikey');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/billing';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '计费服务', '/gw/billing', 'http://127.0.0.1:38092', '/api', 1, 1, 'jv-genai-billing');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/costs';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '成本核算服务', '/gw/costs', 'http://127.0.0.1:38093', '/api', 1, 1, 'jv-genai-costs');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/logs';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '日志服务', '/gw/logs', 'http://127.0.0.1:38094', '/api', 1, 1, 'jv-genai-logs');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/traces';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '链路追踪服务', '/gw/traces', 'http://127.0.0.1:38095', '/api', 1, 1, 'jv-genai-traces');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/docs';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '文档服务', '/gw/docs', 'http://127.0.0.1:38096', '/api', 1, 1, 'jv-genai-docs');
DELETE FROM tb_gw_route WHERE path_prefix='/gw/market';
INSERT INTO tb_gw_route(app_id, app_name, service_name, path_prefix, upstream_url, prefix_path, strip_prefix, status, remark) VALUES('app-genai-studio', 'GenAI Studio', '市场门户服务', '/gw/market', 'http://127.0.0.1:38097', '/api', 1, 1, 'jv-genai-market');

DELETE FROM tb_gw_api WHERE app_id='app-genai-studio';
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '认证', 'POST', '/api/auth/login', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '认证', 'POST', '/api/auth/register', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '模型', 'GET', '/api/models', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '模型', 'POST', '/api/models', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '提示词', 'GET', '/api/prompts', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '提示词', 'POST', '/api/prompts', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '会话', 'GET', '/api/chats', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '会话', 'POST', '/api/chats/{id}/messages', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', 'API Key', 'GET', '/api/apikeys', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', 'API Key', 'POST', '/api/apikeys', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '计费', 'GET', '/api/billing/summary', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '成本', 'GET', '/api/costs/overview', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '日志', 'GET', '/api/logs', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', 'MCP', 'GET', '/api/mcp', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', 'Agent', 'GET', '/api/agents', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '配置', 'GET', '/api/configs', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '运维', 'GET', '/api/ops/services', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '用户', 'GET', '/api/users', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '文档', 'GET', '/api/docs', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '调度', 'GET', '/api/scheduler/jobs', '在线');
INSERT INTO tb_gw_api(app_id, service_name, method, path, status) VALUES('app-genai-studio', '调度', 'GET', '/api/scheduler/stats', '在线');

