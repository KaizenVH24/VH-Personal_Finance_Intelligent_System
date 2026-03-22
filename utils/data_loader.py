"""
utils/data_loader.py
====================
Loads and normalises transaction data from CSV, Excel, or PDF.

PDF support
-----------
  • Generic table extractor  — works for HDFC, ICICI, Axis, Kotak, SBI,
                               Yes Bank, IndusInd, AU SFB, and any bank
                               that embeds proper PDF tables.
  • Auto-detection           — tries table extraction first; if no usable
                               table is found, falls back to Slice-style
                               text parser.

CSV / Excel support
-------------------
  • Flexible column aliasing — maps 50+ column name variants (particulars,
                               narration, debit, withdrawal, value date …)
                               to a canonical schema.
  • Split debit/credit cols  — handles banks that give separate Debit and
                               Credit columns instead of a signed Amount.
  • Multi-format dates       — auto-parses DD/MM/YYYY, MM/DD/YYYY,
                               DD-Mon-YY, ISO, etc.

Output schema (all callers depend on exactly these columns)
-----------------------------------------------------------
  date             datetime64[ns]
  description      str
  amount           float   (always positive)
  is_credit        bool    (True = money came in)
  balance          float   (NaN if unavailable)
"""

import re
import io
import logging
from typing import Optional

import pandas as pd
import numpy as np
import pdfplumber

from config import (
    DATE_ALIASES, DESCRIPTION_ALIASES, AMOUNT_ALIASES,
    DEBIT_ALIASES, CREDIT_ALIASES, BALANCE_ALIASES,
)

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# OUTPUT SCHEMA
# ══════════════════════════════════════════════════════════════════════════════

OUTPUT_COLUMNS = ["date", "description", "amount", "is_credit", "balance"]


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS: column normalisation
# ══════════════════════════════════════════════════════════════════════════════

def _normalise_col(name: str) -> str:
    """Strip, lower, collapse whitespace."""
    return re.sub(r"\s+", " ", str(name).strip().lower())


def _find_col(cols: list[str], aliases: set) -> Optional[str]:
    """Return the first column (raw) whose normalised form is in aliases."""
    for c in cols:
        if _normalise_col(c) in aliases:
            return c
    return None


def _find_col_partial(cols: list[str], aliases: set) -> Optional[str]:
    """Like _find_col but also matches if alias is a substring of the column."""
    for c in cols:
        norm = _normalise_col(c)
        for alias in aliases:
            if alias in norm or norm in alias:
                return c
    return None


def _clean_amount(series: pd.Series) -> pd.Series:
    """Remove currency symbols, commas, spaces; convert to float."""
    return (
        series.astype(str)
        .str.replace(r"[₹$€£,\s]", "", regex=True)
        .str.replace(r"\((.+?)\)", r"-\1", regex=True)   # (1234) → -1234
        .str.replace(r"[^0-9.\-]", "", regex=True)
        .replace("", np.nan)
        .pipe(pd.to_numeric, errors="coerce")
    )


def _parse_date_flexible(series: pd.Series) -> pd.Series:
    """Try multiple date formats; return datetime64 series."""
    # First attempt pandas auto-detection (handles ISO, many locale formats)
    result = pd.to_datetime(series, infer_datetime_format=True, errors="coerce")
    if result.notna().mean() > 0.8:
        return result

    # Explicit format attempts for common Indian bank date styles
    for fmt in [
        "%d/%m/%Y", "%d-%m-%Y", "%d %m %Y",
        "%d/%m/%y", "%d-%m-%y",
        "%d %b %Y", "%d-%b-%Y", "%d/%b/%Y",
        "%d %b '%y", "%d-%b-'%y",          # 04 Feb '26
        "%d %b %y", "%d-%b-%y",
        "%Y-%m-%d", "%Y/%m/%d",
        "%m/%d/%Y", "%m-%d-%Y",
    ]:
        attempt = pd.to_datetime(series, format=fmt, errors="coerce")
        if attempt.notna().mean() > 0.8:
            return attempt

    # Last resort: dayfirst=True
    return pd.to_datetime(series, dayfirst=True, errors="coerce")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS: final normalisation applied to all loaders
# ══════════════════════════════════════════════════════════════════════════════

