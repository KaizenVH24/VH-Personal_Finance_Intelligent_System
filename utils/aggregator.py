"""
aggregator.py
Adds time-based features and provides aggregation helpers.
"""

import pandas as pd


def add_time_features(df):
    df["year"]         = df["date"].dt.year
    df["month_number"] = df["date"].dt.month
    df["month_name"]   = df["date"].dt.month_name()
    df["year_month"]   = df["date"].dt.to_period("M").astype(str)
    df["week"]         = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"]  = df["date"].dt.day_name()
    df["day"]          = df["date"].dt.day
    return df


def monthly_category_summary(df) -> pd.DataFrame:
    """Monthly spend per category (expenses only)."""
    expenses = df[df["transaction_type"] == "Expense"]
    return (
        expenses
        .groupby(["year_month", "category"])["amount"]
        .sum()
        .reset_index()
        .sort_values("year_month")
    )


def merchant_summary(df, top_n: int = 10) -> pd.DataFrame:
    """Top N merchants by total spend (expenses only)."""
    expenses = df[df["transaction_type"] == "Expense"]
    return (
        expenses
        .groupby("merchant")["amount"]
        .sum()
        .reset_index()
        .sort_values("amount", ascending=False)
        .head(top_n)
    )


def monthly_cashflow(df) -> pd.DataFrame:
    """Monthly income and expense totals, with net savings."""
    pivot = (
        df.groupby(["year_month", "transaction_type"])["amount"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    pivot["Income"]  = pivot.get("Income",  0)
    pivot["Expense"] = pivot.get("Expense", 0)
    pivot["Savings"] = pivot["Income"] - pivot["Expense"]
    return pivot.sort_values("year_month")