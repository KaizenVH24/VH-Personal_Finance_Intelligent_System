def categorize_transaction(description):

    categories = {
        "Food": ["swiggy", "zomato", "mcdonald", "dominos", "restaurant"],
        "Shopping": ["amazon", "flipkart", "myntra"],
        "Travel": ["uber", "ola", "irctc", "petrol"],
        "Bills": ["electricity", "water", "gas", "bill", "recharge"],
        "Entertainment": ["netflix", "hotstar", "movie"],
        "Salary": ["salary"],
    }

    for category, keywords in categories.items():
        for word in keywords:
            if word in description:
                return category

    return "Others"


def apply_categorization(df):
    df["category"] = df["description"].apply(categorize_transaction)
    return df

def assign_transaction_type(df):

    df["transaction_type"] = df["category"].apply(
        lambda x: "Income" if x == "Salary" else "Expense"
    )

    return df