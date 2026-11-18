package com.zimo.genai.chats.mapper;

import com.zimo.genai.chats.entity.ChatMessage;
import com.zimo.genai.chats.entity.ChatSession;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ChatMapper {

    @Select("SELECT * FROM tb_chat_session ORDER BY id DESC LIMIT #{offset}, #{size}")
    List<ChatSession> listSessions(@Param("offset") long offset, @Param("size") int size);

    @Select("SELECT COUNT(*) FROM tb_chat_session")
    long countSessions();

    @Insert("INSERT INTO tb_chat_session(title, owner) VALUES(#{title}, #{owner})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertSession(ChatSession s);

    @Update("UPDATE tb_chat_session SET title=#{title} WHERE id=#{id}")
    int renameSession(ChatSession s);

    @Delete("DELETE FROM tb_chat_session WHERE id=#{id}")
    int deleteSession(@Param("id") Long id);

    @Select("SELECT id, session_id AS sessionId, role, content, model, trace_id AS traceId, "
            + "prompt_tokens AS promptTokens, completion_tokens AS completionTokens, duration_ms AS durationMs, cost, created_at AS createdAt "
            + "FROM tb_chat_message WHERE session_id=#{sessionId} ORDER BY id ASC")
    List<ChatMessage> listMessages(@Param("sessionId") Long sessionId);

    @Select("SELECT id, session_id AS sessionId, role, content, model, trace_id AS traceId, "
            + "prompt_tokens AS promptTokens, completion_tokens AS completionTokens, duration_ms AS durationMs, cost, created_at AS createdAt "
            + "FROM tb_chat_message WHERE session_id=#{sessionId} AND trace_id=#{traceId} ORDER BY id ASC")
    List<ChatMessage> listMessagesByTrace(@Param("sessionId") Long sessionId, @Param("traceId") String traceId);

    @Insert("INSERT INTO tb_chat_message(session_id, role, content, model, trace_id, prompt_tokens, completion_tokens, duration_ms, cost) "
            + "VALUES(#{sessionId}, #{role}, #{content}, #{model}, #{traceId}, #{promptTokens}, #{completionTokens}, #{durationMs}, #{cost})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertMessage(ChatMessage m);
}
