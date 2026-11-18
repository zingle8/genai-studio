package com.zimo.genai.mcpgateway.mapper;

import com.zimo.genai.mcpgateway.entity.McpServerEntity;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface McpServerMapper {

    @Select("SELECT * FROM tb_mcp_server ORDER BY id DESC LIMIT #{offset}, #{size}")
    List<McpServerEntity> list(@Param("offset") long offset, @Param("size") int size);

    @Select("SELECT COUNT(*) FROM tb_mcp_server")
    long count();

    @Insert("INSERT INTO tb_mcp_server(name, endpoint, auth_type, status, remark) "
            + "VALUES(#{name}, #{endpoint}, #{authType}, #{status}, #{remark})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(McpServerEntity e);

    @Update("<script>UPDATE tb_mcp_server<set>"
            + "<if test='name != null'>name=#{name},</if>"
            + "<if test='endpoint != null'>endpoint=#{endpoint},</if>"
            + "<if test='authType != null'>auth_type=#{authType},</if>"
            + "<if test='status != null'>status=#{status},</if>"
            + "<if test='remark != null'>remark=#{remark},</if>"
            + "</set>WHERE id=#{id}</script>")
    int update(McpServerEntity e);

    @Delete("DELETE FROM tb_mcp_server WHERE id=#{id}")
    int delete(@Param("id") Long id);
}
