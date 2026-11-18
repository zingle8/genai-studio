package com.zimo.genai.dashboard.mapper;

import org.apache.ibatis.annotations.*;

import java.util.List;
import java.util.Map;

@Mapper
public interface OpsMapper {

    @Select("SELECT * FROM tb_platform_service ORDER BY port")
    List<Map<String, Object>> listServices();

    @Update("UPDATE tb_platform_service SET status=#{status}, checked_at=NOW() WHERE id=#{id}")
    int updateStatus(@Param("id") Long id, @Param("status") String status);
}
