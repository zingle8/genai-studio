package com.zimo.genai.router.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.zimo.genai.router.entity.ModelEntity;
import com.zimo.genai.router.mapper.RelayLogMapper;
import com.zimo.genai.router.mapper.RouterModelMapper;
import com.zimo.genai.router.service.GuardException;
import com.zimo.genai.router.service.RelayGuardService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 模型转发网关：按请求体 model（平台对外名）查库定位模型记录，转发到 base_url + path，
 * model 替换为 real_name，按模型格式注入上游鉴权头，支持流式响应透传。
 *
 * 转发前校验链（RelayGuardService）：
 *   1. API Key 鉴权（Bearer：有效/未过期/模型白名单）→ 401/403
 *   2. 账户余额检查 → 402
 *   3. 限流：RPM/TPM 分钟窗口 + CC 并发信号量 → 429
 * 转发后：按模型等级（tier）单价 × token 用量扣减余额，写 tb_usage_log 与 tb_cost_daily。
 */
@RestController
public class RelayController {

    private static final Logger log = LoggerFactory.getLogger(RelayController.class);
    private static final Pattern P_PROMPT = Pattern.compile("\"prompt_tokens\"\\s*:\\s*(\\d+)");
    private static final Pattern P_COMPLETION = Pattern.compile("\"completion_tokens\"\\s*:\\s*(\\d+)");
    private static final int STREAM_CAPTURE_LIMIT = 2 * 1024 * 1024;
    private static final int LOG_TRUNC = 65536; // 请求/回复日志单侧截断 64KB
    // base_url 支持逗号分隔的多实例地址，按请求原子轮询（round-robin）分发
    private final AtomicInteger rrCounter = new AtomicInteger(0);

