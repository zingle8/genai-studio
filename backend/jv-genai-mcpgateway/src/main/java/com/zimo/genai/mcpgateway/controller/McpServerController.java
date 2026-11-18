package com.zimo.genai.mcpgateway.controller;

import com.zimo.genai.comm.auth.RequireRole;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.mcpgateway.entity.McpServerEntity;
import com.zimo.genai.mcpgateway.mapper.McpServerMapper;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/** MCP 管理：MCP 服务注册/启停（调用转发能力后续接入） */
@RestController
@RequestMapping("/api/mcp")
public class McpServerController {

    private final McpServerMapper mapper;

    public McpServerController(McpServerMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Map<String, Object>> list(@RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "20") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.count());
        data.put("list", mapper.list((page - 1) * size, (int) size));
        return Result.ok(data);
    }

    @RequireRole("ADMIN")

    @PostMapping
    public Result<Object> create(@RequestBody McpServerEntity e) {
        if (e.getName() == null || e.getName().isBlank()) return Result.fail(400, "名称不能为空");
        if (e.getStatus() == null) e.setStatus(1);
        mapper.insert(e);
        return Result.ok(e);
    }

    @RequireRole("ADMIN")

    @PutMapping("/{id}")
    public Result<Object> update(@PathVariable Long id, @RequestBody McpServerEntity e) {
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
