package com.zimo.genai.agentgateway.controller;

import com.zimo.genai.comm.auth.RequireRole;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.agentgateway.entity.AgentEntity;
import com.zimo.genai.agentgateway.mapper.AgentMapper;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/** Skill / Agent 管理：注册与启停（编排执行能力后续接入） */
@RestController
@RequestMapping("/api/agents")
public class AgentController {

    private final AgentMapper mapper;

    public AgentController(AgentMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Map<String, Object>> list(@RequestParam(required = false) String type,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "20") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.count(type));
        data.put("list", mapper.list(type, (page - 1) * size, (int) size));
        return Result.ok(data);
    }

    @RequireRole("ADMIN")

    @PostMapping
    public Result<Object> create(@RequestBody AgentEntity e) {
        if (e.getName() == null || e.getName().isBlank()) return Result.fail(400, "名称不能为空");
        if (e.getEnabled() == null) e.setEnabled(1);
        if (e.getType() == null) e.setType("Agent");
        mapper.insert(e);
        return Result.ok(e);
    }

    @RequireRole("ADMIN")

    @PutMapping("/{id}")
    public Result<Object> update(@PathVariable Long id, @RequestBody AgentEntity e) {
        e.setId(id);
        mapper.update(e);
        return Result.ok(Map.of("id", id));
    }

    @RequireRole("ADMIN")

    @DeleteMapping("/{id}")
    public Result<Object> delete(@PathVariable Long id) {
        mapper.delete(id);
        return Result.ok(Map.of("id", id));
    }
}
