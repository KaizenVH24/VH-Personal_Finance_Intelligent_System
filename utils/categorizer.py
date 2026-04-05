"""
utils/categorizer.py
====================
Improved transaction categorization with robust text cleaning.
"""

import re
import pandas as pd
from config import MERCHANT_MAP


# ─────────────────────────────────────────────────────────────
# NEW: Normalization layer (BIG upgrade)
# ─────────────────────────────────────────────────────────────

def normalize_description(desc: str) -> str:
    """
    Clean messy transaction strings like:
    AMZN/US/12345 → amzn us
    UPI-XYZ@okaxis → xyz
    """
    if not desc:
        return ""

    desc = str(desc).lower()

    # Remove UPI handles
    desc = re.sub(r"[\w\.-]+@[\w]+", " ", desc)

    # Replace special chars with space
    desc = re.sub(r"[^a-z\s]", " ", desc)

    # Remove extra spaces
    desc = re.sub(r"\s+", " ", desc)

    return desc.strip()


# ─────────────────────────────────────────────────────────────
# EXISTING REGEX (kept, slightly improved)
# ─────────────────────────────────────────────────────────────

_UPI_RE = re.compile(
    r"UPI[\s\-/]+(?:Debit|Credit|DR|CR)[\s\-/]+(.+?)[\s\-/]+[\w.\-]+@[\w]+",
    re.IGNORECASE,
)

_UPI_HANDLE_RE = re.compile(r"([\w.\-]+)@[\w]+", re.IGNORECASE)


def _extract_entity_name(description: str) -> str:
    m = _UPI_RE.search(description)
    if m:
        return m.group(1).strip()
    return description


# ─────────────────────────────────────────────────────────────
# MERCHANT MAP MATCHING
# ─────────────────────────────────────────────────────────────

def _apply_merchant_map(text: str):
    lower = text.lower()
    for pattern, (name, cat) in MERCHANT_MAP.items():
        if re.search(pattern, lower):
            return name, cat
    return None, None


# ─────────────────────────────────────────────────────────────
# NEW: Fallback keyword-based categorization
# ─────────────────────────────────────────────────────────────

KEYWORDS = {
    "Shopping": ["amazon", "amzn", "flipkart", "myntra"],
    "Food": ["swiggy", "zomato", "restaurant", "cafe"],
    "Travel": ["uber", "ola", "rapido", "petrol"],
    "Entertainment": ["netflix", "spotify", "youtube"],
}


def fallback_category(desc: str):
    for cat, words in KEYWORDS.items():
        if any(word in desc for word in words):
            return cat
    return "Others"


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def categorize_transaction(description: str):
    if not description or str(description).strip().lower() in ("", "nan", "-"):
        return "Unknown", "Others"

    raw_desc = str(description).strip()

    # 1. Try full raw description
    name, cat = _apply_merchant_map(raw_desc)
    if name:
        return name, cat

    # 2. Extract entity
    entity = _extract_entity_name(raw_desc)

    # 3. Normalize (NEW STEP 🔥)
    clean_desc = normalize_description(entity)

    # 4. Try merchant map again
    name, cat = _apply_merchant_map(clean_desc)
    if name:
        return name, cat

    # 5. Try UPI handle
    handle_match = _UPI_HANDLE_RE.search(raw_desc)
    if handle_match:
        handle = normalize_description(handle_match.group(1))
        name, cat = _apply_merchant_map(handle)
        if name:
            return name, cat

    # 6. Fallback keyword categorization
    fallback_cat = fallback_category(clean_desc)

    # 7. Final fallback name
    cleaned_name = clean_desc.title()[:40] if clean_desc else "Unknown"

    return cleaned_name, fallback_cat


# ─────────────────────────────────────────────────────────────
# APPLY FUNCTIONS
# ─────────────────────────────────────────────────────────────

def apply_categorization(df: pd.DataFrame) -> pd.DataFrame:
    results = df["description"].apply(categorize_transaction)
    df = df.copy()
    df["merchant"] = results.apply(lambda x: x[0])
    df["category"] = results.apply(lambda x: x[1])
    return df


def assign_transaction_type(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transaction_type"] = df["is_credit"].map({
        True: "Income",
        False: "Expense"
    })
    return df