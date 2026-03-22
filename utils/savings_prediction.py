"""
utils/savings_prediction.py
============================
Forecasts future monthly savings using linear regression.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config import FORECAST_PERIODS, CONFIDENCE_MULTIPLIER


def predict_savings(
    df: pd.DataFrame,
    periods: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """
    Returns (historical_df, forecast_df) or None if insufficient data.

    historical_df has a 'savings' column.
    forecast_df columns: year_month, predicted_savings, lower_bound, upper_bound
    """
    if periods is None:
        periods = FORECAST_PERIODS

    pivot = (
        df.groupby(["year", "month_number", "transaction_type"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
        .sort_values(["year", "month_number"])
    )

    if len(pivot) < 2:
        return None

    pivot["savings"]     = pivot.get("Income", 0) - pivot.get("Expense", 0)
    pivot["time_index"]  = np.arange(len(pivot))
    pivot["year_month"]  = (
        pivot["year"].astype(str) + "-" +
        pivot["month_number"].astype(str).str.zfill(2)
    )

    X = pivot[["time_index"]]
    y = pivot["savings"]

    model = LinearRegression().fit(X, y)

    last_idx   = int(pivot["time_index"].max())
    future_idx = np.arange(last_idx + 1, last_idx + 1 + periods).reshape(-1, 1)
    preds      = model.predict(future_idx)
    std_err    = (y - model.predict(X)).std()
    margin     = CONFIDENCE_MULTIPLIER * std_err

    last_year  = int(pivot["year"].iloc[-1])
    last_month = int(pivot["month_number"].iloc[-1])
    labels     = []
    y_, m_     = last_year, last_month
    for _ in range(periods):
        m_ += 1
        if m_ > 12:
            m_, y_ = 1, y_ + 1
        labels.append(f"{y_}-{str(m_).zfill(2)}")

    forecast_df = pd.DataFrame({
        "year_month":        labels,
        "predicted_savings": preds,
        "lower_bound":       preds - margin,
        "upper_bound":       preds + margin,
    })
    return pivot, forecast_df