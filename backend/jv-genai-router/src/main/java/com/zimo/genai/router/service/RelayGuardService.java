package com.zimo.genai.router.service;

import com.zimo.genai.router.mapper.RelayGuardMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 转发校验链：鉴权 → 余额 → 限流（RPM/TPM/CC 双写：Redis 优先 + MySQL 双记录）→ 计费/日志
 *
 * 限流说明：
 * - RPM / TPM：按 Key 固定 1 分钟窗口计数；每次计数双写 Redis（优先读写）+ MySQL
 *   （genai_billing.tb_rate_limit_counter）；Redis 不可用时自动降级读 MySQL（熔断冷却 30s）
 * - TPM 在转发前按请求体大小估算 token（字节数/4），转发后按实际用量回补差额（双写）
 * - CC：Redis 计数优先（TTL 300s 防泄漏），Redis 不可用降级进程内 Semaphore
 * - 配置为 null = 该项不限制
 */
@Service
public class RelayGuardService {

    private static final Logger log = LoggerFactory.getLogger(RelayGuardService.class);

    private final RelayGuardMapper mapper;
    private final RedisRateLimitStore redisStore;

    public RelayGuardService(RelayGuardMapper mapper, RedisRateLimitStore redisStore) {
        this.mapper = mapper;
        this.redisStore = redisStore;
    }

    /** 校验通过的 Key 信息 */
    public static class AuthKey {
        public String name;
        public String keyId;
        public Integer rpm;
        public Integer tpm;
        public Integer cc;
    }

    /** acquire 结果：release 时按此回补（记录 cc 降级路径与 TPM 预扣值/窗口） */
    public static class Ticket {
        boolean ccViaLocal = false; // 并发占位走的进程内 Semaphore（Redis 不可用降级）
        int estimatedTokens = 0;    // TPM 预扣估算值
        long minute = 0;            // acquire 时的窗口（epoch 分钟）
    }

    /* ================= 鉴权 ================= */

