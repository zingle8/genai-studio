package com.zimo.genai.models.mapper;

import com.zimo.genai.models.entity.ModelEntity;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ModelMapper {

    @Select("<script>SELECT * FROM tb_model_info WHERE 1=1"
            + "<if test='keyword != null and keyword != &quot;&quot;'> AND (name LIKE CONCAT('%',#{keyword},'%') OR provider LIKE CONCAT('%',#{keyword},'%') OR vendor LIKE CONCAT('%',#{keyword},'%') OR real_name LIKE CONCAT('%',#{keyword},'%'))</if>"
            + "<if test='provider != null and provider != &quot;&quot;'> AND provider = #{provider}</if>"
            + "<if test='vendor != null and vendor != &quot;&quot;'> AND vendor = #{vendor}</if>"
            + "<if test='category != null and category != &quot;&quot;'> AND category = #{category}</if>"
            + "<if test='tier != null and tier != &quot;&quot;'> AND tier = #{tier}</if>"
            + "<if test='status != null'> AND status = #{status}</if>"
            + " ORDER BY id DESC LIMIT #{offset}, #{size}</script>")
    List<ModelEntity> list(@Param("keyword") String keyword, @Param("provider") String provider,
                           @Param("vendor") String vendor, @Param("category") String category,
                           @Param("tier") String tier, @Param("status") Integer status,
                           @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_model_info WHERE 1=1"
            + "<if test='keyword != null and keyword != &quot;&quot;'> AND (name LIKE CONCAT('%',#{keyword},'%') OR provider LIKE CONCAT('%',#{keyword},'%') OR vendor LIKE CONCAT('%',#{keyword},'%') OR real_name LIKE CONCAT('%',#{keyword},'%'))</if>"
            + "<if test='provider != null and provider != &quot;&quot;'> AND provider = #{provider}</if>"
            + "<if test='vendor != null and vendor != &quot;&quot;'> AND vendor = #{vendor}</if>"
            + "<if test='category != null and category != &quot;&quot;'> AND category = #{category}</if>"
            + "<if test='tier != null and tier != &quot;&quot;'> AND tier = #{tier}</if>"
            + "<if test='status != null'> AND status = #{status}</if></script>")
    long count(@Param("keyword") String keyword, @Param("provider") String provider,
               @Param("vendor") String vendor, @Param("category") String category,
               @Param("tier") String tier, @Param("status") Integer status);


    @Select("SELECT id, name, real_name AS realName, provider, vendor, api_format AS apiFormat, base_url AS baseUrl, url_paths AS urlPaths, category, tier, context_len AS contextLen, status FROM tb_model_info WHERE id = #{id}")
    ModelEntity selectById(@Param("id") Long id);


    @Insert("INSERT INTO tb_model_info(name, real_name, provider, vendor, api_format, base_url, api_key, url_paths, category, tier, context_len, status, description, detail) "
            + "VALUES(#{name}, #{realName}, #{provider}, #{vendor}, #{apiFormat}, #{baseUrl}, #{apiKey}, #{urlPaths}, #{category}, #{tier}, #{contextLen}, #{status}, #{description}, #{detail})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(ModelEntity e);

    @Update("<script>UPDATE tb_model_info<set>"
            + "<if test='name != null'>name=#{name},</if>"
            + "<if test='realName != null'>real_name=#{realName},</if>"
            + "<if test='provider != null'>provider=#{provider},</if>"
            + "<if test='vendor != null'>vendor=#{vendor},</if>"
            + "<if test='apiFormat != null'>api_format=#{apiFormat},</if>"
            + "<if test='baseUrl != null'>base_url=#{baseUrl},</if>"
            + "<if test='apiKey != null and apiKey != &quot;&quot;'>api_key=#{apiKey},</if>"
            + "<if test='urlPaths != null'>url_paths=#{urlPaths},</if>"
            + "<if test='category != null'>category=#{category},</if>"
            + "<if test='tier != null'>tier=#{tier},</if>"
            + "<if test='contextLen != null'>context_len=#{contextLen},</if>"
            + "<if test='status != null'>status=#{status},</if>"
            + "<if test='description != null'>description=#{description},</if>"
            + "<if test='detail != null'>detail=#{detail},</if>"
            + "</set>WHERE id=#{id}</script>")
    int update(ModelEntity e);

    @Delete("DELETE FROM tb_model_info WHERE id=#{id}")
    int delete(@Param("id") Long id);
}
