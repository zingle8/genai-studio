-- ============================================================
-- 22：体验中心消息支持「思考过程」独立字段（reasoning_content）
--     OpenAI 兼容：推理模型（如 mlx-glm-4.7-flash）的 message.reasoning_content
--     前端体验中心据此折叠展示思考文本，与最终答案 content 分离
--     幂等：通过 information_schema 判断列不存在才 ADD
-- ============================================================
SET @col_exists = (
  SELECT COUNT(*) FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = 'genai_chats' AND TABLE_NAME = 'tb_chat_message'
    AND COLUMN_NAME = 'reasoning_content'
);
SET @sql = IF(@col_exists = 0,
  'ALTER TABLE genai_chats.tb_chat_message ADD COLUMN reasoning_content MEDIUMTEXT NULL COMMENT ''推理模型思考过程（reasoning_content）'' AFTER content',
  'SELECT 1');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
