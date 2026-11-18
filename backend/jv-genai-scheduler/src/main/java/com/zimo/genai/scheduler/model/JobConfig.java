package com.zimo.genai.scheduler.model;

/**
 * 定时任务配置（表 tb_job_config）
 */
public class JobConfig {

    private Long id;
    private String jobKey;
    private String jobName;
    private String cronExpr;
    /** 统计类型：ORDER 订单 / COST 成本 / MIXED 订单+成本 */
    private String statType;
    /** 统计周期：DAILY / WEEKLY / MONTHLY */
    private String periodType;
    /** 回溯天数（统计窗口 = [今天-daysBack, 昨天]） */
    private Integer daysBack;
    private String description;
    private Integer enabled;
    private String lastStatus;
    private String lastMessage;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getJobKey() { return jobKey; }
    public void setJobKey(String jobKey) { this.jobKey = jobKey; }
    public String getJobName() { return jobName; }
    public void setJobName(String jobName) { this.jobName = jobName; }
    public String getCronExpr() { return cronExpr; }
    public void setCronExpr(String cronExpr) { this.cronExpr = cronExpr; }
    public String getStatType() { return statType; }
    public void setStatType(String statType) { this.statType = statType; }
    public String getPeriodType() { return periodType; }
    public void setPeriodType(String periodType) { this.periodType = periodType; }
    public Integer getDaysBack() { return daysBack; }
    public void setDaysBack(Integer daysBack) { this.daysBack = daysBack; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Integer getEnabled() { return enabled; }
    public void setEnabled(Integer enabled) { this.enabled = enabled; }
    public String getLastStatus() { return lastStatus; }
    public void setLastStatus(String lastStatus) { this.lastStatus = lastStatus; }
    public String getLastMessage() { return lastMessage; }
    public void setLastMessage(String lastMessage) { this.lastMessage = lastMessage; }
}
