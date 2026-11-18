package com.zimo.genai.apikey;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * API 密钥服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-apikey
 * 服务名：API 密钥服务
 */
@SpringBootApplication
public class ApikeyApplication {

    public static void main(String[] args) {
        SpringApplication.run(ApikeyApplication.class, args);
    }
}
