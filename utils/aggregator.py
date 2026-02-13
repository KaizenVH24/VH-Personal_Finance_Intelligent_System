import pandas as pd


def add_time_features(df):
    """
    Add time-based features for aggregation and forecasting.
    """

    df["year"] = df["date"].dt.year
    df["month_number"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.month_name()

    # Year-Month string for display
    df["year_month"] = df["date"].dt.to_period("M").astype(str)

    # ISO week handling
    df["week"] = df["date"].dt.isocalendar().week
    df["year_week"] = (
        df["year"].astype(str) + "-W" + df["week"].astype(str)
    )

    return df


def monthly_summary(df):
    """
    Aggregate monthly data.
    """

    return (
        df.groupby(["year", "month_number", "year_month", "category"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month_number"])
    )


def yearly_summary(df):
    """
    Aggregate yearly data.
    """

    return (
        df.groupby(["year", "category"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year"])
    )
