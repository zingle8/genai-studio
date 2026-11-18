package com.zimo.genai.costs.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;
import java.util.Map;

@Mapper
public interface CostMapper {

    @Select("SELECT COALESCE(SUM(cost),0) AS cost, COALESCE(SUM(requests),0) AS requests, "
            + "COALESCE(SUM(tokens),0) AS tokens FROM tb_cost_daily WHERE stat_date = CURDATE()")
    Map<String, Object> today();

    @Select("SELECT COALESCE(SUM(cost),0) AS cost, COALESCE(SUM(requests),0) AS requests, "
            + "COALESCE(SUM(tokens),0) AS tokens FROM tb_cost_daily "
            + "WHERE stat_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')")
    Map<String, Object> month();

    @Select("SELECT stat_date AS statDate, ROUND(SUM(cost),4) AS cost, SUM(requests) AS requests, "
            + "SUM(tokens) AS tokens FROM tb_cost_daily "
            + "WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL #{days} DAY) "
            + "GROUP BY stat_date ORDER BY stat_date")
    List<Map<String, Object>> daily(@Param("days") int days);

    @Select("SELECT model, ROUND(SUM(cost),4) AS cost, SUM(requests) AS requests, SUM(tokens) AS tokens "
            + "FROM tb_cost_daily WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL #{days} DAY) "
            + "GROUP BY model ORDER BY cost DESC")
    List<Map<String, Object>> byModel(@Param("days") int days);

    @Select("SELECT service_id AS serviceId, ROUND(SUM(cost),4) AS cost, SUM(requests) AS requests "
            + "FROM tb_cost_daily WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL #{days} DAY) "
            + "GROUP BY service_id ORDER BY cost DESC")
    List<Map<String, Object>> byService(@Param("days") int days);

    /* ===== 按日期区间查询（前端日期筛选） ===== */

    @Select("SELECT stat_date AS statDate, ROUND(SUM(cost),4) AS cost, SUM(requests) AS requests, "
            + "SUM(tokens) AS tokens FROM tb_cost_daily "
            + "WHERE stat_date >= #{from} AND stat_date <= #{to} "
            + "GROUP BY stat_date ORDER BY stat_date")
    List<Map<String, Object>> dailyRange(@Param("from") String from, @Param("to") String to);

    @Select("SELECT model, ROUND(SUM(cost),4) AS cost, SUM(requests) AS requests, SUM(tokens) AS tokens "
            + "FROM tb_cost_daily WHERE stat_date >= #{from} AND stat_date <= #{to} "
            + "GROUP BY model ORDER BY cost DESC")
    List<Map<String, Object>> byModelRange(@Param("from") String from, @Param("to") String to);

    @Select("SELECT COALESCE(SUM(cost),0) AS cost, COALESCE(SUM(requests),0) AS requests, "
            + "COALESCE(SUM(tokens),0) AS tokens, COUNT(DISTINCT stat_date) AS activeDays "
            + "FROM tb_cost_daily WHERE stat_date >= #{from} AND stat_date <= #{to}")
    Map<String, Object> rangeSummary(@Param("from") String from, @Param("to") String to);
}