    /** 解析并校验 API Key（Bearer 头）；失败抛 GuardException(401/403) */
    public AuthKey authenticate(String authorization, String model) {
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            throw new GuardException(401, "缺少 API Key（请求头 Authorization: Bearer sk-...）");
        }
        String rawKey = authorization.substring(7).trim();
        if (rawKey.isEmpty()) {
            throw new GuardException(401, "API Key 为空");
        }
        Map<String, Object> row = mapper.selectApiKey(rawKey);
        if (row == null) {
            throw new GuardException(401, "无效的 API Key");
        }
        Object expiry = row.get("expiryDate");
        if (expiry != null && !String.valueOf(expiry).isBlank()) {
            try {
                if (LocalDate.parse(String.valueOf(expiry)).isBefore(LocalDate.now())) {
                    throw new GuardException(403, "API Key 已过期: " + row.get("keyId"));
                }
            } catch (DateTimeParseException ignore) { /* 非法日期视为永久有效 */ }
        }
        Object models = row.get("models");
        if (models != null && !String.valueOf(models).isBlank()) {
            List<String> allowed = Arrays.asList(String.valueOf(models).split("\\s*,\\s*"));
            if (!allowed.contains(model)) {
                throw new GuardException(403, "API Key 未授权访问模型: " + model);
            }
        }
        AuthKey key = new AuthKey();
        key.name = String.valueOf(row.getOrDefault("name", ""));
        key.keyId = String.valueOf(row.getOrDefault("keyId", ""));
        key.rpm = toInt(row.get("rpm"));
        key.tpm = toInt(row.get("tpm"));
        key.cc = toInt(row.get("cc"));
        return key;
    }

    /* ================= 余额 ================= */

    /** 余额 ≤ 0 拒绝（402） */
    public void checkBalance() {
        BigDecimal balance = mapper.getBalance();
        if (balance == null || balance.compareTo(BigDecimal.ZERO) <= 0) {
            throw new GuardException(402, "账户余额不足，请充值后再调用模型");
        }
    }

    /* ================= 限流（Redis 优先 + MySQL 双记录） ================= */

    private static class Window {
        final long minute;
        final AtomicLong requests = new AtomicLong();
        final AtomicLong tokens = new AtomicLong();

        Window(long minute) { this.minute = minute; }
    }

    private final ConcurrentHashMap<String, Window> windows = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Semaphore> concurrency = new ConcurrentHashMap<>();

    /** MySQL 窗口计数双写（delta 可负） */
    private void mysqlIncr(String keyId, long minute, int req, long tok, int cc) {
        try {
            mapper.incrCounter(keyId, minute, req, tok, cc);
        } catch (Exception e) {
            log.warn("[ratelimit] MySQL 计数双写失败: {}", e.getMessage());
        }
    }

    /** 转发前限流：cc 占位 → rpm 窗口 → tpm 预扣；超限抛 429（内部自动回滚已占用量） */
    public Ticket acquire(AuthKey key, int estimatedTokens) {
        Ticket t = new Ticket();
        t.estimatedTokens = estimatedTokens;
        t.minute = currentMinute();

        // CC：Redis 优先；不可用降级进程内 Semaphore
        if (key.cc != null) {
            long cur = redisStore.incrConcurrency(key.keyId);
            if (cur == RedisRateLimitStore.FAIL) {
                Semaphore sem = concurrency.computeIfAbsent(key.keyId, k -> new Semaphore(key.cc));
                if (!sem.tryAcquire()) {
                    throw new GuardException(429, "并发数已达上限(" + key.cc + ")，请稍后重试");
                }
                t.ccViaLocal = true;
            } else if (cur > key.cc) {
                redisStore.decrConcurrency(key.keyId);
                mysqlIncr(key.keyId, t.minute, 0, 0, -1);
                throw new GuardException(429, "并发数已达上限(" + key.cc + ")，请稍后重试");
            } else {
                mysqlIncr(key.keyId, t.minute, 0, 0, 1); // 双记录
            }
        }

        // RPM：双写（Redis 优先读，失败降级读 MySQL 双记录）
        long reqCnt = redisStore.incrRequests(key.keyId, t.minute);
        mysqlIncr(key.keyId, t.minute, 1, 0, 0);
        if (reqCnt == RedisRateLimitStore.FAIL) {
            Long v = mapper.selectRequests(key.keyId, t.minute);
            reqCnt = v == null ? 1 : v;
        }
        if (key.rpm != null && reqCnt > key.rpm) {
            releaseQuietly(key, t);
            throw new GuardException(429, "请求频率超限(RPM=" + key.rpm + ")，请稍后重试");
        }

        // TPM：预扣估算值（双写）
        if (key.tpm != null && estimatedTokens > 0) {
            long tokCnt = redisStore.incrTokens(key.keyId, t.minute, estimatedTokens);
            mysqlIncr(key.keyId, t.minute, 0, estimatedTokens, 0);
            if (tokCnt == RedisRateLimitStore.FAIL) {
                Long v = mapper.selectTokens(key.keyId, t.minute);
                tokCnt = v == null ? estimatedTokens : v;
            }
            if (tokCnt > key.tpm) {
                releaseQuietly(key, t);
                throw new GuardException(429, "Token 用量超限(TPM=" + key.tpm + ")，请稍后重试");
            }
        }
        return t;
    }

    /** 转发后释放：cc 占位 -1；tpm 窗口按实际用量修正估算差额（双写） */
    public void release(AuthKey key, Ticket t, long actualTotalTokens) {
        if (key.cc != null) {
            if (t.ccViaLocal) {
                Semaphore sem = concurrency.get(key.keyId);
                if (sem != null) sem.release();
            } else {
                redisStore.decrConcurrency(key.keyId);
                mysqlIncr(key.keyId, t.minute, 0, 0, -1);
            }
        }
        long delta = actualTotalTokens - t.estimatedTokens;
        if (key.tpm != null && delta != 0) {
            redisStore.incrTokens(key.keyId, t.minute, delta);
            mysqlIncr(key.keyId, t.minute, 0, delta, 0);
        }
    }

    /** 异常路径释放（不修正 tpm 差额） */
    public void release(AuthKey key, Ticket t) {
        release(key, t, t.estimatedTokens);
    }

    /** acquire 内部超限时的静默回滚 */
    private void releaseQuietly(AuthKey key, Ticket t) {
        try {
            release(key, t, t.estimatedTokens);
        } catch (Exception ignore) { /* 回滚失败不影响主流程 */ }
    }

    private long currentMinute() {
        return System.currentTimeMillis() / 60_000;
    }

    /* ================= 计费 / 日志 ================= */

    /**
     * 转发完成后记账：等级单价 × token 用量 → 扣余额 + 写 tb_usage_log + tb_cost_daily 聚合。
     * 返回本次调用的 trace_id（tb_usage_log 主索引），供 tb_relay_log 内容日志对齐同一 trace；
     * 记账失败仅告警并返回 null，不影响已透传的响应。
     */
    public String recordUsage(AuthKey key, String model, String tier, long promptTokens,
                              long completionTokens, long durationMs, String status, String ip) {
        String traceId = UUID.randomUUID().toString();
        try {
            Map<String, Object> p = mapper.selectPriceByTier(tier == null || tier.isBlank() ? "标准" : tier);
            BigDecimal priceIn = p == null ? BigDecimal.ZERO : toDecimal(p.get("priceIn"));
            BigDecimal priceOut = p == null ? BigDecimal.ZERO : toDecimal(p.get("priceOut"));
            BigDecimal cost = priceIn.multiply(BigDecimal.valueOf(promptTokens)).movePointLeft(3)
                    .add(priceOut.multiply(BigDecimal.valueOf(completionTokens)).movePointLeft(3))
                    .setScale(4, RoundingMode.HALF_UP);

            if (cost.compareTo(BigDecimal.ZERO) > 0) {
                mapper.deductBalance(cost);
            }
            long total = promptTokens + completionTokens;
            mapper.insertUsageLog(traceId, key.keyId, key.name, model,
                    "jv-genai-router", (int) Math.min(promptTokens, Integer.MAX_VALUE),
                    (int) Math.min(completionTokens, Integer.MAX_VALUE),
                    (int) Math.min(total, Integer.MAX_VALUE), cost,
                    (int) Math.min(durationMs, Integer.MAX_VALUE), status, ip);
            upsertCostDaily(model, total, cost);
            log.info("[billing] trace={} model={} tier={} tokens={}/{} cost={} key={}",
                    traceId, model, tier, promptTokens, completionTokens, cost, key.keyId);
            return traceId;
        } catch (Exception e) {
            log.warn("[billing] 记账失败（不影响响应）: {}", e.getMessage());
            return traceId; // 记账失败仍返回 traceId，内容日志保持可关联
        }
    }

    private void upsertCostDaily(String model, long tokens, BigDecimal cost) {
        Map<String, Object> row = mapper.selectCostDaily(model, "jv-genai-router");
        if (row != null) {
            mapper.updateCostDaily(((Number) row.get("id")).longValue(), 1, tokens, cost);
        } else {
            mapper.insertCostDaily(model, "jv-genai-router", 1, tokens, cost);
        }
    }

    /* ================= 工具 ================= */

    private Integer toInt(Object v) {
        if (v == null) return null;
        try { return Integer.parseInt(String.valueOf(v)); } catch (NumberFormatException e) { return null; }
    }

    private BigDecimal toDecimal(Object v) {
        if (v == null) return BigDecimal.ZERO;
        try { return new BigDecimal(String.valueOf(v)); } catch (NumberFormatException e) { return BigDecimal.ZERO; }
    }
}
