package com.zimo.genai.models.controller;

import com.zimo.genai.comm.auth.RequireRole;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.models.entity.ModelEntity;
import com.zimo.genai.models.mapper.ModelMapper;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** 模型广场：模型注册/上下架管理 */
@RestController
@RequestMapping("/api/models")
public class ModelController {

    private final ModelMapper mapper;

    public ModelController(ModelMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Map<String, Object>> list(@RequestParam(required = false) String keyword,
                                            @RequestParam(required = false) String provider,
                                            @RequestParam(required = false) String vendor,
                                            @RequestParam(required = false) String category,
                                            @RequestParam(required = false) String tier,
                                            @RequestParam(required = false) Integer status,
                                            @RequestParam(defaultValue = "1") long page,
                                            @RequestParam(defaultValue = "20") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.count(keyword, provider, vendor, category, tier, status));
        List<ModelEntity> list = mapper.list(keyword, provider, vendor, category, tier, status,
                (page - 1) * size, (int) size);
        list.forEach(m -> m.setApiKey(maskKey(m.getApiKey()))); // apiKey 掩码返回，不泄露明文
        data.put("list", list);
        return Result.ok(data);
    }

    /** apiKey 脱敏：保留前 3 后 4 位 */
    private String maskKey(String key) {
        if (key == null || key.isBlank()) return "";
        if (key.length() <= 8) return key.charAt(0) + "****";
        return key.substring(0, Math.min(3, key.length())) + "****" + key.substring(key.length() - 4);
    }

    @RequireRole("ADMIN")

    @PostMapping
    public Result<Object> create(@RequestBody ModelEntity e) {
        if (e.getName() == null || e.getName().isBlank()) return Result.fail(400, "模型名称不能为空");
        if (e.getStatus() == null) e.setStatus(1);
        mapper.insert(e);
        return Result.ok(e);
    }

    @RequireRole("ADMIN")

    @PutMapping("/{id}")
    public Result<Object> update(@PathVariable Long id, @RequestBody ModelEntity e) {
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
