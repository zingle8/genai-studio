CREATE DATABASE IF NOT EXISTS genai_prompt DEFAULT CHARACTER SET utf8mb4;
USE genai_prompt;
CREATE TABLE IF NOT EXISTS tb_prompt_template (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL COMMENT '模板名',
  content TEXT NOT NULL COMMENT '模板内容',
  variables VARCHAR(512) DEFAULT '' COMMENT '变量，逗号分隔',
  tags VARCHAR(256) DEFAULT '' COMMENT '标签',
  status TINYINT NOT NULL DEFAULT 1,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='提示词模板';
INSERT IGNORE INTO tb_prompt_template(name, content, variables, tags, status) VALUES
('通用助手', '你是一个乐于助人的 AI 助手，请用简洁清晰的中文回答用户问题。', '', '通用,默认', 1),
('代码评审', '请评审以下代码，从正确性、可读性、性能三方面给出建议：\n{{code}}', 'code', '编程,评审', 1),
('知识库问答', '基于以下参考资料回答用户问题，若资料中没有答案请如实说明：\n参考资料：{{context}}\n问题：{{question}}', 'context,question', 'RAG,问答', 1),
('文案润色', '请润色以下文案，使其更加专业流畅：\n{{text}}', 'text', '文案', 1);
