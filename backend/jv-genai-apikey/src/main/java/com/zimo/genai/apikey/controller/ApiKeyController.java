package com.zimo.genai.apikey.controller;

import com.zimo.genai.apikey.entity.ApiKeyEntity;
import com.zimo.genai.apikey.mapper.ApiKeyMapper;
import com.zimo.genai.comm.api.Result;
import org.springframework.web.bind.annotation.*;

import java.security.SecureRandom;
import java.time.LocalDate;
import java.util.*;

/**
 * API Key 密钥服务（自建业务模块）。
 *
 * 参考 DeepSeek 开发者控制台：Key 仅在创建/轮转时完整展示一次，
 * 列表中仅展示掩码形式（sk-xxxxxx...xxxx）。
 */
@RestController
@RequestMapping("/api/apikeys")
public class ApiKeyController {

    private final ApiKeyMapper mapper;
    private static final char[] HEX = "0123456789abcdef".toCharArray();
    private static final SecureRandom RANDOM = new SecureRandom();

    public ApiKeyController(ApiKeyMapper mapper) {
        this.mapper = mapper;
    }

    /** 分页查询（owner/keyword 过滤） */
    @GetMapping
    public Result<Map<String, Object>> list(
            @RequestParam(required = false) String owner,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "50") long size) {

        long total = mapper.count(owner, keyword);
        List<Map<String, Object>> list = new ArrayList<>();
        for (ApiKeyEntity k : mapper.list(owner, keyword, (page - 1) * size, (int) size)) {
            Map<String, Object> row = toRow(k);
            row.put("apiKey", mask(k.getApiKey()));   // 列表仅展示掩码
            list.add(row);
        }
        Map<String, Object> data = new HashMap<>();
        data.put("total", total);
        data.put("list", list);
        return Result.ok(data);
    }

    /** 体验中心/平台内调用：当前用户的可用 Key（status=1 且未过期；返回完整值供平台内直连 router 使用） */
    @GetMapping("/usable")
    public Result<List<Map<String, Object>>> usable(@RequestParam(required = false) String owner) {
        List<Map<String, Object>> out = new ArrayList<>();
        for (ApiKeyEntity k : mapper.list(owner, null, 0, 100)) {
            if (k.getStatus() == null || k.getStatus() != 1) {
                continue;
            }
            if (k.getExpiryDate() != null && k.getExpiryDate().isBefore(LocalDate.now())) {
                continue;
            }
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", k.getId());
            m.put("name", k.getName());
            m.put("apiKey", k.getApiKey());
            m.put("rpm", k.getRpm());
            m.put("tpm", k.getTpm());
            m.put("cc", k.getCc());
            m.put("models", k.getModels() == null || k.getModels().isEmpty()
                    ? null : Arrays.asList(k.getModels().split(",")));
            m.put("remark", k.getRemark());
            out.add(m);
        }
        return Result.ok(out);
    }

    /** 创建（完整 Key 仅本次返回） */
    @PostMapping
    public Result<Map<String, Object>> create(@RequestBody Map<String, Object> body) {
        ApiKeyEntity k = new ApiKeyEntity();
        k.setName(str(body.get("name")));
        if (k.getName() == null || k.getName().isEmpty()) {
            return Result.fail(400, "名称不能为空");
        }
        k.setKeyId("kid=" + (10000000 + RANDOM.nextInt(90000000)));
        k.setApiKey(genKey());
        k.setOwner(str(body.get("owner")));
        k.setExpiryDate(parseExpiry(body));
        k.setModels(joinList(body.get("models")));
        k.setFields(joinList(body.get("fields")));
        k.setOrgCompany(org(body, "company"));
        k.setOrgDept(org(body, "dept"));
        k.setOrgBusiness(org(body, "business"));
        k.setRpm(intOrNull(body.get("rpm")));
        k.setTpm(intOrNull(body.get("tpm")));
        k.setCc(intOrNull(body.get("cc")));
        k.setRemark(str(body.get("remark")));
        mapper.insert(k);

        Map<String, Object> data = toRow(k);
        data.put("apiKey", k.getApiKey());   // 仅创建时返回完整 Key
        return Result.ok(data);
    }

    /** 更新配置 */
    @PutMapping("/{id}")
    public Result<Object> update(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        ApiKeyEntity k = new ApiKeyEntity();
        k.setId(id);
        k.setName(str(body.get("name")));
        k.setExpiryDate(parseExpiry(body));
        k.setModels(joinList(body.get("models")));
        k.setFields(joinList(body.get("fields")));
        k.setOrgCompany(org(body, "company"));
        k.setOrgDept(org(body, "dept"));
        k.setOrgBusiness(org(body, "business"));
        k.setRpm(intOrNull(body.get("rpm")));
        k.setTpm(intOrNull(body.get("tpm")));
        k.setCc(intOrNull(body.get("cc")));
        k.setRemark(str(body.get("remark")));
        if (body.get("status") instanceof Number n) {
            k.setStatus(n.intValue());
        }
        if (Boolean.TRUE.equals(body.get("expiryNever"))) {
            k.setExpiryNever(true);
        }
        mapper.update(k);
        return Result.ok(Map.of("id", id));
    }

    /** 轮转：生成新 Key，旧 Key 立即失效（完整 Key 仅本次返回） */
    @PostMapping("/{id}/rotate")
    public Result<Map<String, Object>> rotate(@PathVariable Long id) {
        ApiKeyEntity k = mapper.getById(id);
        if (k == null) {
            return Result.fail(404, "API Key 不存在");
        }
        k.setApiKey(genKey());
        k.setLastUsedAt(null);
        mapper.update(k);
        Map<String, Object> data = toRow(k);
        data.put("apiKey", k.getApiKey());
        return Result.ok(data);
    }

    /** 延期：过期时间 +1 年 */
    @PostMapping("/{id}/renew")
    public Result<Object> renew(@PathVariable Long id) {
        ApiKeyEntity k = mapper.getById(id);
        if (k == null) {
            return Result.fail(404, "API Key 不存在");
        }
        LocalDate base = k.getExpiryDate() != null ? k.getExpiryDate() : LocalDate.now();
        k.setExpiryDate(base.plusYears(1));
        k.setExpiryNever(false);
        mapper.update(k);
        return Result.ok(Map.of("id", id, "expiryDate", k.getExpiryDate().toString()));
    }

    /** 删除 */
    @DeleteMapping("/{id}")
    public Result<Object> delete(@PathVariable Long id) {
        mapper.delete(id);
        return Result.ok(Map.of("id", id));
    }

    // ---------- helpers ----------

    private Map<String, Object> toRow(ApiKeyEntity k) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", k.getId());
        m.put("name", k.getName());
        m.put("keyId", k.getKeyId());
        m.put("owner", k.getOwner());
        m.put("expiryDate", k.getExpiryDate() == null ? null : k.getExpiryDate().toString());
        m.put("models", k.getModels() == null || k.getModels().isEmpty()
                ? null : Arrays.asList(k.getModels().split(",")));
        m.put("fields", k.getFields() == null || k.getFields().isEmpty()
                ? null : Arrays.asList(k.getFields().split(",")));
        m.put("org", Map.of("company", nz(k.getOrgCompany()), "dept", nz(k.getOrgDept()),
                "business", nz(k.getOrgBusiness())));
        m.put("rpm", k.getRpm());
        m.put("tpm", k.getTpm());
        m.put("cc", k.getCc());
        m.put("remark", k.getRemark());
        m.put("status", k.getStatus());
        m.put("lastUsedAt", k.getLastUsedAt() == null ? "未使用" : k.getLastUsedAt().toString());
        m.put("createdAt", k.getCreatedAt() == null ? null : k.getCreatedAt().toString());
        return m;
    }

    private String genKey() {
        StringBuilder sb = new StringBuilder("sk-");
        for (int i = 0; i < 48; i++) {
            sb.append(HEX[RANDOM.nextInt(16)]);
        }
        return sb.toString();
    }

    private String mask(String key) {
        if (key == null || key.length() < 12) {
            return key;
        }
        return key.substring(0, 7) + "..." + key.substring(key.length() - 4);
    }

    private LocalDate parseExpiry(Map<String, Object> body) {
        Object type = body.get("expiryType");
        if (type == null || "never".equals(type)) {
            return null;
        }
        String d = str(body.get("expiryDate"));
        return d == null || d.isEmpty() ? null : LocalDate.parse(d);
    }

    private String joinList(Object v) {
        if (v instanceof List<?> l && !l.isEmpty()) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < l.size(); i++) {
                if (i > 0) sb.append(',');
                sb.append(l.get(i));
            }
            return sb.toString();
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private String org(Map<String, Object> body, String key) {
        Object o = body.get("org");
        if (o instanceof Map<?, ?> m) {
            Object v = ((Map<String, Object>) m).get(key);
            return v == null ? null : v.toString();
        }
        return null;
    }

    private Integer intOrNull(Object v) {
        if (v instanceof Number n && n.longValue() > 0) {
            return n.intValue();
        }
        return null;
    }

    private String str(Object v) {
        return v == null ? null : v.toString().trim();
    }

    private String nz(String v) {
        return v == null ? "" : v;
    }
}
