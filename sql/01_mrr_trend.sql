-- Total MRR, New MRR, Churned MRR, and Net New MRR by month.
-- Business question: is the business growing, and how much of net growth is
-- new business vs. expansion vs. offset by churn?
SELECT
    month,
    ROUND(SUM(mrr), 2)                                              AS total_mrr,
    ROUND(SUM(CASE WHEN event_type = 'new' THEN mrr ELSE 0 END), 2)      AS new_mrr,
    ROUND(SUM(CASE WHEN event_type = 'churned' THEN mrr ELSE 0 END), 2)  AS churned_mrr,
    COUNT(DISTINCT customer_id)                                     AS active_customers
FROM fact_subscription_monthly
GROUP BY month
ORDER BY month;
