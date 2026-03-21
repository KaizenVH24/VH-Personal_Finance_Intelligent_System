"""
report_generator.py
Generates a clean, structured PDF report using ReportLab.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


# ── colour constants ────────────────────────────────────────────
BLUE      = colors.HexColor("#2563EB")
DARK      = colors.HexColor("#111827")
MID       = colors.HexColor("#6B7280")
LIGHT_BG  = colors.HexColor("#F8FAFC")
BORDER    = colors.HexColor("#E2E8F0")
GREEN     = colors.HexColor("#16A34A")
RED       = colors.HexColor("#DC2626")


def _make_styles():
    base = getSampleStyleSheet()
    return {
        "title":   ParagraphStyle("title",   parent=base["Normal"],
                                  fontSize=22, textColor=DARK,
                                  spaceAfter=4, fontName="Helvetica-Bold"),
        "sub":     ParagraphStyle("sub",     parent=base["Normal"],
                                  fontSize=11, textColor=MID, spaceAfter=16),
        "h2":      ParagraphStyle("h2",      parent=base["Normal"],
                                  fontSize=14, textColor=DARK, spaceBefore=16,
                                  spaceAfter=6, fontName="Helvetica-Bold"),
        "body":    ParagraphStyle("body",    parent=base["Normal"],
                                  fontSize=10, textColor=DARK,
                                  spaceAfter=4, leading=15),
        "insight": ParagraphStyle("insight", parent=base["Normal"],
                                  fontSize=10, textColor=DARK,
                                  spaceAfter=6, leading=15,
                                  leftIndent=10),
    }


def generate_pdf_report(df, score: int, breakdown: dict, insights: list[str]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )

    s     = _make_styles()
    elems = []

    income   = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense  = df[df["transaction_type"] == "Expense"]["amount"].sum()
    savings  = income - expense

    # ── Title ────────────────────────────────────────────────────
    elems.append(Paragraph("PFIS — Financial Report", s["title"]))
    elems.append(Paragraph("Personal Finance Intelligent System", s["sub"]))
    elems.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elems.append(Spacer(1, 0.4*cm))

    # ── Summary table ────────────────────────────────────────────
    elems.append(Paragraph("Financial Summary", s["h2"]))
    summary_data = [
        ["Metric",          "Value"],
        ["Total Income",    f"₹ {income:,.2f}"],
        ["Total Expense",   f"₹ {expense:,.2f}"],
        ["Net Savings",     f"₹ {savings:,.2f}"],
        ["Health Score",    f"{score} / 100"],
    ]
    t = Table(summary_data, colWidths=[9*cm, 8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID",       (0, 0), (-1, -1), 0.5, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0,0), (-1, -1), 6),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 0.3*cm))

    # ── Score breakdown ──────────────────────────────────────────
    elems.append(Paragraph("Health Score Breakdown", s["h2"]))
    bd_data = [["Factor", "Value"]] + [[k, v] for k, v in breakdown.items()
                                        if k != "note"]
    if len(bd_data) > 1:
        bt = Table(bd_data, colWidths=[11*cm, 6*cm])
        bt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("GRID",       (0, 0), (-1, -1), 0.5, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",  (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0,0), (-1, -1), 6),
        ]))
        elems.append(bt)

    elems.append(Spacer(1, 0.3*cm))

    # ── Top expenses by category ─────────────────────────────────
    expense_df = df[df["transaction_type"] == "Expense"]
    if not expense_df.empty:
        elems.append(Paragraph("Expenses by Category", s["h2"]))
        cat_totals = (
            expense_df.groupby("category")["amount"].sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        cat_data = [["Category", "Amount"]] + [
            [r["category"], f"₹ {r['amount']:,.2f}"]
            for _, r in cat_totals.iterrows()
        ]
        ct = Table(cat_data, colWidths=[11*cm, 6*cm])
        ct.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
            ("GRID",       (0, 0), (-1, -1), 0.5, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",  (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING",(0,0), (-1, -1), 6),
        ]))
        elems.append(ct)
        elems.append(Spacer(1, 0.3*cm))

    # ── Insights ─────────────────────────────────────────────────
    elems.append(Paragraph("Automated Insights", s["h2"]))
    for insight in insights:
        elems.append(Paragraph(f"→  {insight}", s["insight"]))

    elems.append(Spacer(1, 0.6*cm))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    elems.append(Spacer(1, 0.2*cm))
    elems.append(Paragraph("Generated by PFIS · Personal Finance Intelligent System, 2026", s["body"]))

    doc.build(elems)
    buffer.seek(0)
    return buffer