import pandas as pd

def add_time_features(df):

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["month_number"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week

    # Ensure chronological month order
    df["month"] = pd.Categorical(
        df["month"],
        categories=[
            "January", "February", "March", "April",
            "May", "June", "July", "August",
            "September", "October", "November", "December"
        ],
        ordered=True
    )

    return df


def monthly_summary(df):
    return (
        df.groupby(["year", "month", "month_number", "category"])["amount"]
        .sum()
        .reset_index()
        .sort_values(["year", "month_number"])
    )


def yearly_summary(df):
    return (
        df.groupby(["year", "category"])["amount"]
        .sum()
        .reset_index()
    )
