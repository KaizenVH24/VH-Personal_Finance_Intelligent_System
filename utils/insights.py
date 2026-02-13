import numpy as np


def generate_insights(df):

    insights = []

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income == 0:
        insights.append("No income detected in dataset. Financial health cannot be fully assessed.")
        return insights

    savings = income - expense
    savings_ratio = savings / income

    # --- Savings Insight ---
    if savings_ratio > 0.3:
        insights.append(f"Strong savings rate at {round(savings_ratio*100,2)}%. Financial discipline is excellent.")
    elif savings_ratio > 0.1:
        insights.append(f"Moderate savings rate at {round(savings_ratio*100,2)}%. There is room for optimization.")
    elif savings_ratio > 0:
        insights.append(f"Low savings rate at {round(savings_ratio*100,2)}%. Consider reducing discretionary spending.")
    else:
        insights.append("Expenses exceed income. Immediate financial restructuring recommended.")

    # --- Category Concentration ---
    expense_df = df[df["transaction_type"] == "Expense"]

    if not expense_df.empty:
        category_expense = (
            expense_df.groupby("category")["amount"].sum()
        )

        top_category = category_expense.idxmax()
        top_ratio = category_expense.max() / expense

        insights.append(
            f"Highest spending category is '{top_category}' "
            f"({round(top_ratio*100,2)}% of total expenses)."
        )

        if top_ratio > 0.5:
            insights.append("Spending concentration risk detected. Diversification recommended.")
    else:
        insights.append("No expense data available for category analysis.")

    # --- Anomaly Insight ---
    anomaly_count = df[df["is_anomaly"]].shape[0]
    total_expense_txn = expense_df.shape[0]

    if total_expense_txn > 0:
        anomaly_ratio = anomaly_count / total_expense_txn
    else:
        anomaly_ratio = 0

    if anomaly_ratio > 0.1:
        insights.append("High anomaly frequency detected. Transaction behavior appears irregular.")
    elif anomaly_ratio > 0:
        insights.append(f"{anomaly_count} unusual transaction(s) detected. Review recommended.")
    else:
        insights.append("No anomalous transaction behavior detected.")

    # --- Large Transaction Insight ---
    large_count = df[df["is_large"]].shape[0]

    if large_count > 0:
        insights.append(f"{large_count} statistically large transaction(s) identified.")

    # --- Stability Insight ---
    monthly_savings = (
        df.groupby(["year", "month_number", "transaction_type"])["amount"]
        .sum()
        .unstack(fill_value=0)
    )

    if not monthly_savings.empty:
        monthly_savings["savings"] = (
            monthly_savings.get("Income", 0) -
            monthly_savings.get("Expense", 0)
        )

        if monthly_savings["savings"].std() > 0:
            volatility = monthly_savings["savings"].std()
            insights.append(
                f"Monthly savings volatility detected (Std Dev: ₹ {round(volatility,2)})."
            )

    return insights
