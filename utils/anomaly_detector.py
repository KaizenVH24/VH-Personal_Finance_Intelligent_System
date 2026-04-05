"""
utils/anomaly_detector.py
=========================
Improved anomaly detection using better feature engineering.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from config import BIG_TRANSACTION_MULTIPLIER, ANOMALY_CONTAMINATION


# ─────────────────────────────────────────────────────────────
# LARGE TRANSACTION DETECTION (same but cleaner)
# ─────────────────────────────────────────────────────────────

def detect_large_transactions(df: pd.DataFrame):
    """
    Flag transactions larger than mean + k * std
    """
    df = df.copy()
    expenses = df[df["transaction_type"] == "Expense"]["amount"]

    if expenses.empty or expenses.std() == 0:
        df["is_large"] = False
        return df, 0.0

    mean = expenses.mean()
    std = expenses.std()

    threshold = mean + BIG_TRANSACTION_MULTIPLIER * std

    df["is_large"] = (
        (df["transaction_type"] == "Expense") &
        (df["amount"] > threshold)
    )

    return df, float(threshold)


# ─────────────────────────────────────────────────────────────
# ANOMALY DETECTION (UPGRADED 🔥)
# ─────────────────────────────────────────────────────────────

def detect_anomalies(df: pd.DataFrame):
    """
    Improved anomaly detection using:
    - amount
    - log(amount)
    - day of month
    """

    df = df.copy()
    expense_df = df[df["transaction_type"] == "Expense"]

    # Not enough data → skip
    if len(expense_df) < 10:
        df["is_anomaly"] = False
        return df

    features = pd.DataFrame(index=expense_df.index)

    # Feature 1: amount
    features["amount"] = expense_df["amount"]

    # Feature 2: log amount (VERY IMPORTANT)
    features["log_amount"] = np.log1p(features["amount"])

    # Feature 3: day of month (behavior pattern)
    if "day" in expense_df.columns:
        features["day"] = expense_df["day"].astype(float)
    else:
        features["day"] = 0

    # Optional normalization (makes model stable)
    features = (features - features.mean()) / (features.std() + 1e-6)

    # Model
    model = IsolationForest(
        n_estimators=150,                 # slightly higher → better detection
        contamination=ANOMALY_CONTAMINATION,
        random_state=42,
    )

    preds = model.fit_predict(features)

    df["is_anomaly"] = False
    df.loc[expense_df.index, "is_anomaly"] = (preds == -1)

    return df