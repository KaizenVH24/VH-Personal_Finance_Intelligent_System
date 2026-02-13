import pandas as pd


def load_data(file):
    """
    Load and clean transaction CSV data.
    Ensures data integrity before processing.
    """

    df = pd.read_csv(file)

    # -----------------------------
    # Standardize column names
    # -----------------------------
    df.columns = df.columns.str.strip().str.lower()

    required_columns = ["date", "description", "amount"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # -----------------------------
    # Clean Date Column
    # -----------------------------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # -----------------------------
    # Clean Description Column
    # -----------------------------
    df["description"] = (
        df["description"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------
    # Clean Amount Column
    # Remove currency symbols and commas
    # -----------------------------
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", "", regex=True)
        .str.replace("₹", "", regex=True)
        .str.strip()
    )

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    # -----------------------------
    # Remove Duplicate Rows
    # -----------------------------
    df = df.drop_duplicates()

    # -----------------------------
    # Sort Chronologically
    # -----------------------------
    df = df.sort_values("date").reset_index(drop=True)

    return df
