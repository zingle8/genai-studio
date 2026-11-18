-- ============================================================
-- 18：体验中心消息表按日分区重构
-- 区分维度：
--   会话(tb_chat_session.id) > 轮次(trace_id，一次提问 = 1 条 user + N 条 assistant 同 trace)
--   > 单条消息(id 自增，assistant 带 model 字段区分多模型并发回复)
-- 历史 GET /{id}/messages 按 session_id 全量还原，前端按 created_at/id 排序展示。
-- 分区：RANGE 按天（TO_DAYS(created_at)），已有分区 + 每天 REORGANIZE 滚动新分区。
-- ============================================================
USE genai_chats;

DROP TABLE IF EXISTS tb_chat_message_new;
CREATE TABLE tb_chat_message_new (
  id BIGINT AUTO_INCREMENT,
  session_id BIGINT NOT NULL COMMENT '会话 ID（多会话区分）',
  role VARCHAR(16) NOT NULL COMMENT 'user / assistant',
  content MEDIUMTEXT COMMENT '消息内容',
  model VARCHAR(64) DEFAULT '' COMMENT '产生该回复的模型（user 消息为空）',
  trace_id VARCHAR(64) DEFAULT '' COMMENT '轮次关联 ID（一次提问 + N 个模型回复同 trace）',
  prompt_tokens INT DEFAULT 0,
  completion_tokens INT DEFAULT 0,
  cost DECIMAL(12,4) DEFAULT 0 COMMENT '消费（元）',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id, created_at),
  KEY idx_session (session_id, created_at),
  KEY idx_trace (trace_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息（按日 RANGE 分区）'
PARTITION BY RANGE (TO_DAYS(created_at)) (
  PARTITION p20261113 VALUES LESS THAN (TO_DAYS('2026-11-14')),
  PARTITION p_max VALUES LESS THAN MAXVALUE
);

-- 迁移旧消息（旧表存在且非空时）
INSERT INTO tb_chat_message_new(session_id, role, content, created_at)
  SELECT session_id, role, content, created_at FROM tb_chat_message;
DROP TABLE IF EXISTS tb_chat_message;
RENAME TABLE tb_chat_message_new TO tb_chat_message;

-- 每日滚动分区（需 SET GLOBAL event_scheduler = ON）
DROP PROCEDURE IF EXISTS sp_add_chat_msg_partition;
DELIMITER //
CREATE PROCEDURE sp_add_chat_msg_partition()
BEGIN
  DECLARE p_day DATE;
  DECLARE p_name VARCHAR(32);
  SET p_day = DATE_ADD(CURDATE(), INTERVAL 2 DAY);
  SET p_name = CONCAT('p', DATE_FORMAT(p_day, '%Y%m%d'));
  IF NOT EXISTS (SELECT 1 FROM information_schema.partitions
                 WHERE table_schema = 'genai_chats' AND table_name = 'tb_chat_message'
                   AND partition_name = p_name) THEN
    SET @sql = CONCAT(
      'ALTER TABLE genai_chats.tb_chat_message REORGANIZE PARTITION p_max INTO (',
      'PARTITION ', p_name, ' VALUES LESS THAN (TO_DAYS(''', p_day, ''')), ',
      'PARTITION p_max VALUES LESS THAN MAXVALUE)');
    PREPARE st FROM @sql; EXECUTE st; DEALLOCATE PREPARE st;
  END IF;
END //
DELIMITER ;

DROP EVENT IF EXISTS ev_chat_msg_daily_partition;
CREATE EVENT ev_chat_msg_daily_partition
ON SCHEDULE EVERY 1 DAY STARTS '2026-11-14 00:05:00'
DO CALL sp_add_chat_msg_partition();
