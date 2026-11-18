package com.zimo.genai.auth.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.Map;

/**
 * 网关平台用户体系客户端。
 *
 * 复用网关平台 jv-api-gateway-user 模块的登录/认证能力（不自建用户库）：
 * /auth/login /auth/logout /auth/info /auth/my-perms /open/auth/token/verify
 */
@Component
public class GatewayUserClient {

    private final RestClient restClient;

    public GatewayUserClient(
            @Value("${genai.gateway.user-base-url:http://localhost:9000}") String baseUrl) {
        this.restClient = RestClient.builder().baseUrl(baseUrl).build();
    }

    /** POST 调用网关用户模块接口 */
    @SuppressWarnings("unchecked")
    public Map<String, Object> post(String path, Object body, String token) {
        return (Map<String, Object>) restClient.post()
                .uri(path)
                .headers(h -> {
                    if (token != null && !token.isEmpty()) {
                        h.set("Authorization", token);
                    }
                })
                .contentType(MediaType.APPLICATION_JSON)
                .body(body)
                .retrieve()
                .body(Map.class);
    }

    /** GET 调用网关用户模块接口 */
    @SuppressWarnings("unchecked")
    public Map<String, Object> get(String path, String token) {
        return (Map<String, Object>) restClient.get()
                .uri(path)
                .headers(h -> {
                    if (token != null && !token.isEmpty()) {
                        h.set("Authorization", token);
                    }
                })
                .retrieve()
                .body(Map.class);
    }
}
