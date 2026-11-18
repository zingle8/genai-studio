package com.zimo.genai.billing.controller;

import com.zimo.genai.billing.entity.BillingOrder;
import com.zimo.genai.billing.mapper.BillingMapper;
import com.zimo.genai.comm.api.Result;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.YearMonth;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 计费服务：余额、充值、账单/订单查询
 */
@RestController
@RequestMapping("/api/billing")
public class BillingController {

    private final BillingMapper mapper;

    public BillingController(BillingMapper mapper) {
        this.mapper = mapper;
    }

    /** 汇总：余额 + 本月消费/充值 + 今日消费 */
    @GetMapping("/summary")
    public Result<Map<String, Object>> summary() {
        String monthStart = YearMonth.now().atDay(1).atStartOfDay()
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("balance", mapper.getBalance());
        data.put("monthConsume", mapper.monthConsume(monthStart));
        data.put("monthTopup", mapper.monthTopup(monthStart));
        data.put("todayConsume", mapper.todayConsume());
        return Result.ok(data);
    }

    /** 账单/订单列表 */
    @GetMapping("/orders")
    public Result<Map<String, Object>> orders(
            @RequestParam(required = false) String type,
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "20") long size) {

        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.countOrders(type));
        data.put("list", mapper.listOrders(type, (page - 1) * size, (int) size));
        return Result.ok(data);
    }

    /** 充值渠道白名单（alipay/wechat/bank_card/balance） */
    private static final java.util.Set<String> CHANNELS = java.util.Set.of("alipay", "wechat", "bank_card", "balance");

    /**
     * 充值（模拟支付）：提交充值仅保存支付记录并即时入账，不接真实支付渠道。
     * 生产环境应改为：创建待支付订单 → 渠道收银台 → 支付回调入账。
     */
    @PostMapping("/topup")
    @Transactional
    public Result<Object> topup(@RequestBody Map<String, Object> body) {
        BigDecimal amount = body.get("amount") instanceof Number n && n.doubleValue() > 0
                ? BigDecimal.valueOf(n.doubleValue()).setScale(2, java.math.RoundingMode.HALF_UP) : null;
        if (amount == null) {
            return Result.fail(400, "充值金额必须大于 0");
        }
        if (amount.doubleValue() > 1000000) {
            return Result.fail(400, "单笔充值金额不能超过 1,000,000 元");
        }
        String channel = str(body.get("channel"), "balance");
        if (!CHANNELS.contains(channel)) {
            return Result.fail(400, "不支持的支付渠道: " + channel + "（可选 alipay/wechat/bank_card/balance）");
        }

        // 模拟支付成功：余额入账 + 保存充值记录
        mapper.changeBalance(amount);

        BillingOrder order = new BillingOrder();
        order.setOrderNo("R" + LocalDateTime.now()
                .format(DateTimeFormatter.ofPattern("yyyyMMddHHmmssSSS"))
                + String.format("%03d", java.util.concurrent.ThreadLocalRandom.current().nextInt(1000)));
        order.setType("topup");
        order.setAmount(amount);
        order.setBalanceAfter(mapper.getBalance());
        order.setChannel(channel);
        order.setStatus("success");
        String channelName = switch (channel) {
            case "alipay" -> "支付宝充值";
            case "wechat" -> "微信支付充值";
            case "bank_card" -> "银行卡充值";
            default -> "对公转账充值";
        };
        order.setRemark(str(body.get("remark"), channelName + "（模拟支付，已即时到账）"));
        mapper.insertOrder(order);
        return Result.ok(order);
    }

    /** 充值记录（渠道 / 时间区间筛选，分页） */
    @GetMapping("/recharges")
    public Result<Map<String, Object>> recharges(
            @RequestParam(required = false) String channel,
            @RequestParam(required = false) String from,
            @RequestParam(required = false) String to,
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "20") long size) {
        if (from != null && to != null && from.compareTo(to) > 0) {
            return Result.fail(400, "时间区间无效（from 晚于 to）");
        }
        return Result.ok(paged("topup", channel, from, to, page, size));
    }

    /** 消费账单（时间区间筛选，分页） */
    @GetMapping("/consumes")
    public Result<Map<String, Object>> consumes(
            @RequestParam(required = false) String from,
            @RequestParam(required = false) String to,
            @RequestParam(defaultValue = "1") long page,
            @RequestParam(defaultValue = "20") long size) {
        if (from != null && to != null && from.compareTo(to) > 0) {
            return Result.fail(400, "时间区间无效（from 晚于 to）");
        }
        return Result.ok(paged("consume", null, from, to, page, size));
    }

    /** 充值渠道统计（笔数 / 金额，可选时间区间） */
    @GetMapping("/channel-stats")
    public Result<Object> channelStats(@RequestParam(required = false) String from,
                                       @RequestParam(required = false) String to) {
        return Result.ok(mapper.channelStats(from, to));
    }

    /** 按月账单汇总（各月充值 / 消费笔数与金额） */
    @GetMapping("/monthly")
    public Result<Object> monthly(@RequestParam(required = false) String from,
                                  @RequestParam(required = false) String to) {
        // 按月分组后合并为 [{month, topupTotal, topupCount, consumeTotal, consumeCount, net}]
        Map<String, Map<String, Object>> byMonth = new LinkedHashMap<>();
        for (Map<String, Object> row : mapper.monthlyStats(from, to)) {
            String month = String.valueOf(row.get("month"));
            String type = String.valueOf(row.get("type"));
            Map<String, Object> m = byMonth.computeIfAbsent(month, k -> {
                Map<String, Object> x = new LinkedHashMap<>();
                x.put("month", k);
                x.put("topupTotal", 0.0); x.put("topupCount", 0L);
                x.put("consumeTotal", 0.0); x.put("consumeCount", 0L);
                return x;
            });
            double total = row.get("total") instanceof Number n ? n.doubleValue() : 0;
            long count = row.get("count") instanceof Number n ? n.longValue() : 0;
            if ("topup".equals(type)) {
                m.put("topupTotal", total); m.put("topupCount", count);
            } else {
                m.put("consumeTotal", total); m.put("consumeCount", count);
            }
        }
        java.util.List<Map<String, Object>> list = new java.util.ArrayList<>(byMonth.values());
        for (Map<String, Object> m : list) {
            double t = (double) m.get("topupTotal"), c = (double) m.get("consumeTotal");
            m.put("net", Math.round((t - c) * 100.0) / 100.0);
        }
        return Result.ok(list);
    }

    /* ===== 工具方法 ===== */

    private Map<String, Object> paged(String type, String channel, String from, String to, long page, long size) {
        size = Math.min(Math.max(size, 1), 100);
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.countRange(type, channel, from, to));
        data.put("list", mapper.listRange(type, channel, from, to, (page - 1) * size, (int) size));
        return data;
    }

    private String str(Object v, String def) {
        return v == null || v.toString().trim().isEmpty() ? def : v.toString().trim();
    }
}
