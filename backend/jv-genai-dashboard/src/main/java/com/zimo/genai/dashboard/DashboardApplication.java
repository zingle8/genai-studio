package com.zimo.genai.dashboard;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 控制台/仪表盘
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-dashboard
 * 服务名：控制台/仪表盘
 */
@SpringBootApplication
public class DashboardApplication {

    public static void main(String[] args) {
        SpringApplication.run(DashboardApplication.class, args);
    }
}
