-- Wave1 新模块建库（MySQL 5.7）：Skill/Agent 注册
CREATE DATABASE IF NOT EXISTS genai_agentgateway DEFAULT CHARACTER SET utf8mb4;
USE genai_agentgateway;
CREATE TABLE IF NOT EXISTS tb_agent_info (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  type VARCHAR(16) DEFAULT 'Agent' COMMENT 'Skill / Agent',
  model VARCHAR(64) DEFAULT '',
  tools VARCHAR(512) DEFAULT '' COMMENT '工具，逗号分隔',
  description VARCHAR(512) DEFAULT '',
  enabled TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Skill/Agent 注册';
INSERT IGNORE INTO tb_agent_info(name, type, model, tools, description, enabled) VALUES
('智能客服 Agent', 'Agent', 'GLM-4.7', '知识库检索,工单创建', '售前售后咨询应答', 1),
('代码助手 Skill', 'Skill', 'DeepSeek-V3.2', '', '代码生成与解释', 1),
('数据分析 Agent', 'Agent', 'DeepSeek-R1', 'SQL查询,图表生成', '自然语言转数据分析', 1),
('日报生成 Skill', 'Skill', 'GLM-4.6', '', '按模板生成工作日报', 0);
