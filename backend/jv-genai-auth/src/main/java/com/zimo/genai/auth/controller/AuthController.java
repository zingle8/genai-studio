package com.zimo.genai.auth.controller;

import com.zimo.genai.auth.client.GatewayUserClient;
import com.zimo.genai.comm.api.Result;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 认证授权服务：网关平台用户体系对接层。
 *
 * 登录/注册/登出统一转发到网关平台 jv-api-gateway-user（应用 ID：app-genai-studio），
 * 本服务不自建用户库，只做会话适配与 token 透传。
 */
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final GatewayUserClient gatewayUserClient;

    public AuthController(GatewayUserClient gatewayUserClient) {
        this.gatewayUserClient = gatewayUserClient;
    }

    /** 登录（转发网关 /auth/login） */
    @PostMapping("/login")
    public Result<Object> login(@RequestBody Map<String, Object> body) {
        return normalize(gatewayUserClient.post("/auth/login", body, null));
    }

    /** 注册（转发网关 /auth/register） */
    @PostMapping("/register")
    public Result<Object> register(@RequestBody Map<String, Object> body) {
        return normalize(gatewayUserClient.post("/auth/register", body, null));
    }

    /** 登出（透传 token 转发网关 /auth/logout） */
    @PostMapping("/logout")
    public Result<Object> logout(@RequestHeader(value = "Authorization", required = false) String token) {
        return normalize(gatewayUserClient.post("/auth/logout", Map.of(), token));
    }

    /** 当前用户信息（透传 token 转发网关 /auth/info） */
    @GetMapping("/info")
    public Result<Object> info(@RequestHeader(value = "Authorization", required = false) String token) {
        return normalize(gatewayUserClient.get("/auth/info", token));
    }

    /** 当前用户权限（透传 token 转发网关 /auth/my-perms） */
    @GetMapping("/my-perms")
    public Result<Object> myPerms(@RequestHeader(value = "Authorization", required = false) String token) {
        return normalize(gatewayUserClient.get("/auth/my-perms", token));
    }

    /** 归一化网关响应：取 data 字段回传给前端 */
    private Result<Object> normalize(Map<String, Object> resp) {
        if (resp == null) {
            return Result.fail(500, "网关平台用户服务无响应");
        }
        Object code = resp.get("code");
        // 网关平台响应约定：code=0 或 200 均为成功
        boolean success = code instanceof Integer c && (c == 0 || c == 200);
        if (!success) {
            Object msg = resp.get("message");
            return Result.fail(code instanceof Integer c2 ? c2 : 500,
                    msg != null ? String.valueOf(msg) : "网关认证失败");
        }
        Object data = resp.get("data");
        return Result.ok(data != null ? data : resp);
    }
}
