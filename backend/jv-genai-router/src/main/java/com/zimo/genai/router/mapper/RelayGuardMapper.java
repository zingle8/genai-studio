package com.zimo.genai.router.mapper;

import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.math.BigDecimal;
import java.util.Map;

/**
 * 转发校验链数据访问：跨库操作（同实例，库名前缀）
 * - 鉴权：genai_apikey.tb_api_key（只读）
 * - 余额：genai_billing.tb_account_balance（读 + 扣减）
 * - 日志：genai_logs.tb_usage_log（写入）
 * - 定价：genai_costs.tb_model_price（只读）；成本日聚合 genai_costs.tb_cost_daily（upsert）
 */
@Mapper
public interface RelayGuardMapper {

    /* ===== 鉴权 ===== */
    @Select("SELECT id, name, key_id AS keyId, api_key AS apiKey, owner, "
            + "DATE_FORMAT(expiry_date, '%Y-%m-%d') AS expiryDate, models, rpm, tpm, cc "
            + "FROM genai_apikey.tb_api_key WHERE api_key = #{apiKey} AND status = 1")
    Map<String, Object> selectApiKey(@Param("apiKey") String apiKey);

    /* ===== 余额 ===== */
    @Select("SELECT balance FROM genai_billing.tb_account_balance WHERE id = 1")
    BigDecimal getBalance();

    @Update("UPDATE genai_billing.tb_account_balance SET balance = balance - #{cost} WHERE id = 1")
    int deductBalance(@Param("cost") BigDecimal cost);

    /* ===== 定价（按等级；查不到单价按 0 计） ===== */
    @Select("SELECT price_in AS priceIn, price_out AS priceOut FROM genai_costs.tb_model_price "
            + "WHERE tier = #{tier} LIMIT 1")
    Map<String, Object> selectPriceByTier(@Param("tier") String tier);

    /* ===== 限流计数（MySQL 双记录 / Redis 不可用时降级数据源） ===== */

    /** 窗口计数累加（delta 可为负，用于回补） */
    @Insert("INSERT INTO genai_billing.tb_rate_limit_counter(key_id, stat_minute, requests, tokens, concurrency) "
            + "VALUES(#{keyId}, #{minute}, #{req}, #{tok}, #{cc}) "
            + "ON DUPLICATE KEY UPDATE requests = requests + #{req}, tokens = tokens + #{tok}, "
            + "concurrency = concurrency + #{cc}")
    int incrCounter(@Param("keyId") String keyId, @Param("minute") long minute,
                    @Param("req") int req, @Param("tok") long tok, @Param("cc") int cc);

    @Select("SELECT requests FROM genai_billing.tb_rate_limit_counter "
            + "WHERE key_id = #{keyId} AND stat_minute = #{minute}")
    Long selectRequests(@Param("keyId") String keyId, @Param("minute") long minute);

    @Select("SELECT tokens FROM genai_billing.tb_rate_limit_counter "
            + "WHERE key_id = #{keyId} AND stat_minute = #{minute}")
    Long selectTokens(@Param("keyId") String keyId, @Param("minute") long minute);

    /* ===== 用量日志 ===== */
    @Insert("INSERT INTO genai_logs.tb_usage_log(trace_id, api_key_id, api_key_name, model, service_id, "
            + "prompt_tokens, completion_tokens, total_tokens, cost, duration_ms, status, ip) "
            + "VALUES(#{traceId}, #{apiKeyId}, #{apiKeyName}, #{model}, #{serviceId}, "
            + "#{promptTokens}, #{completionTokens}, #{totalTokens}, #{cost}, #{durationMs}, #{status}, #{ip})")
    int insertUsageLog(@Param("traceId") String traceId, @Param("apiKeyId") String apiKeyId,
                       @Param("apiKeyName") String apiKeyName, @Param("model") String model,
                       @Param("serviceId") String serviceId, @Param("promptTokens") int promptTokens,
                       @Param("completionTokens") int completionTokens, @Param("totalTokens") int totalTokens,
                       @Param("cost") BigDecimal cost, @Param("durationMs") int durationMs,
                       @Param("status") String status, @Param("ip") String ip);

    /* ===== 成本日聚合（存在则累加，否则插入） ===== */
    @Select("SELECT id, requests, tokens, cost FROM genai_costs.tb_cost_daily "
            + "WHERE stat_date = CURDATE() AND model = #{model} AND service_id = #{serviceId} LIMIT 1")
    Map<String, Object> selectCostDaily(@Param("model") String model, @Param("serviceId") String serviceId);

    @Update("UPDATE genai_costs.tb_cost_daily SET requests = requests + #{req}, tokens = tokens + #{tokens}, "
            + "cost = cost + #{cost} WHERE id = #{id}")
    int updateCostDaily(@Param("id") long id, @Param("req") int req,
                        @Param("tokens") long tokens, @Param("cost") BigDecimal cost);

    @Insert("INSERT INTO genai_costs.tb_cost_daily(stat_date, model, service_id, requests, tokens, cost) "
            + "VALUES(CURDATE(), #{model}, #{serviceId}, #{req}, #{tokens}, #{cost})")
    int insertCostDaily(@Param("model") String model, @Param("serviceId") String serviceId,
                        @Param("req") int req, @Param("tokens") long tokens, @Param("cost") BigDecimal cost);
}
