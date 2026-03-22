"""
utils/recurring.py
==================
Detects recurring transactions — subscriptions, EMIs, regular transfers.

A transaction is considered recurring if:
  • Merchant/description is the same
  • Amount matches within ±RECURRING_AMOUNT_TOLERANCE (%)
  • Appears in at least RECURRING_MIN_OCCURRENCES distinct calendar months
"""

import pandas as pd
from config import (
    RECURRING_AMOUNT_TOLERANCE,
    RECURRING_MIN_OCCURRENCES,
)


def detect_recurring(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a summary DataFrame of detected recurring transactions.

    Columns: merchant, category, amount, frequency, months_active,
             first_seen, last_seen, likely_day, transaction_type
    """
    if df.empty:
        return pd.DataFrame()

    expenses = df[df["transaction_type"] == "Expense"].copy()
    if expenses.empty:
        return pd.DataFrame()

    records = []

    for merchant, group in expenses.groupby("merchant"):
        if len(group) < RECURRING_MIN_OCCURRENCES:
            continue

        group   = group.sort_values("amount")
        amounts = group["amount"].values
        visited = set()

        for i in range(len(amounts)):
            if i in visited:
                continue

            anchor = amounts[i]
            lo, hi = anchor * (1 - RECURRING_AMOUNT_TOLERANCE), anchor * (1 + RECURRING_AMOUNT_TOLERANCE)

            cluster_indices = [j for j, a in enumerate(amounts) if lo <= a <= hi]
            cluster         = group.iloc[cluster_indices]

            if len(cluster) < RECURRING_MIN_OCCURRENCES:
                visited.update(cluster_indices)
                continue

            unique_months = cluster["year_month"].nunique()
            if unique_months < RECURRING_MIN_OCCURRENCES:
                visited.update(cluster_indices)
                continue

            days       = cluster["date"].dt.day
            likely_day = int(days.mode().iloc[0]) if not days.mode().empty else None

            records.append({
                "merchant":         merchant,
                "category":         cluster["category"].mode().iloc[0],
                "amount":           round(float(cluster["amount"].mean()), 2),
                "frequency":        len(cluster),
                "months_active":    unique_months,
                "first_seen":       cluster["date"].min().date(),
                "last_seen":        cluster["date"].max().date(),
                "likely_day":       likely_day,
                "transaction_type": "Expense",
            })
            visited.update(cluster_indices)

    if not records:
        return pd.DataFrame()

    return (
        pd.DataFrame(records)
        .drop_duplicates(subset=["merchant", "amount"])
        .sort_values("amount", ascending=False)
        .reset_index(drop=True)
    )


def monthly_recurring_total(recurring_df: pd.DataFrame) -> float:
    """Estimated monthly committed spend from detected recurring transactions."""
    if recurring_df.empty:
        return 0.0
    return float(recurring_df["amount"].sum())