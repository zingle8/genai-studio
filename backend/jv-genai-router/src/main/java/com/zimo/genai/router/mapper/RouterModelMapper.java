package com.zimo.genai.router.mapper;

import com.zimo.genai.router.entity.ModelEntity;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

/** 模型查询（转发面只读 genai_models.tb_model_info） */
@Mapper
public interface RouterModelMapper {

    /** 上架模型（供 /v1/models、/v1/model 兼容接口使用；不查 tb_api_key） */
    @Select("SELECT id, name, real_name AS realName, provider, vendor, api_format AS apiFormat, "
            + "base_url AS baseUrl, url_paths AS urlPaths, category, tier, context_len AS contextLen, status "
            + "FROM tb_model_info WHERE status = 1 ORDER BY id")
    List<ModelEntity> selectEnabled();

    @Select("SELECT id, name, real_name AS realName, provider, vendor, api_format AS apiFormat, "
            + "base_url AS baseUrl, url_paths AS urlPaths, category, tier, context_len AS contextLen, status "
            + "FROM tb_model_info WHERE id = #{id}")
    ModelEntity selectById(@Param("id") Long id);

    /** 按对外模型名查询（转发网关路由使用，含 tb_api_key） */
    @Select("SELECT id, name, real_name AS realName, provider, vendor, api_format AS apiFormat, "
            + "base_url AS baseUrl, api_key, url_paths AS urlPaths, category, tier, context_len AS contextLen, status "
            + "FROM tb_model_info WHERE name = #{name}")
    ModelEntity selectByName(@Param("name") String name);
}
