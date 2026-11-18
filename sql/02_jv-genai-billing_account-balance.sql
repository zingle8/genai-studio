-- jv-genai-billing：余额与账单（MySQL 5.7）
CREATE DATABASE IF NOT EXISTS genai_billing DEFAULT CHARACTER SET utf8mb4;
USE genai_billing;

CREATE TABLE IF NOT EXISTS tb_account_balance (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  balance DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '账户余额',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账户余额';

CREATE TABLE IF NOT EXISTS tb_billing_order (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  order_no VARCHAR(32) NOT NULL COMMENT '订单号',
  type VARCHAR(16) NOT NULL COMMENT 'topup 充值 / consume 消费',
  amount DECIMAL(12,2) NOT NULL COMMENT '金额',
  balance_after DECIMAL(12,2) NULL COMMENT '交易后余额',
  channel VARCHAR(32) DEFAULT '' COMMENT '渠道',
  status VARCHAR(16) NOT NULL DEFAULT 'success',
  remark VARCHAR(255) DEFAULT '',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_type (type),
  KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='账单/订单';

INSERT IGNORE INTO tb_account_balance(id, balance) VALUES (1, 9.99);

INSERT IGNORE INTO tb_billing_order(order_no, type, amount, balance_after, channel, status, remark, created_at) VALUES
('R20261001093000111', 'topup', 500.00, 500.00, 'balance', 'success', '账户充值', '2026-10-01 09:30:00'),
('C20261005182200222', 'consume', 128.40, 371.60, 'api', 'success', '10月模型调用消费', '2026-10-31 18:22:00'),
('R20261102093000333', 'topup', 200.00, 571.60, 'balance', 'success', '账户充值', '2026-11-02 09:30:00'),
('C20261101235900444', 'consume', 236.75, 334.85, 'api', 'success', '11月上旬模型调用', '2026-11-05 23:59:00'),
('C20261106012200555', 'consume', 18.86, 315.99, 'api', 'success', '对话调用', '2026-11-06 01:22:00'),
('C20261107083000666', 'consume', 306.00, 9.99, 'api', 'success', '批量任务调用', '2026-11-07 08:30:00');
