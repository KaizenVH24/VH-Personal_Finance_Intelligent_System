"""
data_loader.py
Loads and normalises transaction data from CSV, Excel, or PDF.

PDF parser is calibrated for Slice Small Finance Bank statements:
  - Columns: DATE | DETAILS (multi-line) | REF NO. | AMOUNT | BALANCE
  - Date format: 04 Feb '26
  - Signed amounts: positive = credit, negative = debit
"""

import re
import io
import pandas as pd
import pdfplumber


# ── internal helpers ────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^(\d{2}\s+\w{3}\s+['']\d{2})\s+(.*)", re.UNICODE)

# Matches the tail of a transaction block: ref_no  ±₹amount  ₹balance
_TXN_END_RE = re.compile(
    r"(\d{12,18})\s+(-?₹[\d,]+(?:\.\d{1,2})?)\s+(₹[\d,]+(?:\.\d{1,2})?)\s*$",
    re.UNICODE,
)

_SKIP_TOKENS = {
    "need help", "slice small finance", "opening balance", "total credits",
    "interest earned", "total debits", "closing balance", "generated on",
    "date", "ref no", "amount", "balance", "customer id", "phone", "email",
    "address", "nominee", "account", "ifsc", "micr", "branch", "account opening",
    "savings", "details",
}

_PAGE_HEADER_RE = re.compile(r"^\d+/\d+$")
_DATE_RANGE_RE  = re.compile(r"^\d{2}\s+\w{3}\s+['']\d{2}\s+-\s+\d{2}\s+\w{3}\s+['']\d{2}$")


def _should_skip(line: str) -> bool:
    low = line.lower()
    if _PAGE_HEADER_RE.match(line) or _DATE_RANGE_RE.match(line):
        return True
    return any(tok in low for tok in _SKIP_TOKENS)


def _flush_txn(date_raw: str, text: str) -> dict | None:
    m = _TXN_END_RE.search(text)
    if not m:
        return None
    try:
        amount  = float(m.group(2).replace("₹", "").replace(",", ""))
        balance = float(m.group(3).replace("₹", "").replace(",", ""))
        desc    = text[: m.start()].strip()
        # '26 → 2026 (handles both straight and typographic apostrophes)
        ds = re.sub(r"['''](\d{2})$", r"20\1", date_raw.strip())
        date = pd.to_datetime(ds, format="%d %b %Y", errors="coerce")
        if pd.isna(date):
            return None
        return {"date": date, "description": desc, "amount": amount, "balance": balance}
    except (ValueError, TypeError):
        return None


def _parse_slice_pdf(file) -> pd.DataFrame:
    """Parse Slice bank statement PDF into a raw transactions DataFrame."""
    lines = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))

    rows = []
    cur_date: str | None = None
    cur_text: str = ""

    for raw in lines:
        line = raw.strip()
        if not line or _should_skip(line):
            continue

        dm = _DATE_RE.match(line)
        if dm:
            if cur_date:
                row = _flush_txn(cur_date, cur_text)
                if row:
                    rows.append(row)
            cur_date = dm.group(1)
            cur_text = dm.group(2)
        else:
            if cur_date:
                cur_text += " " + line

    # Don't lose the last transaction
    if cur_date:
        row = _flush_txn(cur_date, cur_text)
        if row:
            rows.append(row)

    return pd.DataFrame(rows) if rows else pd.DataFrame(
        columns=["date", "description", "amount", "balance"]
    )


# ── public interface ────────────────────────────────────────────────────────

def load_data(file) -> pd.DataFrame:
    """
    Load transaction data from CSV, Excel, or PDF (Slice format).

    Returns a clean DataFrame with columns:
        date          datetime64[ns]
        description   str
        amount        float   (absolute value)
        is_credit     bool    (True = money came in)
        balance       float   (optional, may be NaN for CSV/Excel)
    """
    name = file.name.lower() if hasattr(file, "name") else ""

    if name.endswith(".pdf"):
        df = _parse_slice_pdf(file)

    elif name.endswith(".csv"):
        df = pd.read_csv(file)

    elif name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)

    else:
        raise ValueError(
            f"Unsupported file format. Upload a PDF, CSV, or Excel file."
        )

    # ── normalise column names ───────────────────────────────────
    df.columns = df.columns.str.strip().str.lower()

    required = {"date", "description", "amount"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(
            f"File is missing required columns: {', '.join(sorted(missing))}. "
            f"Expected: date, description, amount."
        )

    # ── clean date ───────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # ── clean description ────────────────────────────────────────
    df["description"] = df["description"].astype(str).str.strip()
    df = df[df["description"].str.len() > 0]

    # ── clean amount ─────────────────────────────────────────────
    if df["amount"].dtype == object:
        df["amount"] = (
            df["amount"]
            .astype(str)
            .str.replace(r"[₹,\s]", "", regex=True)
            .str.replace(r"\((.+)\)", r"-\1", regex=True)   # (123) → -123
        )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] != 0]

    # ── derive credit flag, then make amount absolute ────────────
    df["is_credit"] = df["amount"] > 0
    df["amount"]    = df["amount"].abs()

    # ── ensure balance column exists ─────────────────────────────
    if "balance" not in df.columns:
        df["balance"] = float("nan")
    else:
        df["balance"] = pd.to_numeric(
            df["balance"].astype(str).str.replace(r"[₹,\s]", "", regex=True),
            errors="coerce",
        )

    # ── dedup and sort ───────────────────────────────────────────
    df = df.drop_duplicates(subset=["date", "description", "amount"])
    df = df.sort_values("date").reset_index(drop=True)

    return df