package com.zimo.genai.logs.entity;

import java.time.LocalDateTime;

/** 转发内容日志（genai_logs.tb_relay_log，含完整请求/响应 body） */
public class RelayLogEntity {

    private Long id;
    private String traceId;
    private String model;
    private String method;
    private String path;
    private Integer statusCode;
    private Boolean isStream;
    private String question;
    private String requestBody;
    private String responseBody;
    private String errorMsg;
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getTraceId() { return traceId; }
    public void setTraceId(String traceId) { this.traceId = traceId; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getMethod() { return method; }
    public void setMethod(String method) { this.method = method; }
    public String getPath() { return path; }
    public void setPath(String path) { this.path = path; }
    public Integer getStatusCode() { return statusCode; }
    public void setStatusCode(Integer statusCode) { this.statusCode = statusCode; }
    public Boolean getIsStream() { return isStream; }
    public void setIsStream(Boolean isStream) { this.isStream = isStream; }
    public String getQuestion() { return question; }
    public void setQuestion(String question) { this.question = question; }
    public String getRequestBody() { return requestBody; }
    public void setRequestBody(String requestBody) { this.requestBody = requestBody; }
    public String getResponseBody() { return responseBody; }
    public void setResponseBody(String responseBody) { this.responseBody = responseBody; }
    public String getErrorMsg() { return errorMsg; }
    public void setErrorMsg(String errorMsg) { this.errorMsg = errorMsg; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
