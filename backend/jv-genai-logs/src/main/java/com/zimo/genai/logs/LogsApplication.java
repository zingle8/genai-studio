package com.zimo.genai.logs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 日志服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-logs
 * 服务名：日志服务
 */
@SpringBootApplication
public class LogsApplication {

    public static void main(String[] args) {
        SpringApplication.run(LogsApplication.class, args);
    }
}
