import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config import FORECAST_PERIODS, CONFIDENCE_MULTIPLIER


def predict_savings(df, periods=None):
    """
    Forecast future monthly savings using linear regression.
    Returns historical savings and forecast dataframe.
    """

    if periods is None:
        periods = FORECAST_PERIODS

    monthly_data = (
        df.groupby(["year", "month_number", "transaction_type"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values(["year", "month_number"])
    )

    if monthly_data.empty or len(monthly_data) < 2:
        return None

    # Ensure both columns exist
    income_series = monthly_data.get("Income", 0)
    expense_series = monthly_data.get("Expense", 0)

    monthly_data["savings"] = income_series - expense_series

    monthly_data["time_index"] = np.arange(len(monthly_data))

    X = monthly_data[["time_index"]]
    y = monthly_data["savings"]

    model = LinearRegression()
    model.fit(X, y)

    last_index = monthly_data["time_index"].max()

    future_indices = np.arange(
        last_index + 1,
        last_index + 1 + periods
    ).reshape(-1, 1)

    predictions = model.predict(future_indices)

    # Confidence interval
    residuals = y - model.predict(X)
    std_error = residuals.std()

    lower_bound = predictions - (CONFIDENCE_MULTIPLIER * std_error)
    upper_bound = predictions + (CONFIDENCE_MULTIPLIER * std_error)

    forecast_df = pd.DataFrame({
        "future_index": future_indices.flatten(),
        "predicted_savings": predictions,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    })

    return monthly_data, forecast_df
