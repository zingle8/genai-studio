package com.zimo.genai.scheduler.mapper;

import com.zimo.genai.scheduler.model.JobConfig;
import org.apache.ibatis.annotations.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * 调度服务 Mapper
 *
 * 说明：统计目标表在其它服务库（genai_billing / genai_costs / genai_logs），
 * 同实例下用「库名.表名」跨库查询；本服务自身数据落 genai_scheduler 库。
 */
@Mapper
public interface SchedulerMapper {

    /* ============ 任务配置 ============ */

    @Select("SELECT * FROM tb_job_config ORDER BY id")
    List<JobConfig> listJobs();

    @Select("SELECT * FROM tb_job_config WHERE job_key = #{jobKey}")
    JobConfig findByKey(@Param("jobKey") String jobKey);

    @Select("SELECT * FROM tb_job_config WHERE enabled = 1 ORDER BY id")
    List<JobConfig> listEnabledJobs();

    @Update("UPDATE tb_job_config SET enabled = #{enabled}, updated_at = NOW() WHERE job_key = #{jobKey}")
    int updateEnabled(@Param("jobKey") String jobKey, @Param("enabled") int enabled);

    @Update("UPDATE tb_job_config SET last_run_at = NOW(), last_status = #{status}, last_message = #{message} "
            + "WHERE job_key = #{jobKey}")
    int updateRunResult(@Param("jobKey") String jobKey, @Param("status") String status,
                        @Param("message") String message);

    /* ============ 统计聚合（跨库） ============ */

    /** 订单区间聚合（成功订单） */
    @Select("SELECT COUNT(*) AS orderCount, COALESCE(SUM(amount),0) AS orderAmount "
            + "FROM genai_billing.tb_billing_order "
            + "WHERE status = 'success' AND DATE(created_at) BETWEEN #{start} AND #{end}")
    Map<String, Object> aggregateOrders(@Param("start") LocalDate start, @Param("end") LocalDate end);

    /** 成本区间聚合（tb_cost_daily 已按 T+1 聚合） */
    @Select("SELECT COALESCE(SUM(cost),0) AS costAmount, COALESCE(SUM(requests),0) AS requestCount, "
            + "COALESCE(SUM(tokens),0) AS tokenCount FROM genai_costs.tb_cost_daily "
            + "WHERE stat_date BETWEEN #{start} AND #{end}")
    Map<String, Object> aggregateCosts(@Param("start") LocalDate start, @Param("end") LocalDate end);

    /** 用量区间聚合（tb_usage_log 实时明细，用于成本表未覆盖的当日数据） */
    @Select("SELECT COUNT(*) AS requestCount, COALESCE(SUM(total_tokens),0) AS tokenCount, "
            + "COALESCE(SUM(cost),0) AS costAmount FROM genai_logs.tb_usage_log "
            + "WHERE status = 'success' AND DATE(created_at) BETWEEN #{start} AND #{end}")
    Map<String, Object> aggregateUsage(@Param("start") LocalDate start, @Param("end") LocalDate end);

    /* ============ 统计结果 ============ */

    @Insert("INSERT INTO tb_stat_period(stat_type, period_type, period_start, period_end, "
            + "order_count, order_amount, cost_amount, request_count, token_count, extra_json) "
            + "VALUES(#{statType}, #{periodType}, #{start}, #{end}, #{orderCount}, #{orderAmount}, "
            + "#{costAmount}, #{requestCount}, #{tokenCount}, #{extraJson}) "
            + "ON DUPLICATE KEY UPDATE order_count = VALUES(order_count), order_amount = VALUES(order_amount), "
            + "cost_amount = VALUES(cost_amount), request_count = VALUES(request_count), "
            + "token_count = VALUES(token_count), extra_json = VALUES(extra_json), updated_at = NOW()")
    int upsertStat(@Param("statType") String statType, @Param("periodType") String periodType,
                   @Param("start") LocalDate start, @Param("end") LocalDate end,
                   @Param("orderCount") long orderCount, @Param("orderAmount") Object orderAmount,
                   @Param("costAmount") Object costAmount, @Param("requestCount") long requestCount,
                   @Param("tokenCount") long tokenCount, @Param("extraJson") String extraJson);

    @Select("<script>SELECT * FROM tb_stat_period WHERE 1=1 "
            + "<if test='statType != null and statType != \"\"'> AND stat_type = #{statType}</if> "
            + "<if test='periodType != null and periodType != \"\"'> AND period_type = #{periodType}</if> "
            + "<if test='from != null'> AND period_end &gt;= #{from}</if> "
            + "<if test='to != null'> AND period_start &lt;= #{to}</if> "
            + "ORDER BY period_start DESC LIMIT #{limit}</script>")
    List<Map<String, Object>> listStats(@Param("statType") String statType,
                                        @Param("periodType") String periodType,
                                        @Param("from") LocalDate from,
                                        @Param("to") LocalDate to,
                                        @Param("limit") int limit);

    /* ============ 执行记录 ============ */

    @Insert("INSERT INTO tb_job_run_log(job_key, trigger_type, start_at, end_at, status, rows_affected, message) "
            + "VALUES(#{jobKey}, #{triggerType}, #{startAt}, NOW(), #{status}, #{rowsAffected}, #{message})")
    int insertRunLog(@Param("jobKey") String jobKey, @Param("triggerType") String triggerType,
                     @Param("startAt") java.time.LocalDateTime startAt, @Param("status") String status,
                     @Param("rowsAffected") int rowsAffected, @Param("message") String message);

    @Select("SELECT * FROM tb_job_run_log ORDER BY id DESC LIMIT #{limit}")
    List<Map<String, Object>> listRuns(@Param("limit") int limit);
}
