package com.zimo.genai.comm.auth;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 角色校验注解：标注在 Controller 方法或类上，要求请求用户具备指定角色之一。
 *
 * <p>校验链路：取请求 Authorization token → 调认证服务（jv-genai-auth → jv-api-gateway-user）
 * 换取用户角色（带 TTL 缓存）→ 角色不匹配返回 403，token 缺失/无效返回 401。
 */
@Target({ElementType.METHOD, ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
public @interface RequireRole {

    /** 允许访问的角色列表（网关平台用户体系：ADMIN / OPERATOR / VIEWER） */
    String[] value() default {"ADMIN"};
}
