from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io


def generate_pdf_report(df, score, breakdown, insights):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()
    savings = income - expense

    elements.append(Paragraph("Personal Finance Intelligent System", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Executive Financial Summary", styles["Heading1"]))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(f"Total Income: ₹ {income:,.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Total Expense: ₹ {expense:,.2f}", styles["Normal"]))
    elements.append(Paragraph(f"Net Savings: ₹ {savings:,.2f}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Financial Health Score: {score}/100", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Health Breakdown:", styles["Heading3"]))
    elements.append(Paragraph(f"Savings Ratio: {breakdown['Savings Ratio']}%", styles["Normal"]))
    elements.append(Paragraph(f"Large Transactions: {breakdown['Large Transactions']}", styles["Normal"]))
    elements.append(Paragraph(f"Anomalies: {breakdown['Anomalies']}", styles["Normal"]))
    elements.append(Paragraph(f"Top Category Concentration: {breakdown['Top Category Ratio']}%", styles["Normal"]))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Automated Insights:", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for insight in insights:
        elements.append(Paragraph(f"- {insight}", styles["Normal"]))
        elements.append(Spacer(1, 8))

    doc.build(elements)

    buffer.seek(0)
    return buffer
