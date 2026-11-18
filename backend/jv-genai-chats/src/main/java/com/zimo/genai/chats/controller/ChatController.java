package com.zimo.genai.chats.controller;

import com.zimo.genai.chats.entity.ChatMessage;
import com.zimo.genai.chats.entity.ChatSession;
import com.zimo.genai.chats.mapper.ChatMapper;
import com.zimo.genai.comm.api.Result;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 体验中心：会话与消息。
 * 消息存储按日 RANGE 分区（tb_chat_message）；区分维度：会话 > 轮次(trace_id) > 消息(model)。
 * 真实推理由前端经 jv-genai-router 直连，调用完成后批量保存消息到本服务。
 */
@RestController
@RequestMapping("/api/chats")
public class ChatController {

    private final ChatMapper mapper;

    public ChatController(ChatMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Map<String, Object>> sessions(@RequestParam(defaultValue = "1") long page,
                                                @RequestParam(defaultValue = "50") long size) {
        Map<String, Object> data = new HashMap<>();
        data.put("total", mapper.countSessions());
        data.put("list", mapper.listSessions((page - 1) * size, (int) size));
        return Result.ok(data);
    }

    @PostMapping
    public Result<ChatSession> create(@RequestBody Map<String, String> body) {
        ChatSession s = new ChatSession();
        s.setTitle(body.getOrDefault("title", "新会话"));
        s.setOwner(body.getOrDefault("owner", "admin"));
        mapper.insertSession(s);
        return Result.ok(s);
    }

    @PutMapping("/{id}")
    public Result<Object> rename(@PathVariable Long id, @RequestBody Map<String, String> body) {
        ChatSession s = new ChatSession();
        s.setId(id);
        s.setTitle(body.get("title"));
        mapper.renameSession(s);
        return Result.ok(Map.of("id", id));
    }

    @DeleteMapping("/{id}")
    public Result<Object> delete(@PathVariable Long id) {
        mapper.deleteSession(id);
        return Result.ok(Map.of("id", id));
    }

    @GetMapping("/{id}/messages")
    public Result<Object> messages(@PathVariable Long id) {
        return Result.ok(mapper.listMessages(id));
    }

    /** 发送消息（演示回复，已由前端真实调用替代，接口保留兼容） */
    @PostMapping("/{id}/messages")
    public Result<Object> send(@PathVariable Long id, @RequestBody Map<String, String> body) {
        String content = body.get("content");
        if (content == null || content.isBlank()) return Result.fail(400, "消息内容不能为空");
        ChatMessage user = new ChatMessage();
        user.setSessionId(id);
        user.setRole("user");
        user.setContent(content);
        mapper.insertMessage(user);

        ChatMessage bot = new ChatMessage();
        bot.setSessionId(id);
        bot.setRole("assistant");
        bot.setContent("（演示回复，体验中心已改为直连模型路由）已收到：「" + content + "」\n"
                + "— " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        mapper.insertMessage(bot);

        return Result.ok(List.of(user, bot));
    }

    /**
     * 批量保存一轮消息（体验中心真实调用后落库）：
     * 轮次区分 = trace_id（一次提问 + N 个模型回复共用同一 trace_id）
     * body: { messages: [{role, content, model?, traceId?, promptTokens?, completionTokens?, cost?}] }
     */
    @PostMapping("/{id}/messages/batch")
    public Result<Object> saveBatch(@PathVariable Long id, @RequestBody Map<String, Object> body) {
        Object raw = body.get("messages");
        if (!(raw instanceof List<?> list) || list.isEmpty()) return Result.fail(400, "messages 不能为空");
        for (Object o : list) {
            if (!(o instanceof Map<?, ?> m)) continue;
            ChatMessage msg = new ChatMessage();
            msg.setSessionId(id);
            msg.setRole(m.get("role") == null ? "user" : String.valueOf(m.get("role")));
            Object content = m.get("content");
            if (content == null || String.valueOf(content).isBlank()) continue;
            msg.setContent(String.valueOf(content));
            msg.setModel(m.get("model") == null ? "" : String.valueOf(m.get("model")));
            msg.setTraceId(m.get("traceId") == null ? "" : String.valueOf(m.get("traceId")));
            msg.setPromptTokens(m.get("promptTokens") instanceof Number n ? n.intValue() : 0);
            msg.setCompletionTokens(m.get("completionTokens") instanceof Number n ? n.intValue() : 0);
            msg.setDurationMs(m.get("durationMs") instanceof Number n ? n.intValue() : 0);
            msg.setCost(m.get("cost") instanceof Number n
                    ? java.math.BigDecimal.valueOf(n.doubleValue()) : java.math.BigDecimal.ZERO);
            mapper.insertMessage(msg);
        }
        return Result.ok(Map.of("saved", list.size()));
    }

    /** 按轮次查询消息（trace_id 关联一次提问与 N 个模型回复） */
    @GetMapping("/{id}/trace/{traceId}")
    public Result<Object> trace(@PathVariable Long id, @PathVariable String traceId) {
        return Result.ok(mapper.listMessagesByTrace(id, traceId));
    }
}
