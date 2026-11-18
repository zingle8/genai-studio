package com.zimo.genai.scheduler.service;

import com.zimo.genai.scheduler.mapper.SchedulerMapper;
import com.zimo.genai.scheduler.model.JobConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 统计任务执行器：按任务配置的周期取窗口，聚合订单 + 成本/用量，写入 tb_stat_period。
 */
@Service
public class StatJobService {

    private static final Logger log = LoggerFactory.getLogger(StatJobService.class);

    private final SchedulerMapper mapper;

    public StatJobService(SchedulerMapper mapper) {
        this.mapper = mapper;
    }

    /**
     * 执行一个统计任务。
     *
     * @param job         任务配置
     * @param triggerType CRON 定时触发 / MANUAL 手动触发
     * @return 执行结果摘要
     */
    public Map<String, Object> run(JobConfig job, String triggerType) {
        LocalDateTime startAt = LocalDateTime.now();
        // 统计窗口：默认 [今天-daysBack, 昨天]，避免统计到不完整的当天数据
        int daysBack = job.getDaysBack() == null || job.getDaysBack() < 1 ? 1 : job.getDaysBack();
        LocalDate end = LocalDate.now().minusDays(1);
        LocalDate start = end.minusDays(daysBack - 1L);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("jobKey", job.getJobKey());
        result.put("periodStart", start.toString());
        result.put("periodEnd", end.toString());

        try {
            Map<String, Object> orders = mapper.aggregateOrders(start, end);
            Map<String, Object> costs = mapper.aggregateCosts(start, end);

            long orderCount = toLong(orders.get("orderCount"));
            BigDecimal orderAmount = toDecimal(orders.get("orderAmount"));
            BigDecimal costAmount = toDecimal(costs.get("costAmount"));
            long requestCount = toLong(costs.get("requestCount"));
            long tokenCount = toLong(costs.get("tokenCount"));

            // 成本表 T+1 聚合，若窗口含当天或成本缺失，用 tb_usage_log 明细兜底
            if (costAmount.signum() == 0) {
                Map<String, Object> usage = mapper.aggregateUsage(start, end);
                costAmount = toDecimal(usage.get("costAmount"));
                requestCount = toLong(usage.get("requestCount"));
                tokenCount = toLong(usage.get("tokenCount"));
            }

            String extra = "{\"orderAmount\":" + orderAmount + ",\"costAmount\":" + costAmount
                    + ",\"requestCount\":" + requestCount + ",\"tokenCount\":" + tokenCount + "}";

            int rows = mapper.upsertStat(job.getStatType(), job.getPeriodType(), start, end,
                    orderCount, orderAmount, costAmount, requestCount, tokenCount, extra);

            String message = "统计完成：订单 " + orderCount + " 笔 / " + orderAmount
                    + " 元，成本 " + costAmount + " 元，请求 " + requestCount + " 次，Token " + tokenCount;

            mapper.insertRunLog(job.getJobKey(), triggerType, startAt, "SUCCESS", rows, message);
            mapper.updateRunResult(job.getJobKey(), "SUCCESS", message);
            log.info("[{}] {}", job.getJobKey(), message);

            result.put("status", "SUCCESS");
            result.put("message", message);
            result.put("orderCount", orderCount);
            result.put("orderAmount", orderAmount);
            result.put("costAmount", costAmount);
            result.put("requestCount", requestCount);
            result.put("tokenCount", tokenCount);
            return result;
        } catch (Exception e) {
            String message = "统计失败：" + e.getMessage();
            mapper.insertRunLog(job.getJobKey(), triggerType, startAt, "FAILED", 0, message);
            mapper.updateRunResult(job.getJobKey(), "FAILED", message);
            log.error("[{}] {}", job.getJobKey(), message, e);

            result.put("status", "FAILED");
            result.put("message", message);
            return result;
        }
    }

    /** 指定区间统计（手动补数 / 临时区间汇总） */
    public Map<String, Object> runRange(LocalDate start, LocalDate end, String statType, String periodType) {
        LocalDateTime startAt = LocalDateTime.now();
        String jobKey = "range_" + start + "_" + end;

        Map<String, Object> orders = mapper.aggregateOrders(start, end);
        Map<String, Object> costs = mapper.aggregateCosts(start, end);

        long orderCount = toLong(orders.get("orderCount"));
        BigDecimal orderAmount = toDecimal(orders.get("orderAmount"));
        BigDecimal costAmount = toDecimal(costs.get("costAmount"));
        long requestCount = toLong(costs.get("requestCount"));
        long tokenCount = toLong(costs.get("tokenCount"));

        if (costAmount.signum() == 0) {
            Map<String, Object> usage = mapper.aggregateUsage(start, end);
            costAmount = toDecimal(usage.get("costAmount"));
            requestCount = toLong(usage.get("requestCount"));
            tokenCount = toLong(usage.get("tokenCount"));
        }

        String extra = "{\"orderAmount\":" + orderAmount + ",\"costAmount\":" + costAmount
                + ",\"requestCount\":" + requestCount + ",\"tokenCount\":" + tokenCount + "}";
        int rows = mapper.upsertStat(statType, periodType, start, end,
                orderCount, orderAmount, costAmount, requestCount, tokenCount, extra);

        String message = "区间统计完成 " + start + " ~ " + end + "：订单 " + orderCount + " 笔 / "
                + orderAmount + " 元，成本 " + costAmount + " 元，请求 " + requestCount + " 次，Token " + tokenCount;
        mapper.insertRunLog(jobKey, "MANUAL", startAt, "SUCCESS", rows, message);
        log.info("[{}] {}", jobKey, message);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("statType", statType);
        result.put("periodType", periodType);
        result.put("periodStart", start.toString());
        result.put("periodEnd", end.toString());
        result.put("orderCount", orderCount);
        result.put("orderAmount", orderAmount);
        result.put("costAmount", costAmount);
        result.put("requestCount", requestCount);
        result.put("tokenCount", tokenCount);
        return result;
    }

    /** 批量执行所有启用的统计任务（可被外部区间统计复用） */
    public List<Map<String, Object>> runAllEnabled() {
        return mapper.listEnabledJobs().stream().map(j -> run(j, "CRON")).toList();
    }

    private long toLong(Object v) {
        return v == null ? 0L : ((Number) v).longValue();
    }

    private BigDecimal toDecimal(Object v) {
        return v == null ? BigDecimal.ZERO : new BigDecimal(v.toString());
    }
}
