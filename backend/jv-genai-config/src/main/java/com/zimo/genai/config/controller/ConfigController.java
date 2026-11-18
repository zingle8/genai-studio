package com.zimo.genai.config.controller;

import com.zimo.genai.comm.auth.RequireRole;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.config.entity.ConfigEntity;
import com.zimo.genai.config.mapper.ConfigMapper;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/** 平台配置：全局配置项 CRUD */
@RestController
@RequestMapping("/api/configs")
public class ConfigController {

    private final ConfigMapper mapper;

    public ConfigController(ConfigMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Map<String, Object>> list(@RequestParam(required = false) String keyword,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "50") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.count(keyword));
        data.put("list", mapper.list(keyword, (page - 1) * size, (int) size));
        return Result.ok(data);
    }

    /** 顶部公告（免登录读取，供基座公告条展示；enabled/content/link 三键） */
    @GetMapping("/announcement")
    public Result<Map<String, Object>> announcement() {
        Map<String, Object> data = new HashMap<>();
        boolean enabled = "true".equalsIgnoreCase(mapper.valueByKey("announce.enabled"));
        data.put("enabled", enabled);
        data.put("content", mapper.valueByKey("announce.content"));
        data.put("link", mapper.valueByKey("announce.link"));
        return Result.ok(data);
    }

    @RequireRole("ADMIN")

    @PostMapping
    public Result<Object> create(@RequestBody ConfigEntity e) {
        if (e.getConfigKey() == null || e.getConfigKey().isBlank()) return Result.fail(400, "配置键不能为空");
        mapper.insert(e);
        return Result.ok(e);
    }

    @RequireRole("ADMIN")

    @PutMapping("/{id}")
    public Result<Object> update(@PathVariable Long id, @RequestBody ConfigEntity e) {
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
