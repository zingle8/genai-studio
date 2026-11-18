package com.zimo.genai.agentgateway.mapper;

import com.zimo.genai.agentgateway.entity.AgentEntity;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface AgentMapper {

    @Select("<script>SELECT * FROM tb_agent_info WHERE 1=1"
            + "<if test='type != null and type != &quot;&quot;'> AND type=#{type}</if>"
            + " ORDER BY id DESC LIMIT #{offset}, #{size}</script>")
    List<AgentEntity> list(@Param("type") String type, @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_agent_info WHERE 1=1"
            + "<if test='type != null and type != &quot;&quot;'> AND type=#{type}</if></script>")
    long count(@Param("type") String type);

    @Insert("INSERT INTO tb_agent_info(name, type, model, tools, description, enabled) "
            + "VALUES(#{name}, #{type}, #{model}, #{tools}, #{description}, #{enabled})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(AgentEntity e);

    @Update("<script>UPDATE tb_agent_info<set>"
            + "<if test='name != null'>name=#{name},</if>"
            + "<if test='type != null'>type=#{type},</if>"
            + "<if test='model != null'>model=#{model},</if>"
            + "<if test='tools != null'>tools=#{tools},</if>"
            + "<if test='description != null'>description=#{description},</if>"
            + "<if test='enabled != null'>enabled=#{enabled},</if>"
            + "</set>WHERE id=#{id}</script>")
    int update(AgentEntity e);

    @Delete("DELETE FROM tb_agent_info WHERE id=#{id}")
    int delete(@Param("id") Long id);
}
