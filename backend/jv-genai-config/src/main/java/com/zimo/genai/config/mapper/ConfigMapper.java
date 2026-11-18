package com.zimo.genai.config.mapper;

import com.zimo.genai.config.entity.ConfigEntity;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ConfigMapper {

    @Select("<script>SELECT * FROM tb_app_config WHERE 1=1"
            + "<if test='keyword != null and keyword != &quot;&quot;'> AND (config_key LIKE CONCAT('%',#{keyword},'%') OR remark LIKE CONCAT('%',#{keyword},'%'))</if>"
            + " ORDER BY id LIMIT #{offset}, #{size}</script>")
    List<ConfigEntity> list(@Param("keyword") String keyword, @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_app_config WHERE 1=1"
            + "<if test='keyword != null and keyword != &quot;&quot;'> AND (config_key LIKE CONCAT('%',#{keyword},'%') OR remark LIKE CONCAT('%',#{keyword},'%'))</if></script>")
    long count(@Param("keyword") String keyword);

    @Select("SELECT config_value FROM tb_app_config WHERE config_key = #{key}")
    String valueByKey(@Param("key") String key);

    @Insert("INSERT INTO tb_app_config(config_key, config_value, remark) VALUES(#{configKey}, #{configValue}, #{remark})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(ConfigEntity e);

    @Update("<script>UPDATE tb_app_config"
            + "<set>"
            + "<if test='configKey != null'>config_key = #{configKey},</if>"
            + "<if test='configValue != null'>config_value = #{configValue},</if>"
            + "<if test='remark != null'>remark = #{remark},</if>"
            + "updated_at = NOW()"
            + "</set>"
            + " WHERE id = #{id}</script>")
    int update(ConfigEntity e);

    @Delete("DELETE FROM tb_app_config WHERE id=#{id}")
    int delete(@Param("id") Long id);
}
