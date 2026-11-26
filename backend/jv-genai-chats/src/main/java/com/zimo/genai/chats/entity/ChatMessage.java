package com.zimo.genai.chats.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/** 消息实体（tb_chat_message 按日 RANGE 分区） */
public class ChatMessage {
    private Long id;
    private Long sessionId;
    private String role;              // user / assistant
    private String content;
    private String reasoningContent;  // 推理模型的思考过程（user 消息为空）
    private String model;             // 产生该回复的模型（user 消息为空）
    private String traceId;           // 轮次关联 ID（一次提问 + N 个模型回复同 trace）
    private Integer promptTokens = 0;
    private Integer completionTokens = 0;
    private Integer durationMs = 0;   // 请求→回复总耗时(ms)
    private BigDecimal cost = BigDecimal.ZERO;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getSessionId() { return sessionId; }
    public void setSessionId(Long sessionId) { this.sessionId = sessionId; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
    public String getReasoningContent() { return reasoningContent; }
    public void setReasoningContent(String reasoningContent) { this.reasoningContent = reasoningContent; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }
    public Integer getPromptTokens() { return promptTokens; }
    public void setPromptTokens(Integer promptTokens) { this.promptTokens = promptTokens; }
    public Integer getCompletionTokens() { return completionTokens; }
    public void setCompletionTokens(Integer completionTokens) { this.completionTokens = completionTokens; }
    public Integer getDurationMs() { return durationMs; }
    public void setDurationMs(Integer durationMs) { this.durationMs = durationMs; }
    public BigDecimal getCost() { return cost; }
    public void setCost(BigDecimal cost) { this.cost = cost; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
