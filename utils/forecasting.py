import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def prepare_monthly_expense_data(df, category=None):

    expense_df = df[df["transaction_type"] == "Expense"]

    if category:
        expense_df = expense_df[expense_df["category"] == category]

    monthly_expense = (
        expense_df
        .groupby(["year", "month_number"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month_number"])
    )

    monthly_expense["time_index"] = np.arange(len(monthly_expense))

    return monthly_expense


def forecast_next_months(df, periods=3, category=None):

    monthly_data = prepare_monthly_expense_data(df, category)

    if len(monthly_data) < 2:
        return None

    X = monthly_data[["time_index"]]
    y = monthly_data["amount"]

    model = LinearRegression()
    model.fit(X, y)

    last_index = monthly_data["time_index"].max()

    future_indices = np.arange(last_index + 1, last_index + 1 + periods).reshape(-1, 1)

    predictions = model.predict(future_indices)

    # Confidence interval (basic std-based band)
    residuals = y - model.predict(X)
    std_error = residuals.std()

    lower_bound = predictions - (1.96 * std_error)
    upper_bound = predictions + (1.96 * std_error)

    forecast_df = pd.DataFrame({
        "future_index": future_indices.flatten(),
        "predicted_expense": predictions,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    })

    return monthly_data, forecast_df
