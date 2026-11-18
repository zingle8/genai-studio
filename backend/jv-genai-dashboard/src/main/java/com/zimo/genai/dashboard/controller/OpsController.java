package com.zimo.genai.dashboard.controller;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.dashboard.mapper.OpsMapper;
import org.springframework.web.bind.annotation.*;

import java.net.HttpURLConnection;
import java.net.URI;
import java.util.List;
import java.util.Map;

/** 运维中心：平台服务清单与健康探测 */
@RestController
@RequestMapping("/api/ops")
public class OpsController {

    private final OpsMapper mapper;

    public OpsController(OpsMapper mapper) { this.mapper = mapper; }

    @GetMapping("/services")
    public Result<List<Map<String, Object>>> services() {
        return Result.ok(mapper.listServices());
    }

    /** 健康探测：对单个服务发 HTTP 请求，按连通性更新状态 */
    @PostMapping("/services/{id}/check")
    public Result<Object> check(@PathVariable Long id) {
        Map<String, Object> svc = null;
        for (Map<String, Object> s : mapper.listServices()) {
            if (Long.valueOf(String.valueOf(s.get("id"))).equals(id)) { svc = s; break; }
        }
        if (svc == null) return Result.fail(404, "服务不存在");
        String status = ping(Integer.parseInt(String.valueOf(svc.get("port")))) ? "up" : "down";
        mapper.updateStatus(id, status);
        return Result.ok(Map.of("id", id, "status", status));
    }

    private boolean ping(int port) {
        try {
            HttpURLConnection conn = (HttpURLConnection) URI.create("http://127.0.0.1:" + port + "/actuator/health").toURL().openConnection();
            conn.setConnectTimeout(800);
            conn.setReadTimeout(800);
            int code = conn.getResponseCode();
            conn.disconnect();
            return code >= 200 && code < 500;
        } catch (Exception e) {
            return false;
        }
    }
}
