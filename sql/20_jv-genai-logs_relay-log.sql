-- ============================================================
-- 20：router 请求/回复内容日志（与 tb_usage_log 计费统计互补）
--     记录每次转发的请求体与响应体内容（截断 64KB），按日 RANGE 分区
-- ============================================================
USE genai_logs;
CREATE TABLE IF NOT EXISTS tb_relay_log (
  id BIGINT AUTO_INCREMENT,
  trace_id VARCHAR(64) DEFAULT '' COMMENT '调用链 ID（与 usage_log 同源）',
  model VARCHAR(64) DEFAULT '' COMMENT '平台模型名',
  method VARCHAR(8) DEFAULT 'POST',
  path VARCHAR(255) DEFAULT '' COMMENT '请求路径',
  question VARCHAR(1024) DEFAULT '' COMMENT '用户当前问题(messages最后一条user)',
  status_code INT DEFAULT 0 COMMENT '上游响应码',
  is_stream TINYINT(1) DEFAULT 0 COMMENT '是否流式响应',
  request_body MEDIUMTEXT COMMENT '请求体（model 替换后，截断 64KB）',
  response_body MEDIUMTEXT COMMENT '响应体（流式为收集片段，截断 64KB）',
  error_msg VARCHAR(512) DEFAULT '' COMMENT '失败原因',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id, created_at),
  KEY idx_trace (trace_id),
  KEY idx_model (model, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='转发请求/回复内容日志（按日分区）'
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p20261113 VALUES LESS THAN (TO_DAYS('2026-11-14')),
  PARTITION p_max VALUES LESS THAN MAXVALUE
);

-- 每日滚动分区（需 SET GLOBAL event_scheduler = ON；与 18 号 chat_message 同款机制）
DROP PROCEDURE IF EXISTS sp_add_relay_log_partition;
DELIMITER //
CREATE PROCEDURE sp_add_relay_log_partition()
BEGIN
  DECLARE p_day DATE;
  DECLARE p_name VARCHAR(32);
  SET p_day = DATE_ADD(CURDATE(), INTERVAL 2 DAY);
  SET p_name = CONCAT('p', DATE_FORMAT(p_day, '%Y%m%d'));
  IF NOT EXISTS (SELECT 1 FROM information_schema.partitions
                 WHERE table_schema = 'genai_logs' AND table_name = 'tb_relay_log'
                   AND partition_name = p_name) THEN
    SET @sql = CONCAT(
      'ALTER TABLE genai_logs.tb_relay_log REORGANIZE PARTITION p_max INTO (',
      'PARTITION ', p_name, ' VALUES LESS THAN (TO_DAYS(''', p_day, ''')), ',
      'PARTITION p_max VALUES LESS THAN MAXVALUE)');
    PREPARE st FROM @sql; EXECUTE st; DEALLOCATE PREPARE st;
  END IF;
END //
DELIMITER ;

DROP EVENT IF EXISTS ev_relay_log_daily_partition;
CREATE EVENT ev_relay_log_daily_partition
ON SCHEDULE EVERY 1 DAY STARTS '2026-11-16 00:05:00'
DO CALL sp_add_relay_log_partition();
