package com.zimo.genai.user;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 用户服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-user
 * 服务名：用户服务
 */
@SpringBootApplication
public class UserApplication {

    public static void main(String[] args) {
        SpringApplication.run(UserApplication.class, args);
    }
}
