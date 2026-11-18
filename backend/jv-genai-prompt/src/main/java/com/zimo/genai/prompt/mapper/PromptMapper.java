package com.zimo.genai.prompt.mapper;

import com.zimo.genai.prompt.entity.PromptEntity;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface PromptMapper {

    @Select("<script>SELECT * FROM tb_prompt_template WHERE 1=1"
            + "<if test='keyword != null and keyword != &quot;&quot;'> AND (name LIKE CONCAT('%',#{keyword},'%') OR tags LIKE CONCAT('%',#{keyword},'%'))</if>"
            + " ORDER BY id DESC LIMIT #{offset}, #{size}</script>")
    List<PromptEntity> list(@Param("keyword") String keyword, @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_prompt_template WHERE 1=1"
            + "<if test='keyword != null and keyword != &quot;&quot;'> AND (name LIKE CONCAT('%',#{keyword},'%') OR tags LIKE CONCAT('%',#{keyword},'%'))</if></script>")
    long count(@Param("keyword") String keyword);

    @Insert("INSERT INTO tb_prompt_template(name, content, variables, tags, status) "
            + "VALUES(#{name}, #{content}, #{variables}, #{tags}, #{status})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(PromptEntity e);

    @Update("<script>UPDATE tb_prompt_template<set>"
            + "<if test='name != null'>name=#{name},</if>"
            + "<if test='content != null'>content=#{content},</if>"
            + "<if test='variables != null'>variables=#{variables},</if>"
            + "<if test='tags != null'>tags=#{tags},</if>"
            + "<if test='status != null'>status=#{status},</if>"
            + "</set>WHERE id=#{id}</script>")
    int update(PromptEntity e);

    @Delete("DELETE FROM tb_prompt_template WHERE id=#{id}")
    int delete(@Param("id") Long id);
}
