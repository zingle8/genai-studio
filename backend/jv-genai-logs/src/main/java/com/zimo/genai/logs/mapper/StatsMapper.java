package com.zimo.genai.logs.mapper;

import com.zimo.genai.logs.entity.RelayLogEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Map;

@Mapper
public interface StatsMapper {

    @Select("SELECT COUNT(*) AS requests,"
            + " IFNULL(SUM(status = 'success') / COUNT(*) * 100, 0) AS successRate,"
            + " IFNULL(SUM(total_tokens), 0) AS tokens,"
            + " IFNULL(SUM(cost), 0) AS cost"
            + " FROM tb_usage_log WHERE created_at >= CURDATE()")
    Map<String, Object> todaySummary();

    @Select("SELECT api_key_id AS id, IFNULL(api_key_name, api_key_id) AS name, COUNT(*) AS count"
            + " FROM tb_usage_log GROUP BY api_key_id, api_key_name ORDER BY count DESC LIMIT 50")
    List<Map<String, Object>> groupApiKeys();

    @Select("SELECT id, trace_id AS traceId, model, method, path, question, status_code AS statusCode,"
            + " is_stream AS isStream, request_body AS requestBody, response_body AS responseBody, error_msg AS errorMsg,"
            + " created_at AS createdAt FROM tb_relay_log WHERE trace_id = #{traceId}"
            + " ORDER BY id DESC LIMIT 1")
    RelayLogEntity relayByTrace(@Param("traceId") String traceId);
}
