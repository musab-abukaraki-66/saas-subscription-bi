-- Logo churn rate: churned customers in month M / active customers in month M-1.
-- Business question: is churn improving or worsening over time?
WITH churned AS (
    SELECT month, COUNT(DISTINCT customer_id) AS churned_customers
    FROM fact_subscription_monthly
    WHERE event_type = 'churned'
    GROUP BY month
),
active_by_month AS (
    SELECT month, COUNT(DISTINCT customer_id) AS active_customers
    FROM fact_subscription_monthly
    GROUP BY month
)
SELECT
    curr.month,
    COALESCE(prev.active_customers, 0) AS starting_customers,
    COALESCE(ch.churned_customers, 0)  AS churned_customers,
    ROUND(
        100.0 * COALESCE(ch.churned_customers, 0) / NULLIF(prev.active_customers, 0), 2
    ) AS churn_rate_pct
FROM (SELECT DISTINCT month FROM fact_subscription_monthly) curr
LEFT JOIN active_by_month prev
    ON prev.month = strftime('%Y-%m', date(curr.month || '-01', '-1 month'))
LEFT JOIN churned ch ON ch.month = curr.month
ORDER BY curr.month;