def _finalise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and clean a DataFrame that already has the canonical columns.
    Ensures correct dtypes, removes invalid rows, deduplicates, sorts.
    """
    required = {"date", "description", "amount", "is_credit"}
    if not required.issubset(df.columns):
        missing = required - set(df.columns)
        raise ValueError(f"Internal error — missing columns after parsing: {missing}")

    df = df.copy()

    # ── date ──────────────────────────────────────────────────────
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # ── description ───────────────────────────────────────────────
    df["description"] = df["description"].astype(str).str.strip()
    df = df[df["description"].str.len() > 0]
    df = df[df["description"].str.lower() != "nan"]

    # ── amount ────────────────────────────────────────────────────
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] > 0]

    # ── is_credit ─────────────────────────────────────────────────
    df["is_credit"] = df["is_credit"].astype(bool)

    # ── balance ───────────────────────────────────────────────────
    if "balance" not in df.columns:
        df["balance"] = np.nan
    else:
        df["balance"] = pd.to_numeric(df["balance"], errors="coerce")

    # ── dedup and sort ────────────────────────────────────────────
    df = df.drop_duplicates(subset=["date", "description", "amount"])
    df = df.sort_values("date").reset_index(drop=True)

    return df[OUTPUT_COLUMNS]


# ══════════════════════════════════════════════════════════════════════════════
# PDF PARSER 1 — Generic table extractor (handles most Indian banks)
# ══════════════════════════════════════════════════════════════════════════════

_SKIP_HEADER_TOKENS = {
    "opening balance", "closing balance", "total", "subtotal",
    "brought forward", "carried forward", "page total",
    "statement of account", "account statement", "transaction summary",
}


def _is_data_row(row: list) -> bool:
    """Heuristic: row is likely a transaction if it contains a date-like string."""
    for cell in row:
        if cell and re.search(r"\d{2}[/-]\d{2}[/-]\d{2,4}", str(cell)):
            return True
        if cell and re.search(r"\d{1,2}\s+[A-Za-z]{3}\s+[''']?\d{2,4}", str(cell)):
            return True
    return False


def _table_to_df(table: list[list]) -> Optional[pd.DataFrame]:
    """Convert a pdfplumber table (list of rows) into a raw DataFrame."""
    if len(table) < 2:
        return None

    # Find the header row — first row that doesn't look like a data row
    header_idx = 0
    for i, row in enumerate(table):
        non_empty = [c for c in row if c and str(c).strip()]
        if not non_empty:
            continue
        if not _is_data_row(row):
            header_idx = i
            break

    header = [str(c).strip() if c else f"col_{j}" for j, c in enumerate(table[header_idx])]
    data_rows = table[header_idx + 1:]
    if not data_rows:
        return None

    # Skip rows that are clearly not transactions
    cleaned = []
    for row in data_rows:
        text = " ".join(str(c) for c in row if c).lower()
        if any(tok in text for tok in _SKIP_HEADER_TOKENS):
            continue
        if all(not c or not str(c).strip() for c in row):
            continue
        cleaned.append(row)

    if not cleaned:
        return None

    # Pad short rows to match header length
    n_cols = len(header)
    padded = [r + [None] * (n_cols - len(r)) if len(r) < n_cols else r[:n_cols]
              for r in cleaned]

    return pd.DataFrame(padded, columns=header)


def _map_table_columns(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Map raw table columns to the canonical schema.
    Handles both a single signed Amount column and separate Debit/Credit columns.
    Returns a df with [date, description, amount, is_credit, balance] or None.
    """
    cols = list(df.columns)

    date_col  = _find_col(cols, DATE_ALIASES) or _find_col_partial(cols, DATE_ALIASES)
    desc_col  = _find_col(cols, DESCRIPTION_ALIASES) or _find_col_partial(cols, DESCRIPTION_ALIASES)
    amt_col   = _find_col(cols, AMOUNT_ALIASES) or _find_col_partial(cols, AMOUNT_ALIASES)
    debit_col = _find_col(cols, DEBIT_ALIASES)  or _find_col_partial(cols, DEBIT_ALIASES)
    credit_col= _find_col(cols, CREDIT_ALIASES) or _find_col_partial(cols, CREDIT_ALIASES)
    bal_col   = _find_col(cols, BALANCE_ALIASES) or _find_col_partial(cols, BALANCE_ALIASES)

    if not date_col or not desc_col:
        return None

    out = pd.DataFrame()
    out["date"]        = df[date_col]
    out["description"] = df[desc_col]

    if amt_col and not (debit_col and credit_col):
        # Single amount column — derive is_credit from sign or use balance delta
        raw_amount = _clean_amount(df[amt_col])
        out["is_credit"] = raw_amount > 0
        out["amount"]    = raw_amount.abs()

    elif debit_col and credit_col:
        # Separate Debit / Credit columns (most common Indian bank format)
        debit  = _clean_amount(df[debit_col]).fillna(0)
        credit = _clean_amount(df[credit_col]).fillna(0)
        out["is_credit"] = credit > 0
        out["amount"]    = credit.where(credit > 0, debit)

    elif debit_col:
        out["is_credit"] = False
        out["amount"]    = _clean_amount(df[debit_col])
    elif credit_col:
        out["is_credit"] = True
        out["amount"]    = _clean_amount(df[credit_col])
    else:
        return None   # Can't determine amounts

    out["balance"] = _clean_amount(df[bal_col]) if bal_col else np.nan

    # Parse dates
    out["date"] = _parse_date_flexible(out["date"])

    return out


