import re
from config import CATEGORY_KEYWORDS


def categorize_transaction(description):
    """
    Categorize transaction based on keyword matching.
    Uses case-insensitive whole-word matching.
    """

    description = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, description):
                return category

    return "Others"


def apply_categorization(df):
    df["category"] = df["description"].apply(categorize_transaction)
    return df


def assign_transaction_type(df):
    """
    Assign transaction type based on category and amount.
    """

    def determine_type(row):
        if row["category"] == "Salary":
            return "Income"
        elif row["amount"] < 0:
            return "Income"  # Refunds treated as income
        else:
            return "Expense"

    df["transaction_type"] = df.apply(determine_type, axis=1)
    return df
