"""
utils/forecasting.py
====================
Linear trend forecasting for monthly expenses (total or per category).
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config import FORECAST_PERIODS, CONFIDENCE_MULTIPLIER


def _build_monthly_series(df: pd.DataFrame, category: str | None = None) -> pd.DataFrame:
    subset = df[df["transaction_type"] == "Expense"].copy()
    if category:
        subset = subset[subset["category"] == category]
    if subset.empty:
        return pd.DataFrame()

    monthly = (
        subset
        .groupby(["year", "month_number"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month_number"])
    )
    monthly["year_month"]  = (
        monthly["year"].astype(str) + "-" +
        monthly["month_number"].astype(str).str.zfill(2)
    )
    monthly["time_index"] = np.arange(len(monthly))
    return monthly


def _next_months(last_year: int, last_month: int, n: int) -> list[str]:
    labels = []
    y, m = last_year, last_month
    for _ in range(n):
        m += 1
        if m > 12:
            m, y = 1, y + 1
        labels.append(f"{y}-{str(m).zfill(2)}")
    return labels


def forecast_next_months(
    df: pd.DataFrame,
    periods: int | None = None,
    category: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame] | None:
    """
    Forecast monthly expenses using linear regression.

    Returns (historical_df, forecast_df) or None if insufficient data.

    forecast_df columns: year_month, predicted_expense, lower_bound, upper_bound
    """
    if periods is None:
        periods = FORECAST_PERIODS

    monthly = _build_monthly_series(df, category)
    if len(monthly) < 2:
        return None

    X = monthly[["time_index"]]
    y = monthly["amount"]

    model = LinearRegression().fit(X, y)
    last_idx   = int(monthly["time_index"].max())
    future_idx = np.arange(last_idx + 1, last_idx + 1 + periods).reshape(-1, 1)
    preds      = model.predict(future_idx)

    std_err = (y - model.predict(X)).std()
    margin  = CONFIDENCE_MULTIPLIER * std_err

    labels = _next_months(
        int(monthly["year"].iloc[-1]),
        int(monthly["month_number"].iloc[-1]),
        periods,
    )

    forecast_df = pd.DataFrame({
        "year_month":        labels,
        "predicted_expense": np.maximum(0, preds),
        "lower_bound":       np.maximum(0, preds - margin),
        "upper_bound":       preds + margin,
    })
    return monthly, forecast_df