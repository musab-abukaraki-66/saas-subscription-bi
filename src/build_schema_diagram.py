"""Renders the star schema diagram used in docs/data_model.md.

Usage:
    python src/build_schema_diagram.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

FACT_COLOR = "#4c1d95"
DIM_COLOR = "#7c3aed"
TEXT_WHITE = "white"


def box(ax, xy, w, h, title, fields, color):
    x, y = xy
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                 linewidth=0, facecolor=color))
    ax.text(x + w / 2, y + h - 0.12, title, ha="center", va="top", fontsize=11,
            fontweight="bold", color=TEXT_WHITE)
    ax.plot([x + 0.08, x + w - 0.08], [y + h - 0.22, y + h - 0.22], color="white", linewidth=0.6, alpha=0.5)
    for i, f in enumerate(fields):
        ax.text(x + 0.1, y + h - 0.36 - i * 0.16, f, ha="left", va="top", fontsize=8.3, color="white")


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=14,
                                  color="#333333", linewidth=1.2))


def main():
    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.2)
    ax.axis("off")

    ax.text(5.0, 6.95, "SaaS Subscription BI — Star Schema", ha="center", fontsize=14, fontweight="bold")
    ax.text(5.0, 6.68, "One fact table at customer x month grain, three conformed dimensions", ha="center", fontsize=9.5, color="#555")

    box(ax, (3.6, 2.6), 2.8, 1.9, "fact_subscription_monthly",
        ["customer_id (FK)", "plan_id (FK)", "month (FK)", "mrr", "event_type"], FACT_COLOR)

    box(ax, (0.3, 4.6), 2.6, 1.6, "dim_customer",
        ["customer_id (PK)", "signup_month", "segment", "acquisition_channel", "region"], DIM_COLOR)

    box(ax, (7.1, 4.6), 2.6, 1.6, "dim_plan",
        ["plan_id (PK)", "plan_name", "monthly_price", "tier"], DIM_COLOR)

    box(ax, (3.6, 0.3), 2.8, 1.4, "dim_date",
        ["month (PK)", "year", "quarter", "month_name"], DIM_COLOR)

    arrow(ax, (1.6, 4.6), (4.4, 4.5))
    arrow(ax, (8.4, 4.6), (5.6, 4.5))
    arrow(ax, (5.0, 2.6), (5.0, 1.7))

    fig.tight_layout()
    fig.savefig(FIG_DIR / "00_star_schema.png", dpi=160)
    plt.close(fig)
    print(f"Saved {FIG_DIR / '00_star_schema.png'}")


if __name__ == "__main__":
    main()
