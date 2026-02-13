import numpy as np
from sklearn.ensemble import IsolationForest
from config import BIG_TRANSACTION_MULTIPLIER, ANOMALY_CONTAMINATION


def detect_large_transactions(df):
    """
    Detect large transactions using statistical threshold.
    Applied only on Expense transactions to avoid salary distortion.
    """

    expense_df = df[df["transaction_type"] == "Expense"]

    if expense_df.empty:
        df["is_large"] = False
        return df, 0

    mean = expense_df["amount"].mean()
    std = expense_df["amount"].std()

    threshold = mean + BIG_TRANSACTION_MULTIPLIER * std

    df["is_large"] = (
        (df["transaction_type"] == "Expense") &
        (df["amount"] > threshold)
    )

    return df, threshold


def detect_anomalies(df):
    """
    Detect anomalies using Isolation Forest.
    Applied only on Expense transactions.
    """

    expense_df = df[df["transaction_type"] == "Expense"]

    if len(expense_df) < 5:
        df["is_anomaly"] = False
        return df

    model = IsolationForest(
        n_estimators=100,
        contamination=ANOMALY_CONTAMINATION,
        random_state=42
    )

    amount_data = expense_df[["amount"]]

    model.fit(amount_data)

    predictions = model.predict(amount_data)

    df["is_anomaly"] = False
    df.loc[expense_df.index, "is_anomaly"] = predictions == -1

    return df
