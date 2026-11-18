package com.zimo.genai.agentgateway.entity;

import java.time.LocalDateTime;

/** Skill / Agent 注册实体 */
public class AgentEntity {
    private Long id;
    private String name;
    private String type;          // Skill / Agent
    private String model;
    private String tools;         // 逗号分隔工具名
    private String description;
    private Integer enabled;      // 1 启用 0 停用
    private LocalDateTime createdAt;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getTools() { return tools; }
    public void setTools(String tools) { this.tools = tools; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Integer getEnabled() { return enabled; }
    public void setEnabled(Integer enabled) { this.enabled = enabled; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
