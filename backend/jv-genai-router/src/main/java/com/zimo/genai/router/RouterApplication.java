package com.zimo.genai.router;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 模型路由转发服务
 *
 * 职责（与 jv-genai-models 管理面分离）：
 *  1. OpenAI 兼容模型列表：GET /v1/models、GET /v1/model（及 /{id}）
 *  2. 模型消息转发：按模型配置（base_url + 真实模型名 + API Key + 请求格式）
 *     将用户请求转发到上游，支持流式透传
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-router
 * 服务名：模型路由转发服务
 */
@SpringBootApplication
public class RouterApplication {

    public static void main(String[] args) {
        SpringApplication.run(RouterApplication.class, args);
    }
}
