package com.zimo.genai.router.controller;

import com.zimo.genai.router.entity.ModelEntity;
import com.zimo.genai.router.mapper.RelayGuardMapper;
import com.zimo.genai.router.mapper.RouterModelMapper;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * OpenAI 兼容模型列表接口 —— 路由面固化接口（免登录）。
 *
 * GET /v1/models    全部上架模型（裸 OpenAI list 格式，供外接 SDK / OpenAI 客户端探测）
 * GET /v1/me        当前 API Key 自检（名称/模型白名单/限流配额），供体验中心等调用方联动
 *
 * 数据来源：直接只读 genai_models.tb_model_info 表（与转发同源，管理面改库后立即生效，
 * 数据面不依赖 jv-genai-models 管理面进程的可用性）。
 *
 * 其余所有接口路径均为动态转发：按请求体 model 查库定位 → base_url + path 转发，
 * 详见 RelayController；模型不存在/下架/路径未开放由转发面返回 OpenAI error 格式。
 */
@RestController
public class ModelListController {

    private final RouterModelMapper mapper;
    private final RelayGuardMapper guardMapper;

    public ModelListController(RouterModelMapper mapper, RelayGuardMapper guardMapper) {
        this.mapper = mapper;
        this.guardMapper = guardMapper;
    }

    /** 当前 API Key 自检：返回名称/模型白名单/限流配额；无效或缺失 Key 返回 401 */
    @GetMapping("/v1/me")
    public ResponseEntity<Map<String, Object>> me(
            @RequestHeader(value = "Authorization", required = false) String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")
                || authorization.substring(7).isBlank()) {
            return ResponseEntity.status(401).body(Map.of(
                    "error", Map.of("message", "缺少 API Key", "type", "invalid_request_error", "code", 401)));
        }
        Map<String, Object> row = guardMapper.selectApiKey(authorization.substring(7).trim());
        if (row == null) {
            return ResponseEntity.status(401).body(Map.of(
                    "error", Map.of("message", "无效的 API Key", "type", "invalid_request_error", "code", 401)));
        }
        Map<String, Object> body = new HashMap<>();
        body.put("object", "me");
        body.put("name", row.get("name"));
        body.put("key_id", row.get("keyId"));
        body.put("owner", row.get("owner"));
        Object models = row.get("models");
        body.put("models", models == null || String.valueOf(models).isBlank()
                ? List.of() : java.util.Arrays.asList(String.valueOf(models).split("\\s*,\\s*")));
        body.put("rpm", row.get("rpm"));
        body.put("tpm", row.get("tpm"));
        body.put("cc", row.get("cc"));
        return ResponseEntity.ok(body);
    }

    @GetMapping("/v1/models")
    public Map<String, Object> listModels() {
        List<Map<String, Object>> data = new ArrayList<>();
        for (ModelEntity m : mapper.selectEnabled()) data.add(toCompat(m));
        Map<String, Object> body = new HashMap<>();
        body.put("object", "list");
        body.put("data", data);
        return body;
    }

    /** OpenAI model 条目 + jv 扩展字段（真实模型名/接口路径/请求格式，供调用方探测转发规则） */
    private Map<String, Object> toCompat(ModelEntity m) {
        Map<String, Object> item = new HashMap<>();
        item.put("id", m.getName());
        item.put("object", "model");
        item.put("created", System.currentTimeMillis() / 1000);
        item.put("owned_by", m.getVendor() != null && !m.getVendor().isBlank() ? m.getVendor() : m.getProvider());
        item.put("jv-category", m.getCategory());
        item.put("jv-tier", m.getTier());
        item.put("jv-api-format", m.getApiFormat());
        item.put("jv-base-url", m.getBaseUrl());
        item.put("jv-real-model", m.getRealName() != null && !m.getRealName().isBlank() ? m.getRealName() : m.getName());
        item.put("jv-url-paths", parsePaths(m.getUrlPaths()));
        return item;
    }

    /** url_paths JSON 解析；为空时按模型默认格式给出常见路径兜底 */
    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> parsePaths(String json) {
        List<Map<String, Object>> paths = new ArrayList<>();
        if (json != null && !json.isBlank()) {
            try {
                List<Object> raw = new com.fasterxml.jackson.databind.ObjectMapper()
                        .readValue(json, List.class);
                for (Object o : raw) {
                    if (o instanceof Map) paths.add((Map<String, Object>) o);
                }
            } catch (Exception ignore) { /* JSON 非法时走兜底 */ }
        }
        if (paths.isEmpty()) {
            for (String p : new String[]{"/chat/completions"}) {
                Map<String, Object> e = new HashMap<>();
                e.put("path", p);
                e.put("format", "openai");
                paths.add(e);
            }
        }
        return paths;
    }
}
