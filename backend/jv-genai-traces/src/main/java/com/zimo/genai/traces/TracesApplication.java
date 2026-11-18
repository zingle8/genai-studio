package com.zimo.genai.traces;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 链路追踪服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-traces
 * 服务名：链路追踪服务
 */
@SpringBootApplication
public class TracesApplication {

    public static void main(String[] args) {
        SpringApplication.run(TracesApplication.class, args);
    }
}
