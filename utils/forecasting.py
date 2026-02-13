import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from config import FORECAST_PERIODS, CONFIDENCE_MULTIPLIER


def prepare_monthly_expense_data(df, category=None):
    """
    Aggregates monthly expense data.
    Optionally filters by category.
    """

    expense_df = df[df["transaction_type"] == "Expense"]

    if category:
        expense_df = expense_df[expense_df["category"] == category]

    if expense_df.empty:
        return pd.DataFrame()

    monthly_expense = (
        expense_df
        .groupby(["year", "month_number"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month_number"])
    )

    # Create display-friendly year_month
    monthly_expense["year_month"] = (
        monthly_expense["year"].astype(str)
        + "-"
        + monthly_expense["month_number"].astype(str).str.zfill(2)
    )


    # Create continuous time index for regression
    monthly_expense["time_index"] = np.arange(len(monthly_expense))

    return monthly_expense


def forecast_next_months(df, periods=None, category=None):
    """
    Forecast future expenses using linear regression.
    Returns historical data and forecast dataframe.
    """

    if periods is None:
        periods = FORECAST_PERIODS

    monthly_data = prepare_monthly_expense_data(df, category)

    if len(monthly_data) < 2:
        return None

    X = monthly_data[["time_index"]]
    y = monthly_data["amount"]

    model = LinearRegression()
    model.fit(X, y)

    last_index = monthly_data["time_index"].max()

    future_indices = np.arange(
        last_index + 1,
        last_index + 1 + periods
    ).reshape(-1, 1)

    predictions = model.predict(future_indices)

    # Residual-based confidence interval
    residuals = y - model.predict(X)
    std_error = residuals.std()

    lower_bound = predictions - (CONFIDENCE_MULTIPLIER * std_error)
    upper_bound = predictions + (CONFIDENCE_MULTIPLIER * std_error)

    # Generate proper future year_month labels
    last_year = monthly_data["year"].iloc[-1]
    last_month = monthly_data["month_number"].iloc[-1]

    future_years = []
    future_months = []

    year = last_year
    month = last_month

    for _ in range(periods):
        month += 1
        if month > 12:
            month = 1
            year += 1

        future_years.append(year)
        future_months.append(month)

    future_year_month = [
        f"{y}-{str(m).zfill(2)}"
        for y, m in zip(future_years, future_months)
    ]

    forecast_df = pd.DataFrame({
        "year_month": future_year_month,
        "predicted_expense": predictions,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    })


    return monthly_data, forecast_df
