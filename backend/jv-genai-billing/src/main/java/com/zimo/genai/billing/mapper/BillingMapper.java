package com.zimo.genai.billing.mapper;

import com.zimo.genai.billing.entity.BillingOrder;
import org.apache.ibatis.annotations.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Mapper
public interface BillingMapper {

    @Select("SELECT balance FROM tb_account_balance WHERE id = 1")
    BigDecimal getBalance();

    @Update("UPDATE tb_account_balance SET balance = balance + #{delta}, updated_at = NOW() WHERE id = 1")
    int changeBalance(@Param("delta") BigDecimal delta);

    @Select("SELECT COALESCE(SUM(amount),0) FROM tb_billing_order "
            + "WHERE type = 'consume' AND status = 'success' AND created_at >= #{monthStart}")
    BigDecimal monthConsume(@Param("monthStart") String monthStart);

    @Select("SELECT COALESCE(SUM(amount),0) FROM tb_billing_order "
            + "WHERE type = 'topup' AND status = 'success' AND created_at >= #{monthStart}")
    BigDecimal monthTopup(@Param("monthStart") String monthStart);

    @Select("SELECT COALESCE(SUM(amount),0) FROM tb_billing_order "
            + "WHERE type = 'consume' AND status = 'success' AND DATE(created_at) = CURDATE()")
    BigDecimal todayConsume();

    @Select("<script>SELECT * FROM tb_billing_order WHERE status = 'success'"
            + "<if test='type != null and type != \"\"'> AND type = #{type}</if>"
            + " ORDER BY created_at DESC LIMIT #{offset}, #{size}</script>")
    List<BillingOrder> listOrders(@Param("type") String type,
                                  @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_billing_order WHERE status = 'success'"
            + "<if test='type != null and type != \"\"'> AND type = #{type}</if></script>")
    long countOrders(@Param("type") String type);

    @Insert("INSERT INTO tb_billing_order(order_no, type, amount, balance_after, channel, status, remark) "
            + "VALUES(#{orderNo}, #{type}, #{amount}, #{balanceAfter}, #{channel}, #{status}, #{remark})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertOrder(BillingOrder order);

    /* ===== 账单中心扩展查询 ===== */

    /** 充值/消费记录：类型 + 渠道 + 时间区间筛选（分页） */
    @Select("<script>SELECT * FROM tb_billing_order WHERE status = 'success'"
            + "<if test='type != null and type != \"\"'> AND type = #{type}</if>"
            + "<if test='channel != null and channel != \"\"'> AND channel = #{channel}</if>"
            + "<if test='from != null and from != \"\"'> AND DATE(created_at) &gt;= #{from}</if>"
            + "<if test='to != null and to != \"\"'> AND DATE(created_at) &lt;= #{to}</if>"
            + " ORDER BY created_at DESC LIMIT #{offset}, #{size}</script>")
    List<BillingOrder> listRange(@Param("type") String type, @Param("channel") String channel,
                                 @Param("from") String from, @Param("to") String to,
                                 @Param("offset") long offset, @Param("size") int size);

    @Select("<script>SELECT COUNT(*) FROM tb_billing_order WHERE status = 'success'"
            + "<if test='type != null and type != \"\"'> AND type = #{type}</if>"
            + "<if test='channel != null and channel != \"\"'> AND channel = #{channel}</if>"
            + "<if test='from != null and from != \"\"'> AND DATE(created_at) &gt;= #{from}</if>"
            + "<if test='to != null and to != \"\"'> AND DATE(created_at) &lt;= #{to}</if>"
            + "</script>")
    long countRange(@Param("type") String type, @Param("channel") String channel,
                    @Param("from") String from, @Param("to") String to);

    /** 充值渠道统计：笔数 / 金额 */
    @Select("<script>SELECT channel, COUNT(*) AS count, COALESCE(SUM(amount),0) AS total "
            + "FROM tb_billing_order WHERE type = 'topup' AND status = 'success'"
            + "<if test='from != null and from != \"\"'> AND DATE(created_at) &gt;= #{from}</if>"
            + "<if test='to != null and to != \"\"'> AND DATE(created_at) &lt;= #{to}</if>"
            + " GROUP BY channel ORDER BY total DESC</script>")
    List<Map<String, Object>> channelStats(@Param("from") String from, @Param("to") String to);

    /** 按月账单汇总：各月充值 / 消费 */
    @Select("<script>SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, type, "
            + "COUNT(*) AS count, COALESCE(SUM(amount),0) AS total "
            + "FROM tb_billing_order WHERE status = 'success'"
            + "<if test='from != null and from != \"\"'> AND DATE_FORMAT(created_at, '%Y-%m') &gt;= #{from}</if>"
            + "<if test='to != null and to != \"\"'> AND DATE_FORMAT(created_at, '%Y-%m') &lt;= #{to}</if>"
            + " GROUP BY DATE_FORMAT(created_at, '%Y-%m'), type ORDER BY month DESC, type</script>")
    List<Map<String, Object>> monthlyStats(@Param("from") String from, @Param("to") String to);
}