def _parse_pdf_tables(file) -> Optional[pd.DataFrame]:
    """
    Primary PDF parser: extracts tables using pdfplumber.
    Works for HDFC, ICICI, Axis, Kotak, SBI, Yes Bank, IndusInd, AU SFB.
    Returns None if no usable table is found.
    """
    all_frames = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                raw_df = _table_to_df(table)
                if raw_df is None or raw_df.empty:
                    continue
                mapped = _map_table_columns(raw_df)
                if mapped is not None and not mapped.empty:
                    all_frames.append(mapped)

    if not all_frames:
        return None

    combined = pd.concat(all_frames, ignore_index=True)
    # Drop rows where critical fields are NaN
    combined = combined.dropna(subset=["date", "amount"])
    return combined if not combined.empty else None


# ══════════════════════════════════════════════════════════════════════════════
# PDF PARSER 2 — Slice Small Finance Bank text layout
# ══════════════════════════════════════════════════════════════════════════════

_SLICE_DATE_RE  = re.compile(r"^(\d{2}\s+\w{3}\s+['']\d{2})\s+(.*)", re.UNICODE)
_SLICE_TXN_RE   = re.compile(
    r"(\d{12,18})\s+(-?₹[\d,]+(?:\.\d{1,2})?)\s+(₹[\d,]+(?:\.\d{1,2})?)\s*$",
    re.UNICODE,
)
_SLICE_SKIP = {
    "need help", "slice small finance", "opening balance", "total credits",
    "interest earned", "total debits", "closing balance", "generated on",
    "date", "ref no", "amount", "balance", "customer id", "phone", "email",
    "address", "nominee", "account", "ifsc", "micr", "branch",
    "account opening", "savings", "details",
}
_SLICE_PAGE_HDR  = re.compile(r"^\d+/\d+$")
_SLICE_DATE_RANGE= re.compile(r"^\d{2}\s+\w{3}\s+['']\d{2}\s+-\s+\d{2}\s+\w{3}\s+['']\d{2}$")


def _slice_skip(line: str) -> bool:
    low = line.lower()
    if _SLICE_PAGE_HDR.match(line) or _SLICE_DATE_RANGE.match(line):
        return True
    return any(tok in low for tok in _SLICE_SKIP)


def _slice_flush(date_raw: str, text: str) -> Optional[dict]:
    m = _SLICE_TXN_RE.search(text)
    if not m:
        return None
    try:
        amount  = float(m.group(2).replace("₹", "").replace(",", ""))
        balance = float(m.group(3).replace("₹", "").replace(",", ""))
        desc    = text[: m.start()].strip()
        ds = re.sub(r"['''](\d{2})$", r"20\1", date_raw.strip())
        date = pd.to_datetime(ds, format="%d %b %Y", errors="coerce")
        if pd.isna(date):
            return None
        return {
            "date":      date,
            "description": desc,
            "amount":    amount,
            "balance":   balance,
        }
    except (ValueError, TypeError):
        return None


