package com.zimo.genai.scheduler.service;

import com.zimo.genai.scheduler.mapper.SchedulerMapper;
import com.zimo.genai.scheduler.model.JobConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.scheduling.support.CronTrigger;
import org.springframework.stereotype.Service;

import jakarta.annotation.PreDestroy;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ScheduledFuture;

/**
 * 任务调度器：启动时从 tb_job_config 加载启用的任务，按 cron 注册到线程池；
 * 支持运行时刷新、启停、手动触发。
 */
@Service
public class JobSchedulerService implements ApplicationRunner {

    private static final Logger log = LoggerFactory.getLogger(JobSchedulerService.class);

    private final SchedulerMapper mapper;
    private final StatJobService statJobService;
    private final ThreadPoolTaskScheduler taskScheduler;

    /** jobKey -> 已注册的定时任务句柄 */
    private final Map<String, ScheduledFuture<?>> tasks = new ConcurrentHashMap<>();

    public JobSchedulerService(SchedulerMapper mapper, StatJobService statJobService,
                               @Value("${scheduler.pool-size:4}") int poolSize) {
        this.mapper = mapper;
        this.statJobService = statJobService;
        this.taskScheduler = new ThreadPoolTaskScheduler();
        this.taskScheduler.setPoolSize(poolSize);
        this.taskScheduler.setThreadNamePrefix("genai-scheduler-");
        this.taskScheduler.setWaitForTasksToCompleteOnShutdown(true);
        this.taskScheduler.initialize();
    }

    @Override
    public void run(ApplicationArguments args) {
        refresh();
    }

    /** 重新加载全部任务（停掉旧的、按当前配置重建） */
    public synchronized int refresh() {
        tasks.values().forEach(f -> f.cancel(false));
        tasks.clear();

        int count = 0;
        for (JobConfig job : mapper.listEnabledJobs()) {
            schedule(job);
            count++;
        }
        log.info("定时任务已加载：{} 个启用任务", count);
        return count;
    }

    /** 注册单个任务 */
    private void schedule(JobConfig job) {
        try {
            CronTrigger trigger = new CronTrigger(job.getCronExpr());
            ScheduledFuture<?> future = taskScheduler.schedule(
                    () -> statJobService.run(job, "CRON"), trigger);
            if (future != null) {
                tasks.put(job.getJobKey(), future);
            }
        } catch (Exception e) {
            log.warn("任务 [{}] cron 表达式无效：{}", job.getJobKey(), job.getCronExpr(), e);
        }
    }

    /** 启停任务 */
    public synchronized void toggle(String jobKey, boolean enabled) {
        mapper.updateEnabled(jobKey, enabled ? 1 : 0);
        ScheduledFuture<?> f = tasks.remove(jobKey);
        if (f != null) {
            f.cancel(false);
        }
        if (enabled) {
            JobConfig job = mapper.findByKey(jobKey);
            if (job != null) {
                schedule(job);
            }
        }
    }

    /** 手动触发（异步执行，不阻塞接口） */
    public void trigger(String jobKey) {
        JobConfig job = mapper.findByKey(jobKey);
        if (job == null) {
            throw new IllegalArgumentException("任务不存在：" + jobKey);
        }
        taskScheduler.execute(() -> statJobService.run(job, "MANUAL"));
    }

    @PreDestroy
    public void shutdown() {
        tasks.values().forEach(f -> f.cancel(false));
        taskScheduler.shutdown();
    }
}
