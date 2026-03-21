"""
categorizer.py
Turns raw bank descriptions into clean merchant names and categories.

Handles:
  • UPI Debit/Credit strings (most common in Indian statements)
  • NEFT / IMPS transfers
  • Opaque alphanumeric codes
  • Plain text descriptions (monies transfer, Repayment, etc.)
"""

import re
from config import MERCHANT_MAP


# ── UPI description dissection ──────────────────────────────────────────────

_UPI_RE = re.compile(
    r"UPI\s+(?:Debit|Credit)[-–\s]+(.+?)[-–\s]+[\w.\-]+@[\w]+",
    re.IGNORECASE | re.UNICODE,
)
_NEFT_RE = re.compile(
    r"(?:NEFT|IMPS)\s+(?:Credit|Debit)[-–\s]+(.+?)[-–\s]",
    re.IGNORECASE,
)


def _extract_entity_name(description: str) -> str:
    """Pull the human-readable entity name out of a UPI / NEFT description."""
    m = _UPI_RE.search(description)
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


def _clean_entity_name(raw: str) -> str:
    """Turn 'NITIN A ZADPE' or 'Mr Om Sanjay Shikare' into a tidy display name."""
    # Remove honorifics
    raw = re.sub(r"^(Mr|Mrs|Ms|Dr|Prof)\.?\s+", "", raw, flags=re.IGNORECASE)
    # Title-case and strip
    return raw.strip().title()


def categorize_transaction(description: str) -> tuple[str, str]:
    """
    Return (merchant_display_name, category) for a raw bank description.

    Priority:
    1. Match full description against MERCHANT_MAP
    2. Extract entity name from UPI/NEFT, then match again
    3. Use cleaned entity name with category 'Others'
    """
    # 1. Try full description first (catches 'monies transfer', 'repayment', etc.)
    name, cat = _apply_merchant_map(description)
    if name:
        return name, cat

    # 2. Extract entity and try again
    entity = _extract_entity_name(description)
    if entity and entity != description:
        name, cat = _apply_merchant_map(entity)
        if name:
            return name, cat
        # Also try UPI handle (sometimes the merchant is in the handle, e.g. amzn0026...)
        handle_match = re.search(r"([\w.\-]+)@[\w]+", description, re.IGNORECASE)
        if handle_match:
            name, cat = _apply_merchant_map(handle_match.group(1))
            if name:
                return name, cat

    # 3. Opaque alphanumeric description — return cleaned entity name
    if entity and entity != description:
        return _clean_entity_name(entity), "Others"

    # 4. Short generic entries
    desc_lower = description.lower().strip()
    if desc_lower in ("", "-", "nan"):
        return "Unknown", "Others"

    return description.strip().title()[:40], "Others"


def apply_categorization(df):
    """Add 'merchant' and 'category' columns to the dataframe."""
    results = df["description"].apply(categorize_transaction)
    df["merchant"]  = results.apply(lambda x: x[0])
    df["category"]  = results.apply(lambda x: x[1])
    return df


def assign_transaction_type(df):
    """
    Add 'transaction_type' column.

    Rule:
      is_credit=True  → Income
      is_credit=False → Expense  (EMI/Loan and Investments are still expenses — money left)
    Simple, correct, and consistent with how bank statements work.
    """
    df["transaction_type"] = df["is_credit"].map({True: "Income", False: "Expense"})
    return df