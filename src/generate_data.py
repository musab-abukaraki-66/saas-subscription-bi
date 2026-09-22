"""
Generates a synthetic SaaS subscription dataset — customers, plans, and a
monthly subscription-state fact table (active / new / upgraded / downgraded /
churned) suitable for a star-schema BI model.

Entirely synthetic (seeded, reproducible). Does not represent a real company.

Usage:
    python src/generate_data.py
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 7
N_CUSTOMERS = 2_500
START_MONTH = "2023-01"
END_MONTH = "2024-12"

PLANS = pd.DataFrame(
    [
        {"plan_id": 1, "plan_name": "Starter", "monthly_price": 19.0, "tier": 1},
        {"plan_id": 2, "plan_name": "Growth", "monthly_price": 49.0, "tier": 2},
        {"plan_id": 3, "plan_name": "Scale", "monthly_price": 99.0, "tier": 3},
        {"plan_id": 4, "plan_name": "Enterprise", "monthly_price": 249.0, "tier": 4},
    ]
)

SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
CHANNELS = ["Self-Serve", "Sales-Led", "Partner"]
REGIONS = ["North America", "Europe", "APAC", "LATAM"]


def month_range() -> pd.PeriodIndex:
    return pd.period_range(START_MONTH, END_MONTH, freq="M")


def generate() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(SEED)
    months = month_range()

    signup_month_idx = rng.integers(0, len(months) - 1, size=N_CUSTOMERS)
    # Bias more signups into earlier months so cohorts have runway to churn.
    signup_month_idx = np.sort(rng.choice(np.arange(len(months) - 1), size=N_CUSTOMERS,
                                           p=_signup_weights(len(months) - 1)))

    dim_customer = pd.DataFrame(
        {
            "customer_id": np.arange(1, N_CUSTOMERS + 1),
            "signup_month": [str(months[i]) for i in signup_month_idx],
            "segment": rng.choice(SEGMENTS, size=N_CUSTOMERS, p=[0.62, 0.28, 0.10]),
            "acquisition_channel": rng.choice(CHANNELS, size=N_CUSTOMERS, p=[0.55, 0.30, 0.15]),
            "region": rng.choice(REGIONS, size=N_CUSTOMERS, p=[0.40, 0.30, 0.20, 0.10]),
        }
    )

    # Starting plan correlates with segment.
    plan_probs = {
        "SMB": [0.55, 0.35, 0.09, 0.01],
        "Mid-Market": [0.10, 0.45, 0.35, 0.10],
        "Enterprise": [0.00, 0.10, 0.30, 0.60],
    }
    dim_customer["start_plan_id"] = [
        rng.choice(PLANS["plan_id"], p=plan_probs[seg]) for seg in dim_customer["segment"]
    ]

    # Monthly churn hazard depends on segment (Enterprise stickier) and tenure
    # (higher hazard in first 3 months, "early churn").
    base_hazard = {"SMB": 0.045, "Mid-Market": 0.025, "Enterprise": 0.012}
    upgrade_prob = {"SMB": 0.03, "Mid-Market": 0.05, "Enterprise": 0.04}
    downgrade_prob = {"SMB": 0.02, "Mid-Market": 0.015, "Enterprise": 0.006}

    fact_rows = []
    for _, cust in dim_customer.iterrows():
        cid = cust["customer_id"]
        seg = cust["segment"]
        plan_id = cust["start_plan_id"]
        start_idx = signup_month_idx[cid - 1]
        churned = False
        for m_idx in range(start_idx, len(months)):
            month = str(months[m_idx])
            tenure = m_idx - start_idx
            if churned:
                break

            hazard = base_hazard[seg] * (2.2 if tenure < 3 else 1.0)
            event = "active"
            if tenure > 0:
                roll = rng.random()
                if roll < hazard:
                    event = "churned"
                elif roll < hazard + upgrade_prob[seg] and plan_id < 4:
                    plan_id += 1
                    event = "upgraded"
                elif roll < hazard + upgrade_prob[seg] + downgrade_prob[seg] and plan_id > 1:
                    plan_id -= 1
                    event = "downgraded"
            else:
                event = "new"

            price = float(PLANS.loc[PLANS["plan_id"] == plan_id, "monthly_price"].iloc[0])
            fact_rows.append(
                {
                    "customer_id": cid,
                    "month": month,
                    "plan_id": plan_id,
                    "mrr": price,
                    "event_type": event,
                }
            )
            if event == "churned":
                churned = True

    fact_subscription = pd.DataFrame(fact_rows)
    return dim_customer.drop(columns=["start_plan_id"]), PLANS, fact_subscription


def _signup_weights(n: int) -> np.ndarray:
    w = np.linspace(1.6, 0.5, n)
    return w / w.sum()


def main() -> None:
    dim_customer, dim_plan, fact_subscription = generate()
    dim_customer.to_csv("data/dim_customer.csv", index=False)
    dim_plan.to_csv("data/dim_plan.csv", index=False)
    fact_subscription.to_csv("data/fact_subscription_monthly.csv", index=False)
    print(f"dim_customer: {len(dim_customer):,} rows")
    print(f"dim_plan: {len(dim_plan):,} rows")
    print(f"fact_subscription_monthly: {len(fact_subscription):,} rows")


if __name__ == "__main__":
    main()
