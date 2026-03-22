"""
utils/report_generator.py
==========================
Generates a clean, structured PDF report using ReportLab.
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

# ── colour palette ────────────────────────────────────────────────────────────
BLUE     = colors.HexColor("#2563EB")
DARK     = colors.HexColor("#111827")
MID      = colors.HexColor("#6B7280")
LIGHT_BG = colors.HexColor("#F8FAFC")
BORDER   = colors.HexColor("#E2E8F0")
GREEN    = colors.HexColor("#16A34A")
RED      = colors.HexColor("#DC2626")
AMBER    = colors.HexColor("#D97706")


def _make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Normal"],
            fontSize=22, textColor=DARK,
            spaceAfter=4, fontName="Helvetica-Bold",
        ),
        "sub": ParagraphStyle(
            "sub", parent=base["Normal"],
            fontSize=11, textColor=MID, spaceAfter=16,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Normal"],
            fontSize=13, textColor=DARK,
            spaceBefore=14, spaceAfter=5,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=9, textColor=DARK,
            spaceAfter=4, leading=14,
        ),
        "insight": ParagraphStyle(
            "insight", parent=base["Normal"],
            fontSize=9, textColor=DARK,
            spaceAfter=5, leading=14, leftIndent=10,
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"],
            fontSize=8, textColor=MID, spaceAfter=3,
        ),
    }


def _table_style(header_color=None) -> TableStyle:
    hc = header_color or BLUE
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  hc),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ])


def generate_pdf_report(
    df,
    score: int,
    breakdown: dict,
    insights: list[str],
) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    s     = _make_styles()
    elems = []

    income   = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense  = df[df["transaction_type"] == "Expense"]["amount"].sum()
    savings  = income - expense
    sav_pct  = savings / income * 100 if income else 0

    # ── Title ─────────────────────────────────────────────────────
    elems.append(Paragraph("PFIS — Financial Report", s["title"]))
    elems.append(Paragraph("Personal Finance Intelligent System", s["sub"]))
    elems.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elems.append(Spacer(1, 0.3*cm))

    # ── Summary table ──────────────────────────────────────────────
    elems.append(Paragraph("Financial Summary", s["h2"]))
    summary_data = [
        ["Metric",            "Value"],
        ["Total Income",      f"₹ {income:,.2f}"],
        ["Total Expense",     f"₹ {expense:,.2f}"],
        ["Net Savings",       f"₹ {savings:,.2f}  ({sav_pct:.1f}%)"],
        ["Health Score",      f"{score} / 100"],
        ["Report Generated",  datetime.now().strftime("%d %b %Y, %I:%M %p")],
    ]
    t = Table(summary_data, colWidths=[9*cm, 8*cm])
    t.setStyle(_table_style())
    elems.append(t)
    elems.append(Spacer(1, 0.3*cm))

    # ── Score breakdown ────────────────────────────────────────────
    elems.append(Paragraph("Health Score Breakdown", s["h2"]))
    bd_rows = [[k, v] for k, v in breakdown.items() if k != "note"]
    if bd_rows:
        bt = Table([["Factor", "Value"]] + bd_rows, colWidths=[11*cm, 6*cm])
        bt.setStyle(_table_style(header_color=DARK))
        elems.append(bt)
    elems.append(Spacer(1, 0.3*cm))

    # ── Expenses by category ───────────────────────────────────────
    expense_df = df[df["transaction_type"] == "Expense"]
    if not expense_df.empty:
        elems.append(Paragraph("Expenses by Category", s["h2"]))
        cat_totals = (
            expense_df.groupby("category")["amount"].sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        cat_data = [["Category", "Amount (₹)", "% of Spend"]] + [
            [
                r["category"],
                f"₹ {r['amount']:,.2f}",
                f"{r['amount']/expense*100:.1f}%",
            ]
            for _, r in cat_totals.iterrows()
        ]
        ct = Table(cat_data, colWidths=[8*cm, 6*cm, 3*cm])
        ct.setStyle(_table_style(header_color=DARK))
        elems.append(ct)
        elems.append(Spacer(1, 0.3*cm))

    # ── Top merchants ──────────────────────────────────────────────
    if not expense_df.empty:
        elems.append(Paragraph("Top 10 Merchants by Spend", s["h2"]))
        top_merch = (
            expense_df.groupby("merchant")["amount"].sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        merch_data = [["Merchant", "Total Spent (₹)"]] + [
            [r["merchant"], f"₹ {r['amount']:,.2f}"]
            for _, r in top_merch.iterrows()
        ]
        mt = Table(merch_data, colWidths=[11*cm, 6*cm])
        mt.setStyle(_table_style(header_color=DARK))
        elems.append(mt)
        elems.append(Spacer(1, 0.3*cm))

    # ── Insights ───────────────────────────────────────────────────
    elems.append(Paragraph("Automated Insights", s["h2"]))
    for insight in insights:
        elems.append(Paragraph(f"→  {insight}", s["insight"]))

    # ── Footer ─────────────────────────────────────────────────────
    elems.append(Spacer(1, 0.6*cm))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elems.append(Spacer(1, 0.2*cm))
    elems.append(Paragraph(
        "Generated by PFIS · Personal Finance Intelligent System · 2026",
        s["caption"],
    ))

    doc.build(elems)
    buffer.seek(0)
    return buffer