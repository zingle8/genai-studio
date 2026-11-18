-- ============================================================
-- 16：tb_model_info 增加 tier 模型等级字段 + 17：tb_model_price 定价表
-- 等级（旗舰/标准/免费）关联计费单价，router 转发后按实际 token 用量实时扣费
-- 已按 05 号脚本建过库的环境执行本文件；新环境执行 05 + 17 即可
-- ============================================================
USE genai_models;
ALTER TABLE tb_model_info
  ADD COLUMN tier VARCHAR(16) DEFAULT '标准' COMMENT '模型等级：旗舰/标准/免费（关联 tb_model_price 计费单价）' AFTER category;
UPDATE tb_model_info SET tier = '旗舰' WHERE name IN ('GLM-4.7', 'DeepSeek-V3.2', 'DeepSeek-R1', 'GLM-4V');
UPDATE tb_model_info SET tier = '免费' WHERE name IN ('GLM-4V-Flash', 'BGE-Large');

USE genai_costs;
CREATE TABLE IF NOT EXISTS tb_model_price (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  tier VARCHAR(16) NOT NULL DEFAULT '标准' COMMENT '模型等级：旗舰/标准/免费',
  price_in DECIMAL(10,4) NOT NULL DEFAULT 0 COMMENT '输入单价（元 / 千 token）',
  price_out DECIMAL(10,4) NOT NULL DEFAULT 0 COMMENT '输出单价（元 / 千 token）',
  remark VARCHAR(255) DEFAULT '' COMMENT '说明',
  UNIQUE KEY uk_tier (tier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='模型定价（按等级）';

INSERT IGNORE INTO tb_model_price(tier, price_in, price_out, remark) VALUES
('旗舰', 0.0600, 0.0600, '旗舰档单价（元/千 token）'),
('标准', 0.0200, 0.0200, '标准档单价'),
('免费', 0.0000, 0.0000, '免费档（本地模型/体验模型不计费）');
