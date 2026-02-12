import numpy as np
from config import BIG_TRANSACTION_MULTIPLIER

def detect_large_transactions(df):

    mean = df["amount"].mean()
    std = df["amount"].std()

    threshold = mean + BIG_TRANSACTION_MULTIPLIER * std

    df["is_large"] = np.where(df["amount"] > threshold, True, False)

    return df, threshold
