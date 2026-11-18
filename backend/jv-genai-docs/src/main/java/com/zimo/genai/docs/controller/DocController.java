package com.zimo.genai.docs.controller;

import com.zimo.genai.comm.api.Result;
import com.zimo.genai.docs.mapper.DocMapper;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/** 接口文档：平台开放 API 清单 */
@RestController
@RequestMapping("/api/docs")
public class DocController {

    private final DocMapper mapper;

    public DocController(DocMapper mapper) { this.mapper = mapper; }

    @GetMapping
    public Result<Object> list() {
        return Result.ok(mapper.listAll());
    }
}