def _parse_slice_pdf(file) -> Optional[pd.DataFrame]:
    """Slice SFB-specific text-based parser."""
    lines = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.split("\n"))

    rows, cur_date, cur_text = [], None, ""

    for raw in lines:
        line = raw.strip()
        if not line or _slice_skip(line):
            continue
        dm = _SLICE_DATE_RE.match(line)
        if dm:
            if cur_date:
                row = _slice_flush(cur_date, cur_text)
                if row:
                    rows.append(row)
            cur_date, cur_text = dm.group(1), dm.group(2)
        else:
            if cur_date:
                cur_text += " " + line

    if cur_date:
        row = _slice_flush(cur_date, cur_text)
        if row:
            rows.append(row)

    if not rows:
        return None

    df = pd.DataFrame(rows)
    # Slice stores signed amounts (negative = debit)
    df["is_credit"] = df["amount"] > 0
    df["amount"]    = df["amount"].abs()
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PDF PARSER 3 — Generic text fallback
# ══════════════════════════════════════════════════════════════════════════════

def _parse_pdf_text_fallback(file) -> Optional[pd.DataFrame]:
    """
    Last-resort text parser for PDFs that embed no proper tables.
    Heuristically looks for lines containing a date + number pattern.
    """
    rows = []
    date_pat = re.compile(
        r"(\d{2}[/-]\d{2}[/-]\d{2,4}|\d{2}\s+[A-Za-z]{3}\s+\d{2,4})"
        r"(.{5,80}?)"
        r"(-?[\d,]+\.\d{2})"
        r"\s+(-?[\d,]+\.\d{2})?",
        re.UNICODE,
    )

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                m = date_pat.search(line)
                if m:
                    try:
                        date = pd.to_datetime(m.group(1).strip(),
                                              infer_datetime_format=True,
                                              dayfirst=True,
                                              errors="coerce")
                        if pd.isna(date):
                            continue
                        desc   = m.group(2).strip()
                        amount = float(m.group(3).replace(",", ""))
                        bal    = float(m.group(4).replace(",", "")) if m.group(4) else np.nan
                        rows.append({
                            "date": date, "description": desc,
                            "amount": amount, "balance": bal,
                        })
                    except (ValueError, TypeError):
                        continue

    if not rows:
        return None

    df = pd.DataFrame(rows)
    df["is_credit"] = df["amount"] > 0
    df["amount"]    = df["amount"].abs()
    return df


# ══════════════════════════════════════════════════════════════════════════════
# CSV / EXCEL LOADER
# ══════════════════════════════════════════════════════════════════════════════

def _load_tabular(file, name: str) -> pd.DataFrame:
    """Load CSV or Excel into a DataFrame."""
    if name.endswith(".csv"):
        # Try common encodings
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                file.seek(0)
                return pd.read_csv(file, encoding=enc, thousands=",")
            except (UnicodeDecodeError, Exception):
                continue
        raise ValueError("Could not read CSV file — check file encoding.")

    elif name.endswith((".xlsx", ".xls")):
        file.seek(0)
        # Try all sheets; use the one with the most rows
        xl = pd.ExcelFile(file)
        best = pd.DataFrame()
        for sheet in xl.sheet_names:
            try:
                df = xl.parse(sheet, thousands=",")
                if len(df) > len(best):
                    best = df
            except Exception:
                continue
        if best.empty:
            raise ValueError("Excel file appears to be empty.")
        return best

    raise ValueError(f"Unsupported file type: {name}")


