package com.zimo.genai.apikey.mapper;

import com.zimo.genai.apikey.entity.ApiKeyEntity;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ApiKeyMapper {

    @Select("<script>SELECT * FROM tb_api_key WHERE 1=1"
            + "<if test='owner != null and owner != \"\"'> AND owner = #{owner}</if>"
            + "<if test='keyword != null and keyword != \"\"'>"
            + " AND (name LIKE CONCAT('%', #{keyword}, '%') OR api_key LIKE CONCAT('%', #{keyword}, '%') OR key_id LIKE CONCAT('%', #{keyword}, '%'))"
            + "</if>"
            + " ORDER BY created_at DESC LIMIT #{offset}, #{size}</script>")
    List<ApiKeyEntity> list(@Param("owner") String owner, @Param("keyword") String keyword,
                            @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_api_key WHERE 1=1"
            + "<if test='owner != null and owner != \"\"'> AND owner = #{owner}</if>"
            + "<if test='keyword != null and keyword != \"\"'>"
            + " AND (name LIKE CONCAT('%', #{keyword}, '%') OR api_key LIKE CONCAT('%', #{keyword}, '%') OR key_id LIKE CONCAT('%', #{keyword}, '%'))"
            + "</if></script>")
    long count(@Param("owner") String owner, @Param("keyword") String keyword);

    @Select("SELECT * FROM tb_api_key WHERE id = #{id}")
    ApiKeyEntity getById(@Param("id") Long id);

    @Insert("INSERT INTO tb_api_key(name, key_id, api_key, owner, expiry_date, models, fields, "
            + "org_company, org_dept, org_business, rpm, tpm, cc, remark, status) "
            + "VALUES(#{name}, #{keyId}, #{apiKey}, #{owner}, #{expiryDate}, #{models}, #{fields}, "
            + "#{orgCompany}, #{orgDept}, #{orgBusiness}, #{rpm}, #{tpm}, #{cc}, #{remark}, 1)")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(ApiKeyEntity entity);

    @Update("<script>UPDATE tb_api_key"
            + "<set>"
            + "<if test='name != null'>name = #{name},</if>"
            + "<if test='expiryDate != null'>expiry_date = #{expiryDate},</if>"
            + "<if test='expiryNever != null and expiryNever'>expiry_date = NULL,</if>"
            + "<if test='models != null'>models = #{models},</if>"
            + "<if test='fields != null'>fields = #{fields},</if>"
            + "<if test='orgCompany != null'>org_company = #{orgCompany},</if>"
            + "<if test='orgDept != null'>org_dept = #{orgDept},</if>"
            + "<if test='orgBusiness != null'>org_business = #{orgBusiness},</if>"
            + "<if test='rpm != null'>rpm = #{rpm},</if>"
            + "<if test='tpm != null'>tpm = #{tpm},</if>"
            + "<if test='cc != null'>cc = #{cc},</if>"
            + "<if test='remark != null'>remark = #{remark},</if>"
            + "<if test='status != null'>status = #{status},</if>"
            + "</set> WHERE id = #{id}</script>")
    int update(ApiKeyEntity entity);

    @Delete("DELETE FROM tb_api_key WHERE id = #{id}")
    int delete(@Param("id") Long id);
}
