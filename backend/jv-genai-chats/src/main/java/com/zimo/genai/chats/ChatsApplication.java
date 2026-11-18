package com.zimo.genai.chats;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 会话对话服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-chats
 * 服务名：会话对话服务
 */
@SpringBootApplication
public class ChatsApplication {

    public static void main(String[] args) {
        SpringApplication.run(ChatsApplication.class, args);
    }
}
