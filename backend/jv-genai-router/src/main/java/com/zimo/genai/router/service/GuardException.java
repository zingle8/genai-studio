package com.zimo.genai.router.service;

/** 校验链异常：携带 HTTP 状态码（401 无效 Key / 402 余额不足 / 403 无权限或过期 / 429 限流） */
public class GuardException extends RuntimeException {
    private final int status;

    public GuardException(int status, String message) {
        super(message);
        this.status = status;
    }

    public int getStatus() { return status; }
}
