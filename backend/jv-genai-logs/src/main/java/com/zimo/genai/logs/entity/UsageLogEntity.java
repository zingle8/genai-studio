package com.zimo.genai.logs.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 调用统计日志（genai_logs.tb_usage_log） */
public class UsageLogEntity {

    private Long id;
    private String traceId;
    private String apiKeyId;
    private String apiKeyName;
    private String model;
    private String serviceId;
    private Integer promptTokens;
    private Integer completionTokens;
    private Integer totalTokens;
    private BigDecimal cost;
    private Integer durationMs;
    private String status;
    private String ip;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }
    public String getApiKeyId() { return apiKeyId; }
    public void setApiKeyId(String apiKeyId) { this.apiKeyId = apiKeyId; }
    public String getApiKeyName() { return apiKeyName; }
    public void setApiKeyName(String apiKeyName) { this.apiKeyName = apiKeyName; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getServiceId() { return serviceId; }
    public void setServiceId(String serviceId) { this.serviceId = serviceId; }
    public Integer getPromptTokens() { return promptTokens; }
    public void setPromptTokens(Integer promptTokens) { this.promptTokens = promptTokens; }
    public Integer getCompletionTokens() { return completionTokens; }
    public void setCompletionTokens(Integer completionTokens) { this.completionTokens = completionTokens; }
    public Integer getTotalTokens() { return totalTokens; }
    public void setTotalTokens(Integer totalTokens) { this.totalTokens = totalTokens; }
    public BigDecimal getCost() { return cost; }
    public void setCost(BigDecimal cost) { this.cost = cost; }
    public Integer getDurationMs() { return durationMs; }
    public void setDurationMs(Integer durationMs) { this.durationMs = durationMs; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public String getIp() { return ip; }
    public void setIp(String ip) { this.ip = ip; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
