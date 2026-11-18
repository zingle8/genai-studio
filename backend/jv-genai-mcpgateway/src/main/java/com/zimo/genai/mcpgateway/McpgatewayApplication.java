package com.zimo.genai.mcpgateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * MCP 网关
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-mcpgateway
 * 服务名：MCP 网关
 */
@SpringBootApplication
public class McpgatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(McpgatewayApplication.class, args);
    }
}
