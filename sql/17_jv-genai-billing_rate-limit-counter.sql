-- ============================================================
-- 17：路由限流计数表（Redis 双记录的 MySQL 持久化层）
-- 策略：RPM/TPM/CC 计数双写（Redis 优先读写；Redis 每次计数同步落 MySQL），
--       Redis 不可用时自动降级读 MySQL 计数；本地重启/Redis 清空不丢窗口数据。
-- ============================================================
USE genai_billing;
CREATE TABLE IF NOT EXISTS tb_rate_limit_counter (
  key_id VARCHAR(64) NOT NULL COMMENT 'API Key ID',
  stat_minute BIGINT NOT NULL COMMENT '统计窗口（epoch 分钟）',
  requests INT NOT NULL DEFAULT 0 COMMENT '窗口内请求数（RPM）',
  tokens BIGINT NOT NULL DEFAULT 0 COMMENT '窗口内 token 数（TPM）',
  concurrency INT NOT NULL DEFAULT 0 COMMENT '并发占位数（CC，双记录）',
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (key_id, stat_minute)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路由限流计数（Redis 双记录 / 降级数据源）';
