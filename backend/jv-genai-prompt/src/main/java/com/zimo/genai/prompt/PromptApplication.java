package com.zimo.genai.prompt;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 提示词服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-prompt
 * 服务名：提示词服务
 */
@SpringBootApplication
public class PromptApplication {

    public static void main(String[] args) {
        SpringApplication.run(PromptApplication.class, args);
    }
}
