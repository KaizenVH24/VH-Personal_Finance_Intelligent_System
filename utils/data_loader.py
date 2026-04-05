"""
utils/data_loader.py
====================
Clean and debuggable data loader for CSV, Excel, and PDF files.
"""

import pandas as pd
import numpy as np
import pdfplumber
import re

from config import (
    DATE_ALIASES, DESCRIPTION_ALIASES, AMOUNT_ALIASES,
    DEBIT_ALIASES, CREDIT_ALIASES, BALANCE_ALIASES,
)


# ─────────────────────────────────────────────────────────────
# BASIC CLEANERS
# ─────────────────────────────────────────────────────────────

def clean_amount(series):
    return (
        series.astype(str)
        .str.replace(r"[₹,\s]", "", regex=True)
        .str.replace(r"\((.+?)\)", r"-\1", regex=True)
        .str.replace(r"[^0-9.\-]", "", regex=True)
        .replace("", np.nan)
        .astype(float)
    )


def parse_date(series):
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def normalize_col(name):
    return str(name).strip().lower()


# ─────────────────────────────────────────────────────────────
# COLUMN DETECTION
# ─────────────────────────────────────────────────────────────

def find_column(cols, aliases):
    for col in cols:
        if normalize_col(col) in aliases:
            return col
    return None


# ─────────────────────────────────────────────────────────────
# CSV / EXCEL LOADER
# ─────────────────────────────────────────────────────────────

def load_tabular(file, name):
    if name.endswith(".csv"):
        return pd.read_csv(file)

    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(file)

    else:
        raise ValueError("Unsupported file")


def process_tabular(df):
    df.columns = [normalize_col(c) for c in df.columns]

    print("Detected columns:", df.columns.tolist())

    date_col = find_column(df.columns, DATE_ALIASES)
    desc_col = find_column(df.columns, DESCRIPTION_ALIASES)
    amt_col = find_column(df.columns, AMOUNT_ALIASES)
    debit_col = find_column(df.columns, DEBIT_ALIASES)
    credit_col = find_column(df.columns, CREDIT_ALIASES)
    bal_col = find_column(df.columns, BALANCE_ALIASES)

    if not date_col or not desc_col:
        raise ValueError("Missing required columns (date/description)")

    result = pd.DataFrame()

    result["date"] = parse_date(df[date_col])
    result["description"] = df[desc_col].astype(str)

    # Handle amount
    if debit_col and credit_col:
        debit = clean_amount(df[debit_col]).fillna(0)
        credit = clean_amount(df[credit_col]).fillna(0)

        result["is_credit"] = credit > 0
        result["amount"] = credit.where(credit > 0, debit)

    elif amt_col:
        raw = clean_amount(df[amt_col])
        result["is_credit"] = raw > 0
        result["amount"] = raw.abs()

    else:
        raise ValueError("No amount column found")

    result["balance"] = clean_amount(df[bal_col]) if bal_col else np.nan

    return result


# ─────────────────────────────────────────────────────────────
# SIMPLE PDF LOADER (CLEAN VERSION)
# ─────────────────────────────────────────────────────────────

def load_pdf(file):
    rows = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    if len(row) < 3:
                        continue

                    rows.append(row)

    if not rows:
        raise ValueError("Could not extract data from PDF")

    df = pd.DataFrame(rows)

    # Try basic mapping
    df.columns = df.iloc[0]
    df = df[1:]

    return process_tabular(df)


# ─────────────────────────────────────────────────────────────
# FINAL CLEANING
# ─────────────────────────────────────────────────────────────

def finalize(df):
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    df["description"] = df["description"].str.strip()
    df = df[df["description"] != ""]

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").abs()
    df = df[df["amount"] > 0]

    df["is_credit"] = df["is_credit"].astype(bool)

    df = df.drop_duplicates(subset=["date", "description", "amount"])
    df = df.sort_values("date").reset_index(drop=True)

    return df


# ─────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────────────────────

def load_data(file):
    name = file.name.lower()

    if name.endswith(".pdf"):
        df = load_pdf(file)

    elif name.endswith((".csv", ".xlsx", ".xls")):
        raw = load_tabular(file, name)
        df = process_tabular(raw)

    else:
        raise ValueError("Unsupported file format")

    return finalize(df)