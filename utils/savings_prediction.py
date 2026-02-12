import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_savings(df, periods=3):

    monthly_data = (
        df.groupby(["year", "month_number", "transaction_type"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values(["year", "month_number"])
    )

    monthly_data["savings"] = (
        monthly_data.get("Income", 0) - monthly_data.get("Expense", 0)
    )

    if len(monthly_data) < 2:
        return None

    monthly_data["time_index"] = np.arange(len(monthly_data))

    X = monthly_data[["time_index"]]
    y = monthly_data["savings"]

    model = LinearRegression()
    model.fit(X, y)

    last_index = monthly_data["time_index"].max()

    future_indices = np.arange(last_index + 1, last_index + 1 + periods).reshape(-1, 1)
    predictions = model.predict(future_indices)

    return predictions
