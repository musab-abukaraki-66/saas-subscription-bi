"""Builds supporting chart images referenced in README.md / docs.

Usage:
    python src/build_figures.py
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

DB_PATH = Path("data/saas_bi.db")
FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#333333",
        "axes.grid": True,
        "grid.color": "#e6e6e6",
        "grid.linewidth": 0.8,
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

ACCENT = "#7c3aed"
ACCENT_DARK = "#4c1d95"
NEUTRAL = "#a1a1aa"


def mrr_trend(conn):
    df = pd.read_sql_query(Path("sql/01_mrr_trend.sql").read_text(), conn)
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(df["month"], df["new_mrr"], color=ACCENT, label="New MRR")
    ax.bar(df["month"], -df["churned_mrr"], color="#f97316", label="Churned MRR")
    ax2 = ax.twinx()
    ax2.plot(df["month"], df["total_mrr"], color=ACCENT_DARK, linewidth=2.2, marker="o", markersize=3, label="Total MRR")
    ax2.grid(False)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.set_xticks(df.index[::3])
    ax.set_xticklabels(df["month"][::3], rotation=45, ha="right")
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", frameon=False, fontsize=9)
    ax.set_title("New vs. churned MRR each month, with total MRR overlay", loc="left", fontweight="bold", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "01_mrr_trend.png", dpi=160)
    plt.close(fig)


def churn_rate(conn):
    df = pd.read_sql_query(Path("sql/02_monthly_churn_rate.sql").read_text(), conn).dropna()
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(df["month"], df["churn_rate_pct"], color=ACCENT, linewidth=2.2, marker="o", markersize=3)
    ax.axhline(df["churn_rate_pct"].mean(), color=NEUTRAL, linestyle="--", linewidth=1, label=f"Avg {df['churn_rate_pct'].mean():.2f}%")
    ax.set_xticks(df.index[::2])
    ax.set_xticklabels(df["month"][::2], rotation=45, ha="right")
    ax.set_ylabel("Monthly logo churn (%)")
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("Monthly logo churn rate — declining as the customer base matures", loc="left", fontweight="bold", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "02_churn_rate.png", dpi=160)
    plt.close(fig)


def cohort_retention(conn):
    df = pd.read_sql_query(Path("sql/04_cohort_retention.sql").read_text(), conn)
    avg_curve = df.groupby("months_since_signup")["retention_pct"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(avg_curve["months_since_signup"].astype(str), avg_curve["retention_pct"], color=ACCENT, width=0.5)
    for i, val in enumerate(avg_curve["retention_pct"]):
        ax.text(i, val, f"{val:.1f}%", ha="center", va="bottom", fontsize=10)
    ax.set_xlabel("Months since signup")
    ax.set_ylabel("Avg. retention across cohorts (%)")
    ax.set_ylim(0, 100)
    ax.set_title("Cohort retention curve\nAveraged across all monthly signup cohorts", loc="left", fontweight="bold", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "03_cohort_retention.png", dpi=160)
    plt.close(fig)


def arpu_by_segment(conn):
    df = pd.read_sql_query(Path("sql/03_arpu_by_segment_plan.sql").read_text(), conn)
    pivot = df.pivot(index="segment", columns="plan_name", values="segment_plan_mrr").fillna(0)
    plan_order = ["Starter", "Growth", "Scale", "Enterprise"]
    pivot = pivot[[p for p in plan_order if p in pivot.columns]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bottom = None
    colors = [ACCENT, "#a78bfa", "#f97316", ACCENT_DARK]
    for i, plan in enumerate(pivot.columns):
        vals = pivot[plan]
        ax.bar(pivot.index, vals, bottom=bottom, label=plan, color=colors[i % len(colors)])
        bottom = vals if bottom is None else bottom + vals
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:.0f}K"))
    ax.set_ylabel("MRR (latest month)")
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    ax.set_title("MRR by segment, split by plan (latest month)", loc="left", fontweight="bold", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "04_arpu_by_segment.png", dpi=160)
    plt.close(fig)


def main():
    conn = sqlite3.connect(DB_PATH)
    mrr_trend(conn)
    churn_rate(conn)
    cohort_retention(conn)
    arpu_by_segment(conn)
    conn.close()
    print(f"Saved 4 figures to {FIG_DIR}/")


if __name__ == "__main__":
    main()
