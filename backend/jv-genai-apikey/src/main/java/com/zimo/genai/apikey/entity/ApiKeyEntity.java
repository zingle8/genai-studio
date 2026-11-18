package com.zimo.genai.apikey.entity;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * API Key 实体（业务模块，自建；不依赖网关 /keys）
 */
public class ApiKeyEntity {

    private Long id;
    private String name;
    private String keyId;
    private String apiKey;
    private String owner;
    private LocalDate expiryDate;      // NULL = 永久有效
    private String models;             // 逗号分隔；空 = 模型不限制
    private String fields;             // 使用领域，逗号分隔
    private String orgCompany;
    private String orgDept;
    private String orgBusiness;
    private Integer rpm;
    private Integer tpm;
    private Integer cc;
    private String remark;
    private Integer status;            // 1 启用 0 停用
    private Boolean expiryNever;       // 更新用：改为永久有效
    private LocalDateTime lastUsedAt;
    private LocalDateTime createdAt;

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
    public LocalDate getExpiryDate() { return expiryDate; }
    public void setExpiryDate(LocalDate expiryDate) { this.expiryDate = expiryDate; }
    public String getModels() { return models; }
    public void setModels(String models) { this.models = models; }
    public String getFields() { return fields; }
    public void setFields(String fields) { this.fields = fields; }
    public String getOrgCompany() { return orgCompany; }
    public void setOrgCompany(String orgCompany) { this.orgCompany = orgCompany; }
    public String getOrgDept() { return orgDept; }
    public void setOrgDept(String orgDept) { this.orgDept = orgDept; }
    public String getOrgBusiness() { return orgBusiness; }
    public void setOrgBusiness(String orgBusiness) { this.orgBusiness = orgBusiness; }
    public Integer getRpm() { return rpm; }
    public void setRpm(Integer rpm) { this.rpm = rpm; }
    public Integer getTpm() { return tpm; }
    public void setTpm(Integer tpm) { this.tpm = tpm; }
    public Integer getCc() { return cc; }
    public void setCc(Integer cc) { this.cc = cc; }
    public String getRemark() { return remark; }
    public void setRemark(String remark) { this.remark = remark; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public Boolean getExpiryNever() { return expiryNever; }
    public void setExpiryNever(Boolean expiryNever) { this.expiryNever = expiryNever; }
    public LocalDateTime getLastUsedAt() { return lastUsedAt; }
    public void setLastUsedAt(LocalDateTime lastUsedAt) { this.lastUsedAt = lastUsedAt; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
