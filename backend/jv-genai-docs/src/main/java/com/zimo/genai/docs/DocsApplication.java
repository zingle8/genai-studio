package com.zimo.genai.docs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 文档服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-docs
 * 服务名：文档服务
 */
@SpringBootApplication
public class DocsApplication {

    public static void main(String[] args) {
        SpringApplication.run(DocsApplication.class, args);
    }
}
