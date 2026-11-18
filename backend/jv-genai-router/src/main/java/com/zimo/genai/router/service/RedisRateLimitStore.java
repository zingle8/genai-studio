package com.zimo.genai.router.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.Duration;

/**
 * Redis 限流计数存取（优先数据源）。
 * 异常驱动熔断：操作失败即标记不可用并冷却 30s，期间调用方直接走 MySQL 双记录；
 * 冷却结束后自动重试恢复。key 约定：
 *   relay:rl:req:{keyId}:{minute}  RPM 窗口计数（TTL 120s）
 *   relay:rl:tok:{keyId}:{minute}  TPM 窗口计数（TTL 120s，允许负值回补）
 *   relay:cc:{keyId}               并发占位数（TTL 300s 防泄漏）
 */
@Service
public class RedisRateLimitStore {

    public static final long FAIL = Long.MIN_VALUE; // 操作失败标记（降级信号）
    private static final long COOLDOWN_MS = 30_000;
    private static final Logger log = LoggerFactory.getLogger(RedisRateLimitStore.class);

    private final StringRedisTemplate redis;
    private volatile long downUntil = 0;

    public RedisRateLimitStore(StringRedisTemplate redis) {
        this.redis = redis;
    }

    /** Redis 是否可用（冷却期外即视为可尝试） */
    public boolean isUp() {
        return System.currentTimeMillis() >= downUntil;
    }

    /** RPM 窗口 +1，返回窗口内请求数；失败返回 FAIL */
    public long incrRequests(String keyId, long minute) {
        String key = "relay:rl:req:" + keyId + ":" + minute;
        try {
            Long v = redis.opsForValue().increment(key);
            redis.expire(key, Duration.ofSeconds(120));
            return v == null ? 0 : v;
        } catch (Exception e) {
            return fail(e);
        }
    }

    /** TPM 窗口累加 delta（可为负），返回窗口内 token 数；失败返回 FAIL */
    public long incrTokens(String keyId, long minute, long delta) {
        String key = "relay:rl:tok:" + keyId + ":" + minute;
        try {
            Long v = redis.opsForValue().increment(key, delta);
            redis.expire(key, Duration.ofSeconds(120));
            return v == null ? 0 : v;
        } catch (Exception e) {
            return fail(e);
        }
    }

    /** 并发占位 +1，返回当前占位数；失败返回 FAIL */
    public long incrConcurrency(String keyId) {
        String key = "relay:cc:" + keyId;
        try {
            Long v = redis.opsForValue().increment(key);
            redis.expire(key, Duration.ofSeconds(300));
            return v == null ? 0 : v;
        } catch (Exception e) {
            return fail(e);
        }
    }

    /** 并发占位 -1；失败返回 FAIL */
    public long decrConcurrency(String keyId) {
        try {
            Long v = redis.opsForValue().decrement("relay:cc:" + keyId);
            return v == null ? FAIL : v;
        } catch (Exception e) {
            return fail(e);
        }
    }

    private long fail(Exception e) {
        downUntil = System.currentTimeMillis() + COOLDOWN_MS;
        log.warn("[ratelimit] Redis 不可用，30s 内降级 MySQL 双记录: {}", e.getMessage());
        return FAIL;
    }
}
