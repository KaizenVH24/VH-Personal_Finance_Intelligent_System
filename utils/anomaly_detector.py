import numpy as np
from sklearn.ensemble import IsolationForest
from config import BIG_TRANSACTION_MULTIPLIER


def detect_large_transactions(df):

    mean = df["amount"].mean()
    std = df["amount"].std()
    threshold = mean + BIG_TRANSACTION_MULTIPLIER * std

    df["is_large"] = np.where(df["amount"] > threshold, True, False)

    return df, threshold


def detect_anomalies(df):

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    amount_data = df[["amount"]]

    model.fit(amount_data)

    df["anomaly"] = model.predict(amount_data)

    # -1 means anomaly, 1 means normal
    df["is_anomaly"] = df["anomaly"].apply(lambda x: True if x == -1 else False)

    return df
