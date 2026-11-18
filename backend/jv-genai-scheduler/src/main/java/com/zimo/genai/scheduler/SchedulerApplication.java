package com.zimo.genai.scheduler;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 定时任务调度服务
 *
 * 职责：按 cron 定时执行数据统计任务（订单 / 成本 / 用量区间聚合），
 * 统计结果落库 genai_scheduler.tb_stat_period，并提供查询与手动触发接口。
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-scheduler
 * 服务名：定时任务调度服务
 */
@SpringBootApplication
public class SchedulerApplication {

    public static void main(String[] args) {
        SpringApplication.run(SchedulerApplication.class, args);
    }
}
