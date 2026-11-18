package com.zimo.genai.docs.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Map;

@Mapper
public interface DocMapper {

    @Select("SELECT * FROM tb_api_doc ORDER BY module, id")
    List<Map<String, Object>> listAll();
}
