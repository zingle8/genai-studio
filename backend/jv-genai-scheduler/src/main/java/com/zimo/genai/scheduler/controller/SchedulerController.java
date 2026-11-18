package com.zimo.genai.scheduler.controller;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.scheduler.mapper.SchedulerMapper;
import com.zimo.genai.scheduler.service.JobSchedulerService;
import com.zimo.genai.scheduler.service.StatJobService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 定时任务调度服务接口
 *
 * GET    /api/scheduler/jobs               任务列表
 * POST   /api/scheduler/jobs/{jobKey}/run  手动触发
 * PUT    /api/scheduler/jobs/{jobKey}/toggle?enabled=true|false 启停
 * POST   /api/scheduler/refresh            重新加载任务
 * GET    /api/scheduler/stats              区间统计结果
 * GET    /api/scheduler/runs               执行记录
 */
@RestController
@RequestMapping("/api/scheduler")
public class SchedulerController {

    private final SchedulerMapper mapper;
    private final JobSchedulerService schedulerService;
    private final StatJobService statJobService;

    public SchedulerController(SchedulerMapper mapper, JobSchedulerService schedulerService,
                               StatJobService statJobService) {
        this.mapper = mapper;
        this.schedulerService = schedulerService;
        this.statJobService = statJobService;
    }

    @GetMapping("/jobs")
    public Result<Object> jobs() {
        return Result.ok(mapper.listJobs());
    }

    @PostMapping("/jobs/{jobKey}/run")
    public Result<Object> run(@PathVariable String jobKey) {
        try {
            schedulerService.trigger(jobKey);
            return Result.ok(Map.of("jobKey", jobKey, "message", "已触发，执行结果可在执行记录中查看"));
        } catch (IllegalArgumentException e) {
            return Result.fail(404, e.getMessage());
        }
    }

    @PutMapping("/jobs/{jobKey}/toggle")
    public Result<Object> toggle(@PathVariable String jobKey, @RequestParam boolean enabled) {
        schedulerService.toggle(jobKey, enabled);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("jobKey", jobKey);
        data.put("enabled", enabled);
        return Result.ok(data);
    }

    @PostMapping("/refresh")
    public Result<Object> refresh() {
        int count = schedulerService.refresh();
        return Result.ok(Map.of("enabledJobs", count));
    }

    /** 指定区间统计（手动补数） */
    @PostMapping("/run-range")
    public Result<Object> runRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate start,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate end,
            @RequestParam(defaultValue = "MIXED") String statType,
            @RequestParam(defaultValue = "CUSTOM") String periodType) {
        if (end.isBefore(start)) {
            return Result.fail(400, "结束日期不能早于开始日期");
        }
        return Result.ok(statJobService.runRange(start, end, statType, periodType));
    }

    /** 区间统计结果查询 */
    @GetMapping("/stats")
    public Result<Object> stats(@RequestParam(required = false) String statType,
                                @RequestParam(required = false) String periodType,
                                @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
                                @RequestParam(required = false) @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to,
                                @RequestParam(defaultValue = "30") int limit) {
        return Result.ok(mapper.listStats(statType, periodType, from, to, Math.min(Math.max(limit, 1), 365)));
    }

    @GetMapping("/runs")
    public Result<Object> runs(@RequestParam(defaultValue = "20") int limit) {
        return Result.ok(mapper.listRuns(Math.min(Math.max(limit, 1), 200)));
    }
}
