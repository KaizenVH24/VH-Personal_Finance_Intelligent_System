"""
utils/insights.py
=================
Improved human-like financial insights.
"""

import pandas as pd
import numpy as np
import random


# ─────────────────────────────────────────────────────────────
# HELPERS (to avoid robotic repetition)
# ─────────────────────────────────────────────────────────────

def pick(options):
    return random.choice(options)


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def generate_insights(df: pd.DataFrame):

    insights = []

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        return ["No income detected. Upload a complete statement for better analysis."]

    savings = income - expense
    savings_ratio = savings / income


    # ─────────────────────────────────────────────────────────
    # SAVINGS ANALYSIS
    # ─────────────────────────────────────────────────────────

    if savings_ratio > 0.4:
        insights.append(
            pick([
                f"You're saving {savings_ratio*100:.1f}% of your income — that's elite-level discipline.",
                f"Strong financial control. A {savings_ratio*100:.1f}% savings rate puts you ahead of most people."
            ])
        )

    elif savings_ratio > 0.2:
        insights.append(
            pick([
                f"You're saving {savings_ratio*100:.1f}% of your income — solid, but there’s room to push toward 30%.",
                f"Healthy savings rate at {savings_ratio*100:.1f}%. Increasing it slightly could accelerate your goals."
            ])
        )

    elif savings_ratio > 0:
        insights.append(
            pick([
                f"Savings are low at {savings_ratio*100:.1f}%. Cutting a few unnecessary expenses could improve this quickly.",
                f"You're saving, but only {savings_ratio*100:.1f}% — small adjustments can create a big impact."
            ])
        )

    else:
        insights.append(
            pick([
                f"You're spending more than you earn by ₹{abs(savings):,.0f}. This isn't sustainable.",
                f"Negative savings detected (₹{abs(savings):,.0f}). Immediate expense control is needed."
            ])
        )


    # ─────────────────────────────────────────────────────────
    # CATEGORY ANALYSIS
    # ─────────────────────────────────────────────────────────

    expense_df = df[df["transaction_type"] == "Expense"]

    if not expense_df.empty:

        cat_totals = expense_df.groupby("category")["amount"].sum().sort_values(ascending=False)

        top_cat = cat_totals.index[0]
        top_pct = cat_totals.iloc[0] / expense * 100

        insights.append(
            pick([
                f"Most of your money is going into '{top_cat}' ({top_pct:.1f}% of total spend).",
                f"'{top_cat}' dominates your expenses at {top_pct:.1f}% — worth reviewing."
            ])
        )

        if top_pct > 50:
            insights.append(
                "You're heavily dependent on a single spending category. Diversifying or optimizing here can improve balance."
            )


    # ─────────────────────────────────────────────────────────
    # MERCHANT ANALYSIS
    # ─────────────────────────────────────────────────────────

    if not expense_df.empty:

        merch = expense_df.groupby("merchant")["amount"].sum().sort_values(ascending=False)

        top_merch = merch.index[0]
        top_amt = merch.iloc[0]

        insights.append(
            pick([
                f"Highest spend is on {top_merch} (₹{top_amt:,.0f}).",
                f"{top_merch} is your top expense source at ₹{top_amt:,.0f}."
            ])
        )


    # ─────────────────────────────────────────────────────────
    # ANOMALY + LARGE TRANSACTIONS
    # ─────────────────────────────────────────────────────────

    if "is_anomaly" in df.columns:
        count = int(df["is_anomaly"].sum())
        if count > 0:
            insights.append(
                f"{count} unusual transactions detected. Worth a quick check."
            )

    if "is_large" in df.columns:
        count = int(df["is_large"].sum())
        if count > 0:
            insights.append(
                f"{count} large transactions spotted — these may be one-time or high-impact expenses."
            )


    # ─────────────────────────────────────────────────────────
    # SPENDING TREND
    # ─────────────────────────────────────────────────────────

    if "year_month" in df.columns:

        monthly = df.groupby(["year_month", "transaction_type"])["amount"].sum().unstack(fill_value=0)

        if len(monthly) >= 3 and "Expense" in monthly.columns:

            first = monthly["Expense"].iloc[:len(monthly)//2].mean()
            second = monthly["Expense"].iloc[len(monthly)//2:].mean()

            if second > first * 1.2:
                insights.append(
                    "Your spending has increased noticeably in recent months. Keep an eye on this trend."
                )


    # ─────────────────────────────────────────────────────────
    # INVESTMENT CHECK
    # ─────────────────────────────────────────────────────────

    if not expense_df.empty and "Investments" in expense_df["category"].values:

        inv_total = expense_df[expense_df["category"] == "Investments"]["amount"].sum()
        inv_pct = inv_total / income * 100

        if inv_pct >= 10:
            insights.append(
                f"You're investing {inv_pct:.1f}% of your income — great long-term strategy."
            )
        else:
            insights.append(
                f"Investment is only {inv_pct:.1f}% of income. Try aiming for 10–15%."
            )

    else:
        insights.append(
            "No investments detected. Even small monthly investments can make a big difference."
        )


    return insights