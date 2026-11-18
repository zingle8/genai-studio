package com.zimo.genai.aigateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * AI 网关
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-aigateway
 * 服务名：AI 网关
 */
@SpringBootApplication
public class AigatewayApplication {

    public static void main(String[] args) {
        SpringApplication.run(AigatewayApplication.class, args);
    }
}
