-- LTV proxy by acquisition channel: average cumulative revenue per customer
-- (sum of all mrr rows to date, a simple realized-revenue-to-date proxy —
-- not a discounted/predicted LTV model).
-- Business question: which acquisition channel brings in customers who are
-- worth the most over their (observed) lifetime so far?
SELECT
    dc.acquisition_channel,
    COUNT(DISTINCT f.customer_id)                              AS customers,
    ROUND(SUM(f.mrr) / COUNT(DISTINCT f.customer_id), 2)       AS revenue_to_date_per_customer,
    ROUND(AVG(months.month_count), 1)                          AS avg_months_active
FROM fact_subscription_monthly f
JOIN dim_customer dc ON dc.customer_id = f.customer_id
JOIN (
    SELECT customer_id, COUNT(*) AS month_count
    FROM fact_subscription_monthly
    GROUP BY customer_id
) months ON months.customer_id = f.customer_id
GROUP BY dc.acquisition_channel
ORDER BY revenue_to_date_per_customer DESC;
