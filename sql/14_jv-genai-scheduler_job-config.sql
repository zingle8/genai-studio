-- 定时任务调度服务（jv-genai-scheduler）初始化脚本
-- 库：genai_scheduler
-- 表：tb_job_config（任务配置）/ tb_stat_period（区间统计结果）/ tb_job_run_log（执行记录）
-- 执行：幂等（IF NOT EXISTS + INSERT IGNORE）

CREATE DATABASE IF NOT EXISTS genai_scheduler DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE genai_scheduler;

-- 1. 定时任务配置
CREATE TABLE IF NOT EXISTS tb_job_config (
  id           BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  job_key      VARCHAR(64)  NOT NULL COMMENT '任务标识',
  job_name     VARCHAR(128) NOT NULL COMMENT '任务名称',
  cron_expr    VARCHAR(64)  NOT NULL COMMENT 'cron 表达式（Spring 6 位）',
  stat_type    VARCHAR(16)  NOT NULL DEFAULT 'MIXED' COMMENT '统计类型：ORDER/COST/MIXED',
  period_type  VARCHAR(16)  NOT NULL DEFAULT 'DAILY' COMMENT '统计周期：DAILY/WEEKLY/MONTHLY',
  days_back    INT          NOT NULL DEFAULT 1 COMMENT '回溯天数（窗口=今天-daysBack ~ 昨天）',
  description  VARCHAR(255) DEFAULT NULL COMMENT '说明',
  enabled      TINYINT      NOT NULL DEFAULT 1 COMMENT '是否启用',
  last_run_at  DATETIME     DEFAULT NULL COMMENT '最近执行时间',
  last_status  VARCHAR(16)  DEFAULT NULL COMMENT '最近执行状态：SUCCESS/FAILED',
  last_message VARCHAR(512) DEFAULT NULL COMMENT '最近执行结果摘要',
  created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_job_key (job_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='定时任务配置';

-- 2. 区间统计结果（订单 + 成本 + 用量）
CREATE TABLE IF NOT EXISTS tb_stat_period (
  id            BIGINT        NOT NULL AUTO_INCREMENT COMMENT '主键',
  stat_type     VARCHAR(16)   NOT NULL COMMENT '统计类型：ORDER/COST/MIXED',
  period_type   VARCHAR(16)   NOT NULL COMMENT '周期：DAILY/WEEKLY/MONTHLY',
  period_start  DATE          NOT NULL COMMENT '区间开始',
  period_end    DATE          NOT NULL COMMENT '区间结束',
  order_count   BIGINT        NOT NULL DEFAULT 0 COMMENT '订单数',
  order_amount  DECIMAL(14,2) NOT NULL DEFAULT 0 COMMENT '订单金额（元）',
  cost_amount   DECIMAL(14,4) NOT NULL DEFAULT 0 COMMENT '成本金额（元）',
  request_count BIGINT        NOT NULL DEFAULT 0 COMMENT '请求次数',
  token_count   BIGINT        NOT NULL DEFAULT 0 COMMENT 'Token 数',
  extra_json    VARCHAR(1024) DEFAULT NULL COMMENT '扩展明细（JSON）',
  created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_period (stat_type, period_type, period_start),
  KEY idx_period_end (period_end)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='区间统计结果';

-- 3. 执行记录
CREATE TABLE IF NOT EXISTS tb_job_run_log (
  id            BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  job_key       VARCHAR(64)  NOT NULL COMMENT '任务标识',
  trigger_type  VARCHAR(16)  NOT NULL DEFAULT 'CRON' COMMENT '触发方式：CRON/MANUAL',
  start_at      DATETIME     NOT NULL COMMENT '开始时间',
  end_at        DATETIME     DEFAULT NULL COMMENT '结束时间',
  status        VARCHAR(16)  NOT NULL COMMENT '执行状态：SUCCESS/FAILED',
  rows_affected INT          NOT NULL DEFAULT 0 COMMENT '影响行数',
  message       VARCHAR(512) DEFAULT NULL COMMENT '结果摘要/错误信息',
  created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_job_key (job_key),
  KEY idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务执行记录';

-- 4. 预置统计任务
INSERT IGNORE INTO tb_job_config(job_key, job_name, cron_expr, stat_type, period_type, days_back, description, enabled) VALUES
('order_daily_stat', '订单日统计', '0 5 1 * * ?', 'ORDER', 'DAILY', 1,
 '每日 01:05 统计前一日成功订单笔数与金额（来源 genai_billing.tb_billing_order）', 1),
('cost_daily_stat', '成本日统计', '0 10 1 * * ?', 'COST', 'DAILY', 1,
 '每日 01:10 统计前一日成本/请求/Token（来源 genai_costs.tb_cost_daily，缺失时用 genai_logs.tb_usage_log 兜底）', 1),
('order_cost_weekly', '订单成本周统计', '0 20 1 * * MON', 'MIXED', 'WEEKLY', 7,
 '每周一 01:20 统计近 7 天订单与成本汇总', 1),
('order_cost_monthly', '订单成本月统计', '0 30 1 1 * ?', 'MIXED', 'MONTHLY', 30,
 '每月 1 日 01:30 统计近 30 天订单与成本汇总', 1);
