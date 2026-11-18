package com.zimo.genai.models.entity;

import java.time.LocalDateTime;

/** 模型信息实体 */
public class ModelEntity {
    private Long id;
    private String name;         // 平台对外模型名
    private String realName;     // 真实模型名（转发上游厂商时使用）
    private String provider;
    private String vendor;       // 模型厂商：智谱/DeepSeek/OpenAI/Anthropic/Google/本地
    private String apiFormat;    // 接口格式：openai/claude/gemini/other
    private String baseUrl;      // 模型服务 Base URL（外接转发）
    private String apiKey;       // 外接模型 API Key（查询时掩码返回）
    private String urlPaths;     // 接口路径列表 JSON：[{"path":"/chat/completions","format":"openai"}]
    private String category;      // 文本生成 / 多模态 / 向量
    private String tier;          // 模型等级：旗舰/标准/免费（关联 tb_model_price 计费）
    private Integer contextLen;
    private Integer status;       // 1 上架 0 下架
    private String description;   // 模型描述（广场摘要）
    private String detail;        // 模型详情（广场详情）
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getProvider() { return provider; }
    public void setProvider(String provider) { this.provider = provider; }
    public String getRealName() { return realName; }
    public void setRealName(String realName) { this.realName = realName; }
    public String getVendor() { return vendor; }
    public void setVendor(String vendor) { this.vendor = vendor; }
    public String getApiFormat() { return apiFormat; }
    public void setApiFormat(String apiFormat) { this.apiFormat = apiFormat; }
    public String getBaseUrl() { return baseUrl; }
    public void setBaseUrl(String baseUrl) { this.baseUrl = baseUrl; }
    public String getApiKey() { return apiKey; }
    public void setApiKey(String apiKey) { this.apiKey = apiKey; }
    public String getDetail() { return detail; }
    public void setDetail(String detail) { this.detail = detail; }
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
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
