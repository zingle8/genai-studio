-- jv-genai-apikey：API 密钥库（MySQL 5.7）
CREATE DATABASE IF NOT EXISTS genai_apikey DEFAULT CHARACTER SET utf8mb4;
USE genai_apikey;

CREATE TABLE IF NOT EXISTS tb_api_key (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(128) NOT NULL COMMENT '名称',
  key_id VARCHAR(64) NOT NULL COMMENT 'API Key ID',
  api_key VARCHAR(128) NOT NULL COMMENT '完整密钥（列表仅展示掩码）',
  owner VARCHAR(64) NOT NULL DEFAULT '' COMMENT '创建人',
  expiry_date DATE NULL COMMENT '过期时间，NULL=永久',
  models VARCHAR(512) NULL COMMENT '可用模型，逗号分隔，空=不限',
  fields VARCHAR(512) NULL COMMENT '使用领域，逗号分隔',
  org_company VARCHAR(128) DEFAULT '' COMMENT '公司',
  org_dept VARCHAR(128) DEFAULT '' COMMENT '部门',
  org_business VARCHAR(128) DEFAULT '' COMMENT '业务',
  rpm INT NULL COMMENT '限流 RPM',
  tpm INT NULL COMMENT '限流 TPM',
  cc INT NULL COMMENT '并发上限',
  remark VARCHAR(255) DEFAULT '' COMMENT '备注',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1 启用 0 停用',
  last_used_at DATETIME NULL COMMENT '上次使用时间',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_key_id (key_id),
  KEY idx_owner (owner)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API Key 密钥表';

INSERT IGNORE INTO tb_api_key(name, key_id, api_key, owner, expiry_date, models, fields, org_company, org_dept, org_business, rpm, tpm, cc, last_used_at) VALUES
('默认项目', 'kid=10048231', 'sk-604b1f2e3a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c6dAKwx', 'admin', NULL, NULL, '对话', '云创科技', '算法平台部', '智能客服', NULL, NULL, NULL, '2026-11-06 10:12:00'),
('zcode-api-key', 'kid=10051186', 'sk-7c0388a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4eii7m', 'admin', '2026-12-31', NULL, '编程', '云创科技', '研发中心', '代码助手', 3000, 1000000, 500, '2026-11-05 22:40:11'),
('prod-main-key', 'kid=10071509', 'sk-a1b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718Kwx', 'zhang.san', '2026-10-20', 'DeepSeek-V3.2,DeepSeek-R1', '业务', '数联集团', '数据智能部', '风控合规', 3000, 1000000, 500, '2026-11-07 08:30:00'),
('test-env-key', 'kid=10082774', 'sk-b2c3d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718297m2x', 'zhang.san', '2026-09-30', 'GLM-4.5-Air', '编程', '数联集团', '研发中心', '代码助手', 100, 50000, 20, '2026-09-30 18:02:33'),
('analytics-svc', 'kid=10104512', 'sk-d4e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a43Kjm', 'wang.wu', '2027-06-30', 'GLM-Embedding-3', '业务,数据分析', '智谱生态', '产品技术部', '数据分析', 500, 200000, 100, '2026-11-04 14:20:00'),
('embedding-only', 'kid=10115627', 'sk-e5f60718293a4b5c6d7e8f90a1b2c3d4e5f60718293a4b5c5Nlp', 'zhao.liu', '2027-01-31', 'GLM-Embedding-3,BGE-Large', '知识库,向量化', '智谱生态', '基础架构部', '知识问答', 1000, 400000, 50, '2026-11-07 09:15:42');
