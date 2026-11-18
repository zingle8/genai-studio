package com.zimo.genai.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 应用服务（门户）
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-app
 * 服务名：应用服务（门户）
 */
@SpringBootApplication
public class AppApplication {

    public static void main(String[] args) {
        SpringApplication.run(AppApplication.class, args);
    }
}
