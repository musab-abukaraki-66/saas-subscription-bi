-- Cohort retention: of customers who signed up in a given month, what % are
-- still active N months later (month 1, 3, 6, 12)?
-- Business question: does retention differ by signup cohort, and where's the
-- steepest drop-off?
WITH cohort_size AS (
    SELECT signup_month, COUNT(*) AS cohort_customers
    FROM dim_customer
    GROUP BY signup_month
),
retained AS (
    SELECT
        dc.signup_month,
        CAST(
            (strftime('%Y', f.month || '-01') - strftime('%Y', dc.signup_month || '-01')) * 12 +
            (strftime('%m', f.month || '-01') - strftime('%m', dc.signup_month || '-01'))
            AS INTEGER
        ) AS months_since_signup,
        COUNT(DISTINCT f.customer_id) AS retained_customers
    FROM fact_subscription_monthly f
    JOIN dim_customer dc ON dc.customer_id = f.customer_id
    WHERE f.event_type != 'churned'
    GROUP BY dc.signup_month, months_since_signup
)
SELECT
    r.signup_month,
    cs.cohort_customers,
    r.months_since_signup,
    r.retained_customers,
    ROUND(100.0 * r.retained_customers / cs.cohort_customers, 1) AS retention_pct
FROM retained r
JOIN cohort_size cs ON cs.signup_month = r.signup_month
WHERE r.months_since_signup IN (1, 3, 6, 12)
ORDER BY r.signup_month, r.months_since_signup;
