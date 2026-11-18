package com.zimo.genai.logs.mapper;

import com.zimo.genai.logs.entity.UsageLogEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface LogsMapper {

    String WHERE = "<if test='startDate != null and startDate != \"\"'> AND created_at &gt;= #{startDate}</if>"
            + "<if test='endDate != null and endDate != \"\"'> AND created_at &lt; DATE_ADD(#{endDate}, INTERVAL 1 DAY)</if>"
            + "<if test='model != null and model != \"\"'> AND model = #{model}</if>"
            + "<if test='status != null and status != \"\"'> AND status = #{status}</if>"
            + "<if test='apiKeyId != null and apiKeyId != \"\"'> AND api_key_id = #{apiKeyId}</if>"
            + "<if test='keyword != null and keyword != \"\"'> AND (trace_id LIKE CONCAT('%',#{keyword},'%') OR api_key_id LIKE CONCAT('%',#{keyword},'%') OR ip LIKE CONCAT('%',#{keyword},'%'))</if>";

    @Select("<script>SELECT id, trace_id AS traceId, api_key_id AS apiKeyId, api_key_name AS apiKeyName,"
            + " model, service_id AS serviceId, prompt_tokens AS promptTokens, completion_tokens AS completionTokens,"
            + " total_tokens AS totalTokens, cost, duration_ms AS durationMs, status, ip, created_at AS createdAt"
            + " FROM tb_usage_log WHERE 1=1" + WHERE
            + " ORDER BY id DESC LIMIT #{offset}, #{size}</script>")
    List<UsageLogEntity> list(@Param("startDate") String startDate, @Param("endDate") String endDate,
                              @Param("model") String model, @Param("status") String status,
                              @Param("apiKeyId") String apiKeyId, @Param("keyword") String keyword,
                              @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_usage_log WHERE 1=1" + WHERE + "</script>")
    long count(@Param("startDate") String startDate, @Param("endDate") String endDate,
               @Param("model") String model, @Param("status") String status,
               @Param("apiKeyId") String apiKeyId, @Param("keyword") String keyword);
}
