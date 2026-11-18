package com.zimo.genai.costs.controller;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.costs.mapper.CostMapper;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 成本核算服务：成本归集查询（数据来源：tb_usage_log 按 T+1 聚合入 tb_cost_daily）
 */
@RestController
@RequestMapping("/api/costs")
public class CostController {

    private final CostMapper mapper;

    public CostController(CostMapper mapper) {
        this.mapper = mapper;
    }

    /** 总览：今日/本月 成本、请求、Token */
    @GetMapping("/overview")
    public Result<Map<String, Object>> overview() {
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("today", mapper.today());
        data.put("month", mapper.month());
        return Result.ok(data);
    }

    /** 按日成本趋势（支持 days 或 from/to 区间） */
    @GetMapping("/daily")
    public Result<Object> daily(@RequestParam(defaultValue = "14") int days,
                                @RequestParam(required = false) String from,
                                @RequestParam(required = false) String to) {
        if (isValidRange(from, to)) return Result.ok(mapper.dailyRange(from, to));
        return Result.ok(mapper.daily(Math.min(Math.max(days, 1), 90)));
    }

    /** 按模型成本分布（支持 days 或 from/to 区间） */
    @GetMapping("/by-model")
    public Result<Object> byModel(@RequestParam(defaultValue = "30") int days,
                                  @RequestParam(required = false) String from,
                                  @RequestParam(required = false) String to) {
        if (isValidRange(from, to)) return Result.ok(mapper.byModelRange(from, to));
        return Result.ok(mapper.byModel(Math.min(Math.max(days, 1), 90)));
    }

    /** 任意区间汇总统计（成本 / 请求 / Token / 有效天数） */
    @GetMapping("/summary")
    public Result<Object> summary(@RequestParam String from, @RequestParam String to) {
        if (!isValidRange(from, to)) return Result.fail(400, "日期区间无效（from ≤ to，且不超过 366 天）");
        return Result.ok(mapper.rangeSummary(from, to));
    }

    private boolean isValidRange(String from, String to) {
        if (from == null || to == null || !from.matches("\\d{4}-\\d{2}-\\d{2}") || !to.matches("\\d{4}-\\d{2}-\\d{2}")) return false;
        if (from.compareTo(to) > 0) return false;
        try {
            java.time.LocalDate f = java.time.LocalDate.parse(from);
            java.time.LocalDate t = java.time.LocalDate.parse(to);
            return !f.isBefore(java.time.LocalDate.now().minusYears(1)) && java.time.temporal.ChronoUnit.DAYS.between(f, t) <= 366;
        } catch (Exception e) { return false; }
    }

    /** 按服务成本分布 */
    @GetMapping("/by-service")
    public Result<Object> byService(@RequestParam(defaultValue = "30") int days) {
        return Result.ok(mapper.byService(Math.min(Math.max(days, 1), 90)));
    }
}
