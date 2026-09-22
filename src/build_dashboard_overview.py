"""Composes a single dashboard-overview PNG from a KPI header + the four chart
figures, for use as the README hero image. This is a Python/PIL composite
image mirroring the layout of reports/dashboard_mockup.html — labeled
explicitly (both here and in the README) as a rendered mockup, not a Power BI
Desktop screenshot, since Power BI Desktop was not available in this build
environment.

Usage:
    python src/build_dashboard_overview.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FIG_DIR = Path("reports/figures")
OUT_DIR = Path("reports/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)

PURPLE = (124, 58, 237)
PURPLE_DARK = (76, 29, 149)
BG = (244, 245, 247)
CARD = (255, 255, 255)
TEXT = (31, 41, 55)
MUTED = (107, 114, 128)

W = 1440
PAD = 28


def font(size, bold=False):
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    try:
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def rounded_card(draw, box, fill, radius=10, outline=None):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline)


def main():
    kpis = [
        ("TOTAL MRR (DEC 2024)", "$129.4K", "1,501 active customers"),
        ("AVG. MONTHLY LOGO CHURN", "4.50%", "Trending down since Q2 2023"),
        ("BLENDED ARPU", "$86.21", "Across all plans, latest month"),
        ("12-MONTH COHORT RETENTION", "60.1%", "Averaged across all signup cohorts"),
    ]

    header_h = 90
    kpi_h = 110
    chart_row_h = 340
    chart_row2_h = 400
    footer_h = 40
    H = header_h + kpi_h + chart_row_h + chart_row2_h + footer_h + PAD * 5

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((PAD, PAD), "SaaS Subscription BI — Growth & Retention", font=font(24, True), fill=TEXT)
    draw.text((PAD, PAD + 32), "Portfolio case study · synthetic dataset · 2023–2024", font=font(13), fill=MUTED)
    badge_text = "DASHBOARD MOCKUP — Python/PIL render, not a Power BI Desktop screenshot"
    bf = font(12, True)
    bw = draw.textlength(badge_text, font=bf)
    badge_box = (W - PAD - bw - 24, PAD + 4, W - PAD, PAD + 30)
    rounded_card(draw, badge_box, PURPLE, radius=14)
    draw.text((badge_box[0] + 12, badge_box[1] + 6), badge_text, font=bf, fill="white")

    y = header_h + PAD
    kpi_w = (W - PAD * 2 - PAD * 3) / 4
    for i, (label, value, sub) in enumerate(kpis):
        x = PAD + i * (kpi_w + PAD)
        box = (x, y, x + kpi_w, y + kpi_h)
        rounded_card(draw, box, CARD, radius=10)
        draw.rectangle((x, y, x + 4, y + kpi_h), fill=PURPLE)
        draw.text((x + 16, y + 12), label, font=font(11, True), fill=MUTED)
        draw.text((x + 16, y + 32), value, font=font(26, True), fill=PURPLE_DARK)
        draw.text((x + 16, y + 68), sub, font=font(11), fill=MUTED)

    y += kpi_h + PAD

    def paste_panel(path, title, box):
        x0, y0, x1, y1 = box
        rounded_card(draw, box, CARD, radius=10)
        draw.text((x0 + 14, y0 + 10), title, font=font(13, True), fill=TEXT)
        chart = Image.open(path)
        avail_w = (x1 - x0) - 24
        avail_h = (y1 - y0) - 44
        scale = min(avail_w / chart.width, avail_h / chart.height)
        chart = chart.resize((int(chart.width * scale), int(chart.height * scale)))
        img.paste(chart, (int(x0 + 12), int(y0 + 36)))

    half_w = (W - PAD * 3) / 2
    paste_panel(FIG_DIR / "01_mrr_trend.png", "New vs. Churned MRR, with Total MRR trend",
                (PAD, y, PAD + half_w, y + chart_row_h))
    paste_panel(FIG_DIR / "02_churn_rate.png", "Monthly Logo Churn Rate",
                (PAD * 2 + half_w, y, PAD * 2 + half_w * 2, y + chart_row_h))

    y += chart_row_h + PAD
    paste_panel(FIG_DIR / "03_cohort_retention.png", "Cohort Retention Curve",
                (PAD, y, PAD + half_w, y + chart_row2_h))
    paste_panel(FIG_DIR / "04_arpu_by_segment.png", "MRR by Segment, split by Plan",
                (PAD * 2 + half_w, y, PAD * 2 + half_w * 2, y + chart_row2_h))

    y += chart_row2_h + PAD
    footer_text = "All KPI values verified against sql/*.sql output via src/run_sql.py · synthetic data, seed=7 · not a real company's metrics"
    fw = draw.textlength(footer_text, font=font(11))
    draw.text(((W - fw) / 2, y), footer_text, font=font(11), fill=MUTED)

    out_path = OUT_DIR / "dashboard_overview.png"
    img.save(out_path)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
