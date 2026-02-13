import pandas as pd
from config import (
    BASE_HEALTH_SCORE,
    MAX_SAVINGS_CONTRIBUTION,
    MAX_LARGE_TXN_PENALTY,
    MAX_ANOMALY_PENALTY,
    MAX_CONCENTRATION_PENALTY
)


def calculate_financial_health_score(df):

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        return 0, {}

    savings = income - expense
    savings_ratio = savings / income

    # Cap savings ratio between -1 and 1
    savings_ratio = max(-1, min(1, savings_ratio))

    # Savings contribution
    savings_score = savings_ratio * MAX_SAVINGS_CONTRIBUTION

    # Large transaction penalty (proportional)
    total_expense_txn = df[df["transaction_type"] == "Expense"].shape[0]
    large_count = df[df["is_large"]].shape[0]

    if total_expense_txn > 0:
        large_ratio = large_count / total_expense_txn
    else:
        large_ratio = 0

    large_penalty = min(
        MAX_LARGE_TXN_PENALTY,
        large_ratio * MAX_LARGE_TXN_PENALTY
    )

    # Anomaly penalty (proportional)
    anomaly_count = df[df["is_anomaly"]].shape[0]

    if total_expense_txn > 0:
        anomaly_ratio = anomaly_count / total_expense_txn
    else:
        anomaly_ratio = 0

    anomaly_penalty = min(
        MAX_ANOMALY_PENALTY,
        anomaly_ratio * MAX_ANOMALY_PENALTY
    )

    # Concentration penalty
    expense_df = df[df["transaction_type"] == "Expense"]

    if expense > 0 and not expense_df.empty:
        category_expense = (
            expense_df.groupby("category")["amount"].sum()
        )
        top_category_ratio = category_expense.max() / expense
    else:
        top_category_ratio = 0

    concentration_penalty = min(
        MAX_CONCENTRATION_PENALTY,
        top_category_ratio * MAX_CONCENTRATION_PENALTY
    )

    final_score = (
        BASE_HEALTH_SCORE
        + savings_score
        - large_penalty
        - anomaly_penalty
        - concentration_penalty
    )

    final_score = max(0, min(100, round(final_score)))

    breakdown = {
        "Savings Ratio (%)": round(savings_ratio * 100, 2),
        "Large Transaction Ratio (%)": round(large_ratio * 100, 2),
        "Anomaly Ratio (%)": round(anomaly_ratio * 100, 2),
        "Top Category Concentration (%)": round(top_category_ratio * 100, 2)
    }

    return final_score, breakdown


def monthly_health_trend(df):

    monthly_groups = df.groupby(["year", "month_number"])

    trend_data = []

    for (year, month), group in monthly_groups:
        score, _ = calculate_financial_health_score(group)
        trend_data.append({
            "year": year,
            "month": month,
            "score": score
        })

    trend_df = pd.DataFrame(trend_data)
    trend_df = trend_df.sort_values(["year", "month"])

    return trend_df