    private final RouterModelMapper modelMapper;
    private final RelayGuardService guard;
    private final RelayLogMapper relayLogMapper;
    private final ObjectMapper om = new ObjectMapper();
    // 固定 HTTP/1.1：JDK 25 HttpClient 默认发送 Upgrade: h2c，Python uvicorn(h11) 会拒绝该请求（422/空 body）
    private final java.net.http.HttpClient client = java.net.http.HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(15))
            .version(java.net.http.HttpClient.Version.HTTP_1_1)
            .build();

    private static final Set<String> HOP_HEADERS = Set.of(
            "connection", "keep-alive", "transfer-encoding", "upgrade",
            "proxy-authenticate", "proxy-authorization", "te", "trailer");

    public RelayController(RouterModelMapper modelMapper, RelayGuardService guard, RelayLogMapper relayLogMapper) {
        this.modelMapper = modelMapper;
        this.guard = guard;
        this.relayLogMapper = relayLogMapper;
    }

    @PostMapping(value = {"/v1/**", "/chat/completions", "/v1/messages",
            "/v1/responses", "/v1/responses/compact", "/v1/completions", "/v1/embeddings"})
    public void relay(HttpServletRequest request, HttpServletResponse response) throws Exception {
        long t0 = System.currentTimeMillis();
        String path = normalizePath(request.getRequestURI());

        // 1. 读取请求体并解析模型名（同时提取用户当前问题，供内容日志直接展示）
        String body = new String(request.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        String modelName = extractModel(body);
        String question = extractQuestion(body);
        if (modelName == null || modelName.isBlank()) {
            writeError(response, 400, "请求体缺少 model 字段");
            return;
        }

        // 2. 转发前校验链：鉴权 → 余额 → 限流（异常统一 OpenAI error 格式）
        RelayGuardService.AuthKey key;
        RelayGuardService.Ticket ticket = null;
        try {
            key = guard.authenticate(request.getHeader("Authorization"), modelName);
            guard.checkBalance();
            ticket = guard.acquire(key, body.length() / 4);
        } catch (GuardException e) {
            writeError(response, e.getStatus(), e.getMessage());
            return;
        }

        // 3. 查模型配置（不存在/下架/未配地址/路径未开放）
        ModelEntity m = modelMapper.selectByName(modelName);
        if (m == null || m.getStatus() == null || m.getStatus() != 1) {
            guard.release(key, ticket);
            writeError(response, 404, "模型不存在或已下架: " + modelName);
            return;
        }
        if (m.getBaseUrl() == null || m.getBaseUrl().isBlank()) {
            guard.release(key, ticket);
            writeError(response, 400, "模型未配置 Base URL，无法转发: " + modelName);
            return;
        }
        if (!pathAllowed(m.getUrlPaths(), path)) {
            guard.release(key, ticket);
            writeError(response, 400, "模型 " + modelName + " 未开放接口路径: " + path);
            return;
        }

        // 4. 构造上游请求：baseUrl + path，model 替换为真实模型名
        //    base_url 可为逗号分隔的多实例地址，原子轮询分发以提升本地模型吞吐
        String baseUrl = pickBaseUrl(m.getBaseUrl());
        String upstreamUrl = joinUrl(baseUrl, path);
        String upstreamBody = replaceModel(body, m.getRealName());
        HttpRequest.Builder rb = HttpRequest.newBuilder(URI.create(upstreamUrl))
                .timeout(Duration.ofMinutes(10))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(upstreamBody, StandardCharsets.UTF_8));

        // 5. 按格式注入上游鉴权头（空 key 不注入，适配本地模型），透传少量调用方头
        String format = m.getApiFormat() == null ? "openai" : m.getApiFormat();
        String apiKey = m.getApiKey() == null ? "" : m.getApiKey().trim();
        switch (format) {
            case "claude" -> {
                if (!apiKey.isEmpty()) rb.header("x-api-key", apiKey);
                rb.header("anthropic-version", headerOr(request, "anthropic-version", "2023-06-01"));
            }
            case "gemini" -> { if (!apiKey.isEmpty()) rb.header("x-goog-api-key", apiKey); }
            default -> { if (!apiKey.isEmpty()) rb.header("Authorization", "Bearer " + apiKey); }
        }
        passHeader(request, rb, "OpenAI-Beta");
        passHeader(request, rb, "Accept");

        // 6. 发送上游（失败记 fail 日志并返回 502）
        HttpResponse<InputStream> up;
        try {
            log.info("[relay] {} {} -> {} (model: {} -> {}, format: {}, key: {})",
                    request.getMethod(), path, upstreamUrl, modelName, m.getRealName(), format, key.keyId);
            up = client.send(rb.build(), HttpResponse.BodyHandlers.ofInputStream());
        } catch (Exception e) {
            guard.release(key, ticket);
            log.warn("[relay] 上游调用失败: {} {}", upstreamUrl, e.getMessage());
            String traceId = guard.recordUsage(key, modelName, m.getTier(), 0, 0,
                    System.currentTimeMillis() - t0, "fail", request.getRemoteAddr());
            logRelay(traceId, modelName, request.getMethod(), path, question, isStreamReq(body), 0, upstreamBody, "", e.getMessage());
            writeError(response, 502, "上游服务调用失败: " + e.getMessage());
            return;
        }

        // 7. 透传响应 + 事后记账（tier 单价 × token 用量扣费，写 tb_usage_log / tb_cost_daily）
        boolean stream = String.valueOf(up.headers().firstValue("content-type").orElse(""))
                .toLowerCase().contains("text/event-stream");
        long prompt = 0, completion = 0;
        String respContent = "";
        try (InputStream in = up.body(); OutputStream out = response.getOutputStream()) {
            response.setStatus(up.statusCode());
            up.headers().map().forEach((k, vs) -> {
                if (!HOP_HEADERS.contains(k.toLowerCase())) vs.forEach(v -> response.addHeader(k, v));
            });
            if (stream) {
                StringBuilder cap = new StringBuilder(); // 限量收集，用于解析末帧 usage
                byte[] buf = new byte[8192];
                int n;
                while ((n = in.read(buf)) != -1) {
                    out.write(buf, 0, n);
                    out.flush();
                    if (cap.length() < STREAM_CAPTURE_LIMIT) {
                        cap.append(new String(buf, 0, n, StandardCharsets.UTF_8));
                    }
                }
                respContent = cap.toString();
                long[] u = parseUsage(respContent);
                prompt = u[0]; completion = u[1];
            } else {
                byte[] all = in.readAllBytes();
                out.write(all);
                out.flush();
                respContent = new String(all, StandardCharsets.UTF_8);
                long[] u = parseUsage(respContent);
                prompt = u[0]; completion = u[1];
            }
        } finally {
            guard.release(key, ticket, prompt + completion);
            String traceId = guard.recordUsage(key, modelName, m.getTier(), prompt, completion,
                    System.currentTimeMillis() - t0,
                    up.statusCode() < 400 ? "success" : "fail", request.getRemoteAddr());
            logRelay(traceId, modelName, request.getMethod(), path, question, stream,
                    up.statusCode(), upstreamBody,
                    stream ? buildStreamRespJson(respContent, modelName, prompt, completion) : respContent, "");
        }
    }

    /** 请求/回复内容日志（tb_relay_log，trace_id 与 tb_usage_log 同源对齐；失败仅告警不影响转发） */
    private void logRelay(String traceId, String model, String method, String path, String question,
                          boolean isStream, int status, String reqBody, String respBody, String errorMsg) {
        try {
            relayLogMapper.insertRelayLog(traceId, model, method, path,
                    trunc(question), status, isStream,
                    trunc(reqBody), trunc(respBody), errorMsg == null ? "" : errorMsg.substring(0, Math.min(errorMsg.length(), 512)));
        } catch (Exception e) {
            log.warn("[relay] 内容日志写入失败: {}", e.getMessage());
        }
    }

    private String trunc(String s) {
        if (s == null) return "";
        return s.length() <= LOG_TRUNC ? s : s.substring(0, LOG_TRUNC);
    }

    /* ===== 内容日志辅助：用户当前问题 / 流式判定 / SSE 聚合 ===== */

    /** 提取用户当前问题：messages 最后一条 user 消息 content（兼容字符串与分段数组） */
    @SuppressWarnings("unchecked")
    private String extractQuestion(String body) {
        try {
            Map<String, Object> root = om.readValue(body, Map.class);
            Object msgsObj = root.get("messages");
            if (!(msgsObj instanceof List<?> msgs) || msgs.isEmpty()) return "";
            for (int i = msgs.size() - 1; i >= 0; i--) {
                Object o = msgs.get(i);
                if (!(o instanceof Map<?, ?> m) || !"user".equals(String.valueOf(m.get("role")))) continue;
                Object c = m.get("content");
                if (c instanceof String s) return s;
                if (c instanceof List<?> parts) { // 多模态分段：取首个 text 分段
                    for (Object p : parts) {
                        if (p instanceof Map<?, ?> pm && "text".equals(String.valueOf(pm.get("type")))) {
                            return String.valueOf(pm.get("text"));
                        }
                    }
                }
                return "";
            }
        } catch (Exception ignore) { /* 非 JSON 请求体不提取 */ }
        return "";
    }

    /** 请求体是否声明流式（"stream": true） */
    private boolean isStreamReq(String body) {
        return body != null && body.matches("(?s).*\"stream\"\s*:\s*true.*");
    }

    /** 流式响应聚合为 OpenAI 兼容完整 JSON（choices.message.content 全量拼接 + usage），供内容日志直接解析 */
    private String buildStreamRespJson(String sseText, String model, long prompt, long completion) {
        try {
            StringBuilder content = new StringBuilder();
            String id = "", finish = "";
            for (String line : sseText.split("\\r?\\n")) {
                line = line.trim();
                if (!line.startsWith("data:")) continue;
                String payload = line.substring(5).trim();
                if (payload.isEmpty() || "[DONE]".equals(payload)) continue;
                try {
                    Map<?, ?> frame = om.readValue(payload, Map.class);
                    if (id.isEmpty() && frame.get("id") != null) id = String.valueOf(frame.get("id"));
                    List<?> choices = (List<?>) frame.get("choices");
                    if (choices != null && !choices.isEmpty() && choices.get(0) instanceof Map<?, ?> c) {
                        Object delta = c.get("delta");
                        if (delta instanceof Map<?, ?> d && d.get("content") instanceof String s) content.append(s);
                        else if (delta == null && c.get("message") instanceof Map<?, ?> msg && msg.get("content") instanceof String s) content.append(s);
                        if (c.get("finish_reason") != null) finish = String.valueOf(c.get("finish_reason"));
                    }
                } catch (Exception ignore) { /* 单帧解析失败跳过 */ }
            }
            Map<String, Object> msg = new java.util.LinkedHashMap<>();
            msg.put("role", "assistant");
            msg.put("content", content.toString());
            Map<String, Object> choice = new java.util.LinkedHashMap<>();
            choice.put("index", 0);
            choice.put("message", msg);
            choice.put("finish_reason", finish.isEmpty() ? "stop" : finish);
            Map<String, Object> usage = new java.util.LinkedHashMap<>();
            usage.put("prompt_tokens", prompt);
            usage.put("completion_tokens", completion);
            usage.put("total_tokens", prompt + completion);
            Map<String, Object> resp = new java.util.LinkedHashMap<>();
            resp.put("id", id.isEmpty() ? "relay-sse" : id);
            resp.put("object", "chat.completion");
            resp.put("model", model);
            resp.put("choices", List.of(choice));
            resp.put("usage", usage);
            resp.put("_sse_raw", "(流式响应已聚合，SSE 原始帧见 relay 转发流)");
            return om.writeValueAsString(resp);
        } catch (Exception e) {
            return sseText; // 聚合失败回退原文
        }
    }

    /* ===== 记账工具 ===== */

    /** 从响应体解析 usage（OpenAI 兼容；流式取末帧，解析不到按 0 计） */
    private long[] parseUsage(String body) {
        long prompt = 0, completion = 0;
        try {
            Matcher mp = P_PROMPT.matcher(body);
            while (mp.find()) prompt = Long.parseLong(mp.group(1));
            Matcher mc = P_COMPLETION.matcher(body);
            while (mc.find()) completion = Long.parseLong(mc.group(1));
        } catch (Exception ignore) { /* 解析失败按 0 计 */ }
        return new long[]{prompt, completion};
    }

    /* ===== 原有工具方法 ===== */

    private String normalizePath(String uri) {
        if (uri.endsWith("/")) uri = uri.substring(0, uri.length() - 1);
        return uri;
    }

    private boolean pathAllowed(String urlPathsJson, String path) {
        List<String> paths = new ArrayList<>();
        if (urlPathsJson != null && !urlPathsJson.isBlank()) {
            try {
                List<?> raw = om.readValue(urlPathsJson, List.class);
                for (Object o : raw) {
                    if (o instanceof Map<?, ?> p) {
                        Object v = p.get("path");
                        if (v != null) paths.add(String.valueOf(v));
                    }
                }
            } catch (Exception ignore) { /* 非法 JSON 走兜底 */ }
        }
        if (paths.isEmpty()) paths.add("/chat/completions");
        return paths.contains(path);
    }

    private String extractModel(String body) {
        try {
            JsonNode n = om.readTree(body);
            return n == null ? null : (n.has("model") ? n.get("model").asText() : null);
        } catch (Exception e) {
            return null;
        }
    }

    private String replaceModel(String body, String realName) {
        if (realName == null || realName.isBlank()) return body;
        try {
            ObjectNode node = (ObjectNode) om.readTree(body);
            node.put("model", realName);
            return om.writeValueAsString(node);
        } catch (Exception e) {
            return body;
        }
    }

    /** 从逗号分隔的多实例地址中轮询选一个；单地址直接返回（向后兼容） */
    private String pickBaseUrl(String baseUrlRaw) {
        String[] parts = baseUrlRaw.split(",");
        if (parts.length == 1) return parts[0].trim();
        int idx = Math.floorMod(rrCounter.getAndIncrement(), parts.length);
        return parts[idx].trim();
    }

    private String joinUrl(String baseUrl, String path) {
        String b = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        String p = path.startsWith("/") ? path : "/" + path;
        return b + p;
    }

    private void passHeader(HttpServletRequest req, HttpRequest.Builder rb, String name) {
        String v = req.getHeader(name);
        if (v != null && !v.isBlank()) rb.header(name, v);
    }

    private String headerOr(HttpServletRequest req, String name, String def) {
        String v = req.getHeader(name);
        return v == null || v.isBlank() ? def : v;
    }

    private void writeError(HttpServletResponse resp, int status, String message) throws Exception {
        resp.setStatus(status);
        resp.setContentType("application/json;charset=UTF-8");
        resp.getWriter().write(om.writeValueAsString(Map.of(
                "error", Map.of("message", message, "type", "invalid_request_error", "code", status))));
    }
}
