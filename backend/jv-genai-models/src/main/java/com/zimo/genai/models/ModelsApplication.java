package com.zimo.genai.models;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 模型管理服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-models
 * 服务名：模型管理服务
 */
@SpringBootApplication
public class ModelsApplication {

    public static void main(String[] args) {
        SpringApplication.run(ModelsApplication.class, args);
    }
}
