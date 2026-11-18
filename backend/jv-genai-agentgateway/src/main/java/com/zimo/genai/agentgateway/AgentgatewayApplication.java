package com.zimo.genai.agentgateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Agent 网关
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-agentgateway
 * 服务名：Agent 网关
 */
@SpringBootApplication
public class AgentgatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(AgentgatewayApplication.class, args);
    }
}
