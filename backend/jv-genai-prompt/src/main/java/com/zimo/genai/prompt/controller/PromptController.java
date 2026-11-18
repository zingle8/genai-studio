package com.zimo.genai.prompt.controller;

import com.zimo.genai.comm.auth.RequireRole;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.prompt.entity.PromptEntity;
import com.zimo.genai.prompt.mapper.PromptMapper;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/** 提示词管理：模板 CRUD */
@RestController
@RequestMapping("/api/prompts")
public class PromptController {

    private final PromptMapper mapper;

    public PromptController(PromptMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Map<String, Object>> list(@RequestParam(required = false) String keyword,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "20") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.count(keyword));
        data.put("list", mapper.list(keyword, (page - 1) * size, (int) size));
        return Result.ok(data);
    }

    @RequireRole("ADMIN")

    @PostMapping
    public Result<Object> create(@RequestBody PromptEntity e) {
        if (e.getName() == null || e.getName().isBlank()) return Result.fail(400, "模板名称不能为空");
        if (e.getStatus() == null) e.setStatus(1);
        mapper.insert(e);
        return Result.ok(e);
    }

    @RequireRole("ADMIN")

    @PutMapping("/{id}")
    public Result<Object> update(@PathVariable Long id, @RequestBody PromptEntity e) {
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