def _normalise_tabular(df: pd.DataFrame) -> pd.DataFrame:
    """
    Map raw CSV/Excel column names → canonical schema.
    Handles:
      - Single signed amount column
      - Split Debit / Credit columns
      - Many date / description column name variants
    """
    # Normalise column names
    df.columns = df.columns.str.strip()

    # Drop completely empty rows / columns
    df = df.dropna(how="all").dropna(axis=1, how="all")

    cols = list(df.columns)

    date_col  = _find_col(cols, DATE_ALIASES) or _find_col_partial(cols, DATE_ALIASES)
    desc_col  = _find_col(cols, DESCRIPTION_ALIASES) or _find_col_partial(cols, DESCRIPTION_ALIASES)
    amt_col   = _find_col(cols, AMOUNT_ALIASES)
    debit_col = _find_col(cols, DEBIT_ALIASES)  or _find_col_partial(cols, DEBIT_ALIASES)
    credit_col= _find_col(cols, CREDIT_ALIASES) or _find_col_partial(cols, CREDIT_ALIASES)
    bal_col   = _find_col(cols, BALANCE_ALIASES) or _find_col_partial(cols, BALANCE_ALIASES)

    # ── Provide helpful error messages ───────────────────────────────────────
    if not date_col:
        raise ValueError(
            "Could not find a date column.\n"
            f"Columns found: {cols}\n"
            "Expected one of: date, value date, txn date, transaction date, posting date …"
        )
    if not desc_col:
        raise ValueError(
            "Could not find a description/narration column.\n"
            f"Columns found: {cols}\n"
            "Expected one of: description, particulars, narration, details, remarks …"
        )

    has_split = debit_col and credit_col
    has_amount = bool(amt_col)

    if not has_split and not has_amount:
        # One last try — if there's exactly one numeric column, use it
        numeric_cols = [c for c in cols
                        if pd.to_numeric(df[c].astype(str)
                            .str.replace(r"[₹,\s]", "", regex=True),
                            errors="coerce").notna().mean() > 0.5
                        and c not in {date_col, desc_col, bal_col}]
        if len(numeric_cols) == 1:
            amt_col = numeric_cols[0]
            has_amount = True
        else:
            raise ValueError(
                "Could not find an amount column.\n"
                f"Columns found: {cols}\n"
                "Expected one of: amount, debit+credit, withdrawal+deposit …"
            )

    out = pd.DataFrame()
    out["date"]        = _parse_date_flexible(df[date_col].astype(str))
    out["description"] = df[desc_col].astype(str)

    if has_split:
        debit  = _clean_amount(df[debit_col]).fillna(0)
        credit = _clean_amount(df[credit_col]).fillna(0)
        out["is_credit"] = credit > 0
        out["amount"]    = credit.where(credit > 0, debit)
    else:
        raw_amount = _clean_amount(df[amt_col])
        out["is_credit"] = raw_amount > 0
        out["amount"]    = raw_amount.abs()

    out["balance"] = _clean_amount(df[bal_col]) if bal_col else np.nan

    return out


# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def load_data(file) -> pd.DataFrame:
    """
    Load transaction data from a CSV, Excel, or PDF bank statement.

    Returns a clean DataFrame with exactly these columns:
        date         datetime64[ns]
        description  str
        amount       float   (always positive)
        is_credit    bool    (True = money came in)
        balance      float   (NaN if unavailable)

    Raises ValueError with a user-friendly message on failure.
    """
    name = getattr(file, "name", "").lower()

    # ── PDF ───────────────────────────────────────────────────────────────────
    if name.endswith(".pdf"):
        raw = None

        # 1. Generic table extractor (most banks)
        try:
            file.seek(0)
            raw = _parse_pdf_tables(file)
        except Exception as e:
            logger.debug(f"Table extractor failed: {e}")

        # 2. Slice-specific text parser
        if raw is None or raw.empty:
            try:
                file.seek(0)
                raw = _parse_slice_pdf(file)
            except Exception as e:
                logger.debug(f"Slice parser failed: {e}")

        # 3. Generic text fallback
        if raw is None or raw.empty:
            try:
                file.seek(0)
                raw = _parse_pdf_text_fallback(file)
            except Exception as e:
                logger.debug(f"Text fallback failed: {e}")

        if raw is None or raw.empty:
            raise ValueError(
                "Could not extract transactions from this PDF.\n"
                "The file may be scanned (image-only), password-protected, "
                "or in an unsupported layout.\n"
                "Try exporting your bank statement as CSV instead."
            )

        return _finalise(raw)

    # ── CSV / Excel ───────────────────────────────────────────────────────────
    elif name.endswith((".csv", ".xlsx", ".xls")):
        raw_df = _load_tabular(file, name)
        mapped = _normalise_tabular(raw_df)
        return _finalise(mapped)

    else:
        raise ValueError(
            f"Unsupported file format '{name}'.\n"
            "Upload a PDF, CSV (.csv), or Excel (.xlsx / .xls) bank statement."
        )