package com.zimo.genai.router.entity;

import java.math.BigDecimal;

/**
 * API Key（转发鉴权/限流视图：跨库只读 genai_apikey.tb_api_key）。
 * rpm/tpm/cc 为该 Key 的限流配置：null = 不限制。
 */
public class ApiKeyEntity {
    private Long id;
    private String name;        // Key 名称
    private String keyId;       // 对外展示的 Key ID（如 kid=10048231）
    private String apiKey;      // 完整密钥（Bearer 校验用）
    private String owner;
    private String expiryDate;  // 过期日期 yyyy-MM-dd，null=永久
    private String models;      // 允许的模型，逗号分隔；空 = 不限
    private Integer rpm;        // 请求数/分钟
    private Integer tpm;        // Token/分钟
    private Integer cc;         // 并发上限
    private BigDecimal balance; // 账户余额（genai_billing.tb_account_balance，单账户）

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getKeyId() { return keyId; }
    public void setKeyId(String keyId) { this.keyId = keyId; }
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
    public String getOwner() { return owner; }
    public void setOwner(String owner) { this.owner = owner; }
    public String getExpiryDate() { return expiryDate; }
    public void setExpiryDate(String expiryDate) { this.expiryDate = expiryDate; }
    public String getModels() { return models; }
    public void setModels(String models) { this.models = models; }
    public Integer getRpm() { return rpm; }
    public void setRpm(Integer rpm) { this.rpm = rpm; }
    public Integer getTpm() { return tpm; }
    public void setTpm(Integer tpm) { this.tpm = tpm; }
    public Integer getCc() { return cc; }
    public void setCc(Integer cc) { this.cc = cc; }
    public BigDecimal getBalance() { return balance; }
    public void setBalance(BigDecimal balance) { this.balance = balance; }
}
