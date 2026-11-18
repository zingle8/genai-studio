package com.zimo.genai.logs.controller;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.logs.entity.RelayLogEntity;
import com.zimo.genai.logs.entity.UsageLogEntity;
import com.zimo.genai.logs.mapper.LogsMapper;
import com.zimo.genai.logs.mapper.StatsMapper;
import org.springframework.web.bind.annotation.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 使用日志：明细检索 / 今日汇总 / Key 聚合 / 转发详情 */
@RestController
@RequestMapping("/api/logs")
public class LogController {

    private final LogsMapper logsMapper;
    private final StatsMapper statsMapper;

    public LogController(LogsMapper logsMapper, StatsMapper statsMapper) {
        this.logsMapper = logsMapper;
        this.statsMapper = statsMapper;
    }

    @GetMapping
    public Result<Map<String, Object>> list(@RequestParam(required = false) String startDate,
                                            @RequestParam(required = false) String endDate,
                                            @RequestParam(required = false) String model,
                                            @RequestParam(required = false) String status,
                                            @RequestParam(required = false) String apiKeyId,
                                            @RequestParam(required = false) String keyword,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "20") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", logsMapper.count(startDate, endDate, model, status, apiKeyId, keyword));
        data.put("list", logsMapper.list(startDate, endDate, model, status, apiKeyId, keyword, (page - 1) * size, (int) size));
        return Result.ok(data);
    }

    @GetMapping("/summary")
    public Result<Map<String, Object>> summary() { return Result.ok(statsMapper.todaySummary()); }

    @GetMapping("/apikeys")
    public Result<List<Map<String, Object>>> apikeys() { return Result.ok(statsMapper.groupApiKeys()); }

    /** 日志详情：按链路 ID 取转发内容日志（完整请求/响应 body） */
    @GetMapping("/relay/{traceId}")
    public Result<RelayLogEntity> relay(@PathVariable String traceId) { return Result.ok(statsMapper.relayByTrace(traceId)); }
}
