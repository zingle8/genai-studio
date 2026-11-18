package com.zimo.genai.user.controller;

import com.zimo.genai.comm.api.Result;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestClient;

import java.util.Map;

/**
 * 用户/权限管理：代理网关平台 jv-api-gateway-user 的 /users、/perm/* 接口。
 * 本服务不自建用户库，仅做转发与响应归一（code 0/200 均视为成功）。
 */
@RestController
@RequestMapping("/api")
public class UserProxyController {

    @Value("${genai.gateway.user-base-url:http://localhost:28081/api}")
    private String gatewayBaseUrl;

    private RestClient client(String auth) {
        return RestClient.builder().baseUrl(gatewayBaseUrl)
                .defaultHeader(HttpHeaders.AUTHORIZATION, auth == null ? "" : auth)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();
    }

    @GetMapping("/users")
    public Result<Object> users(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String auth,
                                @RequestParam Map<String, String> query) {
        return normalize(client(auth).get().uri(u -> {
            var b = u.path("/users");
            query.forEach(b::queryParam);
            return b.build();
        }).retrieve().toEntity(new ParameterizedTypeReference<Map<String, Object>>() {}));
    }

    @GetMapping("/perms/groups")
    public Result<Object> permGroups(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String auth) {
        return normalize(client(auth).get().uri("/perm/groups")
                .retrieve().toEntity(new ParameterizedTypeReference<Map<String, Object>>() {}));
    }

    @GetMapping("/perms/dictionary")
    public Result<Object> dictionary(@RequestHeader(value = HttpHeaders.AUTHORIZATION, required = false) String auth) {
        return normalize(client(auth).get().uri("/perm/dictionary")
                .retrieve().toEntity(new ParameterizedTypeReference<Map<String, Object>>() {}));
    }

    /** 透传网关响应：code 0/200 均为成功 */
    private Result<Object> normalize(org.springframework.http.ResponseEntity<Map<String, Object>> resp) {
        Map<String, Object> body = resp.getBody();
        if (body == null) return Result.fail(502, "网关响应为空");
        Object code = body.get("code");
        boolean success = code instanceof Number n && (n.intValue() == 0 || n.intValue() == 200);
        if (!success) {
            Object msg = body.get("message");
            return Result.fail(code instanceof Number n ? n.intValue() : 502,
                    msg != null ? String.valueOf(msg) : "网关调用失败");
        }
        return Result.ok(body.get("data"));
    }
}
