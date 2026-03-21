"""
anomaly_detector.py
Statistical + ML-based detection of unusual expense transactions.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from config import BIG_TRANSACTION_MULTIPLIER, ANOMALY_CONTAMINATION


def detect_large_transactions(df):
    """
    Flag expenses that exceed mean + k*std as statistically large.
    Returns df with 'is_large' column, plus the threshold value.
    """
    expenses = df[df["transaction_type"] == "Expense"]["amount"]

    if expenses.empty:
        df["is_large"] = False
        return df, 0.0

    threshold = expenses.mean() + BIG_TRANSACTION_MULTIPLIER * expenses.std()

    df["is_large"] = (
        (df["transaction_type"] == "Expense") &
        (df["amount"] > threshold)
    )
    return df, float(threshold)


def detect_anomalies(df):
    """
    Use Isolation Forest to detect behavioural anomalies in expense patterns.
    Applied only to expenses; needs at least 10 rows to be meaningful.
    """
    expense_df = df[df["transaction_type"] == "Expense"]

    if len(expense_df) < 10:
        df["is_anomaly"] = False
        return df

    features = expense_df[["amount"]].copy()

    model = IsolationForest(
        n_estimators=100,
        contamination=ANOMALY_CONTAMINATION,
        random_state=42,
    )
    preds = model.fit_predict(features)

    df["is_anomaly"] = False
    df.loc[expense_df.index, "is_anomaly"] = preds == -1

    return df