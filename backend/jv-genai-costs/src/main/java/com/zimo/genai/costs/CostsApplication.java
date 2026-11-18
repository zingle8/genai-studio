package com.zimo.genai.costs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * 成本核算服务
 *
 * 网关平台接入信息：
 * 应用 ID：app-genai-studio
 * 服务 ID：jv-genai-costs
 * 服务名：成本核算服务
 */
@SpringBootApplication
public class CostsApplication {

    public static void main(String[] args) {
        SpringApplication.run(CostsApplication.class, args);
    }
}
