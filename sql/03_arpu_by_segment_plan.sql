-- ARPU (average revenue per active account) by customer segment and plan,
-- for the most recent month in the dataset.
-- Business question: which segment/plan combinations carry the most revenue
-- weight per account?
WITH latest_month AS (
    SELECT MAX(month) AS month FROM fact_subscription_monthly
)
SELECT
    dc.segment,
    dp.plan_name,
    COUNT(DISTINCT f.customer_id)              AS accounts,
    ROUND(SUM(f.mrr), 2)                        AS segment_plan_mrr,
    ROUND(AVG(f.mrr), 2)                        AS arpu
FROM fact_subscription_monthly f
JOIN dim_customer dc ON dc.customer_id = f.customer_id
JOIN dim_plan dp ON dp.plan_id = f.plan_id
JOIN latest_month lm ON f.month = lm.month
GROUP BY dc.segment, dp.plan_name
ORDER BY dc.segment, dp.plan_name;
