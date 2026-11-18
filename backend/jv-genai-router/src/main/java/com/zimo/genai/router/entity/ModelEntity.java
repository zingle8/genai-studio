package com.zimo.genai.router.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;

/** 模型信息（转发面视图：来自 genai_models.tb_model_info，只读） */
public class ModelEntity {
    private Long id;
    private String name;         // 平台对外模型名
    private String realName;     // 真实模型名（转发上游时使用）
    private String provider;
    private String vendor;
    private String apiFormat;    // openai / claude / gemini / other
    private String baseUrl;      // 上游服务地址
    private String apiKey;       // 上游鉴权密钥
    private String urlPaths;     // 开放的接口路径 JSON：[{path, format}]
    private String category;
    private String tier;         // 模型等级：旗舰/标准/免费（计费单价）
    private Integer contextLen;
    private Integer status;      // 1 上架 0 下架

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getRealName() { return realName; }
    public void setRealName(String realName) { this.realName = realName; }
    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public String getVendor() { return vendor; }
    public void setVendor(String vendor) { this.vendor = vendor; }
    public String getApiFormat() { return apiFormat; }
    public void setApiFormat(String apiFormat) { this.apiFormat = apiFormat; }
    public String getBaseUrl() { return baseUrl; }
    public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
    public String getUrlPaths() { return urlPaths; }
    public void setUrlPaths(String urlPaths) { this.urlPaths = urlPaths; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    public String getTier() { return tier; }
    public void setTier(String tier) { this.tier = tier; }
    public Integer getContextLen() { return contextLen; }
    public void setContextLen(Integer contextLen) { this.contextLen = contextLen; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
}
