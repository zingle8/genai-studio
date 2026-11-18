package com.zimo.genai.comm.auth;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/**
 * 角色校验自动配置：各业务服务引入 jv-genai-comm 依赖即生效，无需手动注册。
 *
 * <p>可通过 genai.role-check.enabled=false 关闭（如本地联调）。
 */
@AutoConfiguration
@ConditionalOnProperty(name = "genai.role-check.enabled", havingValue = "true", matchIfMissing = true)
public class RoleAutoConfiguration {

    @Bean
    public RoleInterceptor roleInterceptor(
            @Value("${genai.auth.base-url:http://127.0.0.1:38081}") String authBaseUrl,
            @Value("${genai.role-check.cache-ttl-seconds:60}") long cacheTtlSeconds) {
        return new RoleInterceptor(authBaseUrl, cacheTtlSeconds);
    }

    @Bean
    public WebMvcConfigurer roleInterceptorConfigurer(RoleInterceptor roleInterceptor) {
        return new WebMvcConfigurer() {
            @Override
            public void addInterceptors(InterceptorRegistry registry) {
                registry.addInterceptor(roleInterceptor).addPathPatterns("/**");
            }
        };
    }
}
