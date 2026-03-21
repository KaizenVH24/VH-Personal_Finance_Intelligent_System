"""
recurring.py
Detects recurring transactions — subscriptions, EMIs, regular transfers.

A transaction is considered recurring if:
  • Amount matches within ±RECURRING_AMOUNT_TOLERANCE (%)
  • Merchant/description is the same
  • Appears at least RECURRING_MIN_OCCURRENCES times
  • Optionally, occurs on similar calendar days (within RECURRING_DAY_WINDOW)
"""

import pandas as pd
from config import (
    RECURRING_AMOUNT_TOLERANCE,
    RECURRING_MIN_OCCURRENCES,
    RECURRING_DAY_WINDOW,
)


def detect_recurring(df) -> pd.DataFrame:
    """
    Returns a summary DataFrame of detected recurring transactions.

    Columns: merchant, category, amount, frequency, first_seen, last_seen,
             likely_day, transaction_type
    """
    if df.empty:
        return pd.DataFrame()

    expenses = df[df["transaction_type"] == "Expense"].copy()
    if expenses.empty:
        return pd.DataFrame()

    # Group by merchant and look for similar amounts
    records = []

    for merchant, group in expenses.groupby("merchant"):
        if len(group) < RECURRING_MIN_OCCURRENCES:
            continue

        # Sort by amount to find clusters
        group = group.sort_values("amount")
        amounts = group["amount"].values

        i = 0
        while i < len(amounts):
            anchor = amounts[i]
            lo     = anchor * (1 - RECURRING_AMOUNT_TOLERANCE)
            hi     = anchor * (1 + RECURRING_AMOUNT_TOLERANCE)

            cluster_mask = (amounts >= lo) & (amounts <= hi)
            cluster      = group[cluster_mask]

            if len(cluster) >= RECURRING_MIN_OCCURRENCES:
                days = cluster["date"].dt.day
                likely_day = int(days.mode().iloc[0]) if not days.mode().empty else None

                # Check if transactions are roughly periodic (not all on the same day)
                unique_months = cluster["year_month"].nunique()
                if unique_months >= RECURRING_MIN_OCCURRENCES:
                    records.append({
                        "merchant":        merchant,
                        "category":        cluster["category"].mode().iloc[0],
                        "amount":          round(float(cluster["amount"].mean()), 2),
                        "frequency":       len(cluster),
                        "months_active":   unique_months,
                        "first_seen":      cluster["date"].min().date(),
                        "last_seen":       cluster["date"].max().date(),
                        "likely_day":      likely_day,
                        "transaction_type": "Expense",
                    })
                # Advance past this cluster
                i = int(cluster_mask.sum()) + (i - cluster_mask[:i].sum())
                continue
            i += 1

    if not records:
        return pd.DataFrame()

    result = (
        pd.DataFrame(records)
        .drop_duplicates(subset=["merchant", "amount"])
        .sort_values("amount", ascending=False)
        .reset_index(drop=True)
    )
    return result


def monthly_recurring_total(recurring_df: pd.DataFrame) -> float:
    """Estimated monthly committed spend from detected recurring transactions."""
    if recurring_df.empty:
        return 0.0
    return float(recurring_df["amount"].sum())