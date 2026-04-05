"""
utils/forecasting.py
====================
Improved forecasting using smoothing + linear regression.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from config import FORECAST_PERIODS, CONFIDENCE_MULTIPLIER


# ─────────────────────────────────────────────────────────────
# BUILD MONTHLY SERIES
# ─────────────────────────────────────────────────────────────

def build_monthly_series(df, category=None):
    data = df[df["transaction_type"] == "Expense"].copy()

    if category:
        data = data[data["category"] == category]

    if data.empty:
        return pd.DataFrame()

    monthly = (
        data.groupby(["year", "month_number"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month_number"])
    )

    monthly["year_month"] = (
        monthly["year"].astype(str) + "-" +
        monthly["month_number"].astype(str).str.zfill(2)
    )

    # Time index
    monthly["time_index"] = np.arange(len(monthly))

    # 🔥 NEW: smoothing (3-month moving avg)
    monthly["smoothed"] = monthly["amount"].rolling(3, min_periods=1).mean()

    return monthly


# ─────────────────────────────────────────────────────────────
# GENERATE FUTURE LABELS
# ─────────────────────────────────────────────────────────────

def get_future_months(last_year, last_month, periods):
    labels = []
    y, m = last_year, last_month

    for _ in range(periods):
        m += 1
        if m > 12:
            m = 1
            y += 1
        labels.append(f"{y}-{str(m).zfill(2)}")

    return labels


# ─────────────────────────────────────────────────────────────
# MAIN FORECAST FUNCTION
# ─────────────────────────────────────────────────────────────

def forecast_next_months(df, periods=None, category=None):

    if periods is None:
        periods = FORECAST_PERIODS

    monthly = build_monthly_series(df, category)

    if len(monthly) < 2:
        return None

    # Use smoothed values instead of raw
    X = monthly[["time_index"]]
    y = monthly["smoothed"]

    model = LinearRegression()
    model.fit(X, y)

    last_idx = int(monthly["time_index"].max())
    future_idx = np.arange(last_idx + 1, last_idx + 1 + periods).reshape(-1, 1)

    preds = model.predict(future_idx)

    # 🔥 Residual-based confidence
    residuals = y - model.predict(X)
    std = residuals.std()
    margin = CONFIDENCE_MULTIPLIER * std

    # Labels
    last_year = int(monthly["year"].iloc[-1])
    last_month = int(monthly["month_number"].iloc[-1])
    labels = get_future_months(last_year, last_month, periods)

    forecast_df = pd.DataFrame({
        "year_month": labels,
        "predicted_expense": np.maximum(0, preds),
        "lower_bound": np.maximum(0, preds - margin),
        "upper_bound": preds + margin,
    })

    return monthly, forecast_df