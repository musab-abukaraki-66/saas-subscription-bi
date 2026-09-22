"""Loads the generated CSVs into a SQLite star schema: fact_subscription_monthly
plus dim_customer, dim_plan, and a generated dim_date.

This mirrors the exact model that would be built in Power BI: one fact table
at customer-month grain, three dimension tables, one-to-many relationships
from each dimension into the fact table's foreign keys.

Usage:
    python src/load_model.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path("data/saas_bi.db")


def build_dim_date(months: pd.Series) -> pd.DataFrame:
    periods = pd.PeriodIndex(sorted(months.unique()), freq="M")
    return pd.DataFrame(
        {
            "month": [str(p) for p in periods],
            "year": periods.year,
            "quarter": periods.quarter,
            "month_name": periods.strftime("%B"),
            "month_number": periods.month,
        }
    )


def main() -> None:
    dim_customer = pd.read_csv("data/dim_customer.csv")
    dim_plan = pd.read_csv("data/dim_plan.csv")
    fact = pd.read_csv("data/fact_subscription_monthly.csv")
    dim_date = build_dim_date(fact["month"])

    DB_PATH.unlink(missing_ok=True)
    conn = sqlite3.connect(DB_PATH)
    dim_customer.to_sql("dim_customer", conn, index=False)
    dim_plan.to_sql("dim_plan", conn, index=False)
    dim_date.to_sql("dim_date", conn, index=False)
    fact.to_sql("fact_subscription_monthly", conn, index=False)

    conn.execute("CREATE INDEX idx_fact_customer ON fact_subscription_monthly(customer_id)")
    conn.execute("CREATE INDEX idx_fact_month ON fact_subscription_monthly(month)")
    conn.execute("CREATE INDEX idx_fact_plan ON fact_subscription_monthly(plan_id)")
    conn.commit()
    conn.close()

    print(f"fact_subscription_monthly: {len(fact):,} rows")
    print(f"dim_customer: {len(dim_customer):,} | dim_plan: {len(dim_plan):,} | dim_date: {len(dim_date):,}")
    print(f"-> {DB_PATH}")


if __name__ == "__main__":
    main()
