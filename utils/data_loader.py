import pandas as pd

def load_data(file):
    df = pd.read_csv(file)

    # Standardizing column names
    df.columns = df.columns.str.strip().str.lower()

    required_columns = ["date", "description", "amount"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Convert date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove invalid dates
    df = df.dropna(subset=["date"])

    # Clean description
    df["description"] = df["description"].astype(str).str.lower()

    # Ensure amount is numeric
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    return df
