"""
utils/health_score.py
=====================
Composite 0-100 financial health score with a breakdown of contributing factors.

Formula
-------
  score = BASE + savings_contribution − risk_penalties   → clamped [0, 100]

  savings_contribution  = up to MAX_SAVINGS_CONTRIBUTION (full at ≥ 30% savings rate)
  risk_penalties        = large_txn_penalty + anomaly_penalty + concentration_penalty
"""

import pandas as pd
from config import (
    BASE_HEALTH_SCORE,
    MAX_SAVINGS_CONTRIBUTION,
    MAX_LARGE_TXN_PENALTY,
    MAX_ANOMALY_PENALTY,
    MAX_CONCENTRATION_PENALTY,
)


def calculate_financial_health_score(df: pd.DataFrame) -> tuple[int, dict]:
    """
    Returns (score: int, breakdown: dict).
    score is clamped to [0, 100].
    """
    income  = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        return 0, {"note": "No income detected — score cannot be computed."}

    # ── savings contribution ──────────────────────────────────────
    savings_ratio = max(-1.0, min(1.0, (income - expense) / income))
    savings_score = min(
        MAX_SAVINGS_CONTRIBUTION,
        (savings_ratio / 0.30) * MAX_SAVINGS_CONTRIBUTION,
    )

    # ── large transaction penalty ─────────────────────────────────
    expense_txns = df[df["transaction_type"] == "Expense"]
    n_expense    = len(expense_txns)
    large_ratio  = df.get("is_large", pd.Series(False, index=df.index)).sum() / n_expense if n_expense else 0
    large_penalty= min(MAX_LARGE_TXN_PENALTY, large_ratio * MAX_LARGE_TXN_PENALTY)

    # ── anomaly penalty ───────────────────────────────────────────
    anomaly_ratio  = df.get("is_anomaly", pd.Series(False, index=df.index)).sum() / n_expense if n_expense else 0
    anomaly_penalty= min(MAX_ANOMALY_PENALTY, anomaly_ratio * MAX_ANOMALY_PENALTY)

    # ── concentration penalty ─────────────────────────────────────
    if expense > 0 and not expense_txns.empty:
        top_ratio = expense_txns.groupby("category")["amount"].sum().max() / expense
    else:
        top_ratio = 0
    concentration_penalty = min(MAX_CONCENTRATION_PENALTY, top_ratio * MAX_CONCENTRATION_PENALTY)

    raw_score   = BASE_HEALTH_SCORE + savings_score - large_penalty - anomaly_penalty - concentration_penalty
    final_score = int(max(0, min(100, round(raw_score))))

    breakdown = {
        "Savings Ratio":              f"{savings_ratio * 100:.1f}%",
        "Large Transaction Ratio":    f"{large_ratio * 100:.1f}%",
        "Anomaly Ratio":              f"{anomaly_ratio * 100:.1f}%",
        "Top Category Concentration": f"{top_ratio * 100:.1f}%",
        "Savings Score":              f"+{savings_score:.1f}",
        "Risk Penalties":             f"-{large_penalty + anomaly_penalty + concentration_penalty:.1f}",
    }
    return final_score, breakdown


def monthly_health_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the health score for each calendar month in the dataset.
    Anomaly / large flags are taken from the already-computed dataset-wide columns.
    """
    records = []
    for (year, month), group in df.groupby(["year", "month_number"]):
        score, _ = calculate_financial_health_score(group)
        records.append({
            "year":       year,
            "month":      month,
            "year_month": group["year_month"].iloc[0],
            "score":      score,
        })
    if not records:
        return pd.DataFrame(columns=["year", "month", "year_month", "score"])
    return pd.DataFrame(records).sort_values(["year", "month"])