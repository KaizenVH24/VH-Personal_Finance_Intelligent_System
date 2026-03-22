"""
utils/categorizer.py
====================
Turns raw bank descriptions into clean merchant names and categories.

Handles:
  • UPI Debit/Credit strings  — most common in Indian statements
  • NEFT / IMPS transfers
  • Opaque alphanumeric codes  — e.g. "NEFT/RTGS000123456"
  • Plain-text descriptions    — e.g. "Loan Repayment", "Bill Payment"
  • UPI handles                — extracts merchant from VPA (e.g. amzn0026@axisbank)
"""

import re
import pandas as pd
from config import MERCHANT_MAP


# ── Regex patterns for UPI / NEFT / IMPS strings ─────────────────────────────

_UPI_RE = re.compile(
    r"UPI[\s\-/]+(?:Debit|Credit|DR|CR)[\s\-/]+(.+?)[\s\-/]+[\w.\-]+@[\w]+",
    re.IGNORECASE | re.UNICODE,
)
_UPI_TO_RE = re.compile(
    r"UPI(?:[\s\-/]+\w+)*[\s\-/]+(?:to|from|by)[\s\-/]+(.+?)[\s\-/@]",
    re.IGNORECASE | re.UNICODE,
)
_NEFT_RE = re.compile(
    r"(?:NEFT|IMPS|RTGS)[\s\-/]+(?:Credit|Debit|CR|DR)?[\s\-/]+(.+?)(?:[\s\-/]|$)",
    re.IGNORECASE,
)
_UPI_HANDLE_RE = re.compile(r"([\w.\-]+)@[\w]+", re.IGNORECASE)


def _extract_entity_name(description: str) -> str:
    """Pull the human-readable entity name from a UPI / NEFT description."""
    m = _UPI_RE.search(description)
    if m:
        return m.group(1).strip()
    m = _UPI_TO_RE.search(description)
    if m:
        return m.group(1).strip()
    m = _NEFT_RE.search(description)
    if m:
        return m.group(1).strip()
    return description


def _apply_merchant_map(text: str) -> tuple[str, str]:
    """
    Match text against MERCHANT_MAP patterns.
    Returns (display_name, category) or (None, None) if no match.
    """
    lower = text.lower()
    for pattern, (name, cat) in MERCHANT_MAP.items():
        if re.search(pattern, lower):
            return name, cat
    return None, None


def _clean_person_name(raw: str) -> str:
    """
    Tidy up person names from UPI: 'NITIN A ZADPE' → 'Nitin A Zadpe'.
    Strips honorifics and excess whitespace.
    """
    raw = re.sub(r"^(Mr|Mrs|Ms|Dr|Prof)\.?\s+", "", raw, flags=re.IGNORECASE)
    # Remove trailing noise: numbers, ref codes
    raw = re.sub(r"[\s_\-]+\d+$", "", raw).strip()
    return raw.strip().title()[:40]


def categorize_transaction(description: str) -> tuple[str, str]:
    """
    Return (merchant_display_name, category) for a raw bank description.

    Resolution order:
    1. Full description → MERCHANT_MAP                   (catches bill payments, etc.)
    2. Extracted entity → MERCHANT_MAP                   (catches UPI merchant names)
    3. UPI handle       → MERCHANT_MAP                   (e.g. amzn@axisbank → Amazon)
    4. Cleaned entity name, category = 'Others'          (personal transfers)
    5. Fallback: truncated, title-cased description
    """
    if not description or str(description).strip().lower() in ("", "nan", "-"):
        return "Unknown", "Others"

    desc = str(description).strip()

    # 1. Try full description
    name, cat = _apply_merchant_map(desc)
    if name:
        return name, cat

    # 2. Extract entity and try
    entity = _extract_entity_name(desc)
    if entity and entity != desc:
        name, cat = _apply_merchant_map(entity)
        if name:
            return name, cat

        # 3. Try from UPI handle (VPA)
        handle_m = _UPI_HANDLE_RE.search(desc)
        if handle_m:
            name, cat = _apply_merchant_map(handle_m.group(1))
            if name:
                return name, cat

        # 4. Personal name transfer
        return _clean_person_name(entity), "Others"

    # 5. Generic fallback — clean up the description itself
    # Remove ref numbers / numeric suffixes
    cleaned = re.sub(r"\b\d{8,}\b", "", desc).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned[:40].strip().title() or "Unknown", "Others"


def apply_categorization(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'merchant' and 'category' columns to the DataFrame."""
    results = df["description"].apply(categorize_transaction)
    df = df.copy()
    df["merchant"] = results.apply(lambda x: x[0])
    df["category"] = results.apply(lambda x: x[1])
    return df


def assign_transaction_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'transaction_type' column.

    is_credit=True  → Income
    is_credit=False → Expense

    Note: Investments and EMI/Loans are still Expenses — money leaving the account.
    """
    df = df.copy()
    df["transaction_type"] = df["is_credit"].map({True: "Income", False: "Expense"})
    return df