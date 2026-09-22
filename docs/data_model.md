# Data Model

![Star schema](../reports/figures/00_star_schema.png)

## Design

One fact table at **customer × month** grain, three conformed dimensions —
the standard Power BI star schema pattern (fact tables narrow and numeric,
dimensions wide and descriptive, all relationships one-to-many from dimension
to fact).

| Table | Role | Grain / Key |
|---|---|---|
| `fact_subscription_monthly` | Fact | One row per customer per month they were on the platform |
| `dim_customer` | Dimension | One row per customer |
| `dim_plan` | Dimension | One row per plan tier |
| `dim_date` | Dimension | One row per calendar month present in the fact table |

## Why this grain

Customer × month (rather than one row per subscription-lifetime, or one row
per raw event) is the standard SaaS metrics grain because it's what MRR,
churn rate, and cohort retention are all naturally computed against — each
measure is either a sum over this grain (`Total MRR`) or a distinct count at
this grain (`Active Customers`), which keeps the DAX in `dax/measures.dax`
simple and avoids row-context traps that a raw event-log grain would create.

## `event_type` field

Each fact row carries the account's *state that month*: `new`, `active`,
`upgraded`, `downgraded`, or `churned`. This is what makes New MRR and
Churned MRR simple `CALCULATE` filters instead of month-over-month deltas
computed in DAX — the classification is resolved once, at generation time,
and every downstream measure just filters on it.

## Relationships

- `dim_customer[customer_id]` → `fact_subscription_monthly[customer_id]` (1:M)
- `dim_plan[plan_id]` → `fact_subscription_monthly[plan_id]` (1:M)
- `dim_date[month]` → `fact_subscription_monthly[month]` (1:M)

All three are single-direction filters (dimension → fact), the default and
recommended Power BI relationship direction — it keeps filter propagation
predictable and avoids the ambiguous-filter-path warnings that bidirectional
relationships between three dimensions and one fact can trigger.
