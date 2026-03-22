"""
utils/insights.py
=================
Generates plain-language financial insights from transaction data.
Rule-based and deterministic — every insight has a clear data source.
"""

import pandas as pd
import numpy as np


def generate_insights(df: pd.DataFrame) -> list[str]:
    insights = []

    income  = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        insights.append(
            "No income transactions found. Upload a statement with both "
            "credits and debits for a full analysis."
        )
        return insights

    savings       = income - expense
    savings_ratio = savings / income

    # ── savings rate ──────────────────────────────────────────────
    if savings_ratio > 0.40:
        insights.append(
            f"Savings rate is {savings_ratio*100:.1f}% — well above the 30% benchmark. "
            "Strong financial discipline."
        )
    elif savings_ratio > 0.20:
        insights.append(
            f"Savings rate of {savings_ratio*100:.1f}% is healthy. "
            f"Pushing past 30% would add ₹{income*0.10:,.0f}/month to your wealth."
        )
    elif savings_ratio > 0:
        insights.append(
            f"Savings rate is only {savings_ratio*100:.1f}%. "
            f"Reducing discretionary spend by 10% would free up ₹{income*0.10:,.0f}/month."
        )
    else:
        insights.append(
            f"Expenses exceed income by ₹{abs(savings):,.0f}. "
            "You're drawing down savings — this needs immediate attention."
        )

    # ── top spending category ─────────────────────────────────────
    expense_df = df[df["transaction_type"] == "Expense"]
    if not expense_df.empty:
        cat_totals = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)
        top_cat    = cat_totals.index[0]
        top_pct    = cat_totals.iloc[0] / expense * 100
        insights.append(
            f"'{top_cat}' is your largest expense category at {top_pct:.1f}% of total spend."
        )
        if top_pct > 50:
            insights.append(
                "Spending concentration is high — over half your expenses go to one category. "
                "Consider reviewing if all of it is necessary."
            )

        # Second-largest category if worth mentioning
        if len(cat_totals) >= 2:
            sec_cat = cat_totals.index[1]
            sec_pct = cat_totals.iloc[1] / expense * 100
            if sec_pct > 15:
                insights.append(
                    f"'{sec_cat}' is your second-largest category at {sec_pct:.1f}% of spend."
                )

    # ── top merchant ──────────────────────────────────────────────
    if not expense_df.empty:
        merch_totals  = expense_df.groupby("merchant")["amount"].sum().sort_values(ascending=False)
        top_merch     = merch_totals.index[0]
        top_merch_amt = merch_totals.iloc[0]
        insights.append(
            f"Highest single-merchant spend: {top_merch} at ₹{top_merch_amt:,.0f}."
        )

    # ── anomaly alert ─────────────────────────────────────────────
    if "is_anomaly" in df.columns:
        anomaly_count = int(df["is_anomaly"].sum())
        if anomaly_count > 0:
            insights.append(
                f"{anomaly_count} statistically unusual transaction(s) detected. "
                "Review the Transactions page for details."
            )

    # ── large transactions ────────────────────────────────────────
    if "is_large" in df.columns:
        large_count = int(df["is_large"].sum())
        if large_count > 0:
            large_total = df[df["is_large"]]["amount"].sum()
            insights.append(
                f"{large_count} large transaction(s) totalling ₹{large_total:,.0f} "
                "— significantly above your average expense."
            )

    # ── month-to-month stability ──────────────────────────────────
    if "year_month" in df.columns:
        monthly = df.groupby(["year_month", "transaction_type"])["amount"].sum().unstack(fill_value=0)
        monthly["savings"] = monthly.get("Income", 0) - monthly.get("Expense", 0)
        if len(monthly) >= 2:
            vol = monthly["savings"].std()
            avg = monthly["savings"].mean()
            if vol > 0 and avg != 0 and (vol / abs(avg)) > 0.5:
                insights.append(
                    f"Monthly savings vary significantly (std dev ₹{vol:,.0f}). "
                    "Income or expenses are inconsistent month to month."
                )

            # Trend: is spending increasing?
            if len(monthly) >= 3 and "Expense" in monthly.columns:
                first_half  = monthly["Expense"].iloc[:len(monthly)//2].mean()
                second_half = monthly["Expense"].iloc[len(monthly)//2:].mean()
                if second_half > first_half * 1.2:
                    insights.append(
                        f"Spending has increased by ~{(second_half/first_half - 1)*100:.0f}% "
                        "in recent months compared to earlier periods."
                    )

    # ── investment presence ────────────────────────────────────────
    if not expense_df.empty and "Investments" in expense_df["category"].values:
        inv_total = expense_df[expense_df["category"] == "Investments"]["amount"].sum()
        inv_pct   = inv_total / income * 100
        msg = (
            f"Investing ₹{inv_total:,.0f} ({inv_pct:.1f}% of income). "
        )
        msg += "Good habit." if inv_pct >= 10 else "Consider scaling up toward 10–15% of income."
        insights.append(msg)
    else:
        insights.append(
            "No investment transactions detected. "
            "Consider allocating a portion of income to investments."
        )

    return insights