def generate_insights(df):

    insights = []

    income = df[df["transaction_type"] == "Income"]["amount"].sum()
    expense = df[df["transaction_type"] == "Expense"]["amount"].sum()

    if income > expense:
        insights.append("You are saving more than you spend. Good financial discipline.")
    else:
        insights.append("Your expenses exceed income. Immediate optimization needed.")

    top_category = (
        df[df["transaction_type"] == "Expense"]
        .groupby("category")["amount"]
        .sum()
        .idxmax()
    )

    insights.append(f"Highest spending category is {top_category}.")

    anomaly_count = df[df["is_anomaly"] == True].shape[0]

    if anomaly_count > 0:
        insights.append(f"{anomaly_count} unusual transactions detected.")
    else:
        insights.append("No suspicious activity detected.")

    return insights
