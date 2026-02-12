def calculate_financial_health_score(df):

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        return 0, {}

    savings = income - expense
    savings_ratio = savings / income

    # Savings Score (40 points)
    savings_score = max(0, min(40, savings_ratio * 40))

    # Large transaction penalty (15 points)
    large_count = df[df["is_large"] == True].shape[0]
    large_penalty = min(15, large_count * 2)

    # Anomaly penalty (20 points)
    anomaly_count = df[df["is_anomaly"] == True].shape[0]
    anomaly_penalty = min(20, anomaly_count * 3)

    # Expense concentration risk (15 points)
    category_expense = (
        df[df["transaction_type"] == "Expense"]
        .groupby("category")["amount"]
        .sum()
    )

    if len(category_expense) > 0:
        top_category_ratio = category_expense.max() / expense
    else:
        top_category_ratio = 0

    concentration_penalty = min(15, top_category_ratio * 15)

    # Stability factor (10 points)
    stability_score = 10 if savings_ratio > 0.2 else 5 if savings_ratio > 0 else 0

    final_score = (
        savings_score
        + stability_score
        - large_penalty
        - anomaly_penalty
        - concentration_penalty
    )

    final_score = max(0, min(100, round(final_score)))

    breakdown = {
        "Savings Ratio": round(savings_ratio * 100, 2),
        "Large Transactions": large_count,
        "Anomalies": anomaly_count,
        "Top Category Ratio": round(top_category_ratio * 100, 2)
    }

    return final_score, breakdown
