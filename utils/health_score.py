import pandas as pd

def calculate_financial_health_score(df):

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        return 0, {}

    savings = income - expense
    savings_ratio = savings / income

    # Base score starts at 50
    base_score = 50

    # Savings contribution (up to +30)
    savings_score = savings_ratio * 30

    # Large transaction penalty (max -10)
    large_count = df[df["is_large"] == True].shape[0]
    large_penalty = min(10, large_count)

    # Anomaly penalty (max -10)
    anomaly_count = df[df["is_anomaly"] == True].shape[0]
    anomaly_penalty = min(10, anomaly_count)

    # Concentration penalty (max -10)
    category_expense = (
        df[df["transaction_type"] == "Expense"]
        .groupby("category")["amount"]
        .sum()
    )

    if len(category_expense) > 0:
        top_category_ratio = category_expense.max() / expense
    else:
        top_category_ratio = 0

    concentration_penalty = min(10, top_category_ratio * 10)

    final_score = base_score + savings_score - large_penalty - anomaly_penalty - concentration_penalty

    final_score = max(0, min(100, round(final_score)))

    breakdown = {
        "Savings Ratio": round(savings_ratio * 100, 2),
        "Large Transactions": large_count,
        "Anomalies": anomaly_count,
        "Top Category Ratio": round(top_category_ratio * 100, 2)
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