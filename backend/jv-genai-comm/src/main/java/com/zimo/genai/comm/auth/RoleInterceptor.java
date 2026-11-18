package com.zimo.genai.comm.auth;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpHeaders;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.HandlerInterceptor;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Arrays;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 角色校验拦截器：仅对标注了 {@link RequireRole} 的 Controller 方法/类生效。
 *
 * <p>角色解析：透传 token 调认证服务 /api/auth/info（jv-genai-auth → jv-api-gateway-user，
 * 由网关完成签名/过期/令牌版本/账号状态全链路校验），本地仅做角色比对与短 TTL 缓存，
 * 不在业务服务重复实现 JWT 验签。
 */
public class RoleInterceptor implements HandlerInterceptor {

    private static final Pattern ROLE_PATTERN = Pattern.compile("\"role\"\\s*:\\s*\"([^\"]+)\"");
    private static final Pattern CODE_OK_PATTERN = Pattern.compile("\"code\"\\s*:\\s*0\\b");
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(2)).build();

    private final String authBaseUrl;
    private final long ttlMs;
    private final Map<String, CacheEntry> cache = new ConcurrentHashMap<>();

    private record CacheEntry(String role, long expireAt) {}

    public RoleInterceptor(String authBaseUrl, long ttlSeconds) {
        this.authBaseUrl = authBaseUrl.replaceAll("/+$", "");
        this.ttlMs = ttlSeconds * 1000L;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        if (!(handler instanceof HandlerMethod hm)) {
            return true;
        }
        RequireRole ann = hm.getMethodAnnotation(RequireRole.class);
        if (ann == null) {
            ann = hm.getBeanType().getAnnotation(RequireRole.class);
        }
        if (ann == null) {
            return true;
        }

        String header = request.getHeader(HttpHeaders.AUTHORIZATION);
        if (header == null || header.isBlank()) {
            return reject(response, 401, "未登录，请先登录");
        }
        String token = header.startsWith("Bearer ") ? header.substring(7).trim() : header.trim();

        String role = resolveRole(token);
        if (role == null) {
            return reject(response, 401, "登录已过期或认证服务不可用");
        }
        if (!Arrays.asList(ann.value()).contains(role)) {
            return reject(response, 403, "无权限执行该操作（需 " + String.join(" / ", ann.value()) + " 角色）");
        }
        return true;
    }

    /** token → 角色（带 TTL 缓存；token 作为缓存键） */
    private String resolveRole(String token) {
        long now = System.currentTimeMillis();
        CacheEntry hit = cache.get(token);
        if (hit != null && hit.expireAt() > now) {
            return hit.role();
        }
        try {
            HttpRequest req = HttpRequest.newBuilder(URI.create(authBaseUrl + "/api/auth/info"))
                    .header(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                    .timeout(Duration.ofSeconds(3))
                    .GET().build();
            HttpResponse<String> resp = HTTP.send(req, HttpResponse.BodyHandlers.ofString());
            String body = resp.body();
            if (resp.statusCode() != 200 || body == null || !CODE_OK_PATTERN.matcher(body).find()) {
                return null;
            }
            Matcher m = ROLE_PATTERN.matcher(body);
            String role = m.find() ? m.group(1) : null;
            if (role != null) {
                cache.put(token, new CacheEntry(role, now + ttlMs));
            }
            return role;
        } catch (Exception e) {
            return null;
        }
    }

    private boolean reject(HttpServletResponse response, int status, String message) throws Exception {
        response.setStatus(status);
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write("{\"code\":" + status + ",\"message\":\"" + message + "\",\"data\":null}");
        return false;
    }
}
