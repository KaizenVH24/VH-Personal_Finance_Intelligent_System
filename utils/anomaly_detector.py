"""
utils/anomaly_detector.py
=========================
Statistical + ML-based detection of unusual expense transactions.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from config import BIG_TRANSACTION_MULTIPLIER, ANOMALY_CONTAMINATION


def detect_large_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """
    Flag expenses that exceed mean + k×std as statistically large.

    Returns (df_with_is_large_col, threshold_value).
    """
    df = df.copy()
    expenses = df[df["transaction_type"] == "Expense"]["amount"]

    if expenses.empty or expenses.std() == 0:
        df["is_large"] = False
        return df, 0.0

    threshold = expenses.mean() + BIG_TRANSACTION_MULTIPLIER * expenses.std()
    df["is_large"] = (
        (df["transaction_type"] == "Expense") &
        (df["amount"] > threshold)
    )
    return df, float(threshold)


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use Isolation Forest to detect behavioural anomalies in expense patterns.
    Requires at least 10 expense rows to be meaningful.
    """
    df = df.copy()
    expense_df = df[df["transaction_type"] == "Expense"]

    if len(expense_df) < 10:
        df["is_anomaly"] = False
        return df

    # Feature: amount + day-of-month (if available)
    features = expense_df[["amount"]].copy()
    if "day" in expense_df.columns:
        features["day"] = expense_df["day"].astype(float)

    model = IsolationForest(
        n_estimators=100,
        contamination=ANOMALY_CONTAMINATION,
        random_state=42,
    )
    preds = model.fit_predict(features)

    df["is_anomaly"] = False
    df.loc[expense_df.index, "is_anomaly"] = (preds == -1)
    return df