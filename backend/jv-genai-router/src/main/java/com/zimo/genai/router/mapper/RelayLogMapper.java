package com.zimo.genai.router.mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;

/**
 * 转发请求/回复内容日志（genai_logs.tb_relay_log，按日分区）。
 * 与 RelayGuardService 写入的 tb_usage_log（计费统计）互补：本表存请求/响应原文。
 */
@Mapper
public interface RelayLogMapper {

    @Insert("INSERT INTO genai_logs.tb_relay_log(trace_id, model, method, path, question, status_code, is_stream, "
            + "request_body, response_body, error_msg) "
            + "VALUES(#{traceId}, #{model}, #{method}, #{path}, #{question}, #{statusCode}, #{isStream}, "
            + "#{requestBody}, #{responseBody}, #{errorMsg})")
    int insertRelayLog(@org.apache.ibatis.annotations.Param("traceId") String traceId,
                       @org.apache.ibatis.annotations.Param("model") String model,
                       @org.apache.ibatis.annotations.Param("method") String method,
                       @org.apache.ibatis.annotations.Param("path") String path,
                       @org.apache.ibatis.annotations.Param("question") String question,
                       @org.apache.ibatis.annotations.Param("statusCode") int statusCode,
                       @org.apache.ibatis.annotations.Param("isStream") boolean isStream,
                       @org.apache.ibatis.annotations.Param("requestBody") String requestBody,
                       @org.apache.ibatis.annotations.Param("responseBody") String responseBody,
                       @org.apache.ibatis.annotations.Param("errorMsg") String errorMsg);
}
