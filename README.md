# Personal Finance Intelligent System (PFIS)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_Dashboard-red)
![ML](https://img.shields.io/badge/ML-IsolationForest-green)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange)
![Status](https://img.shields.io/badge/Status-VH_v4.0-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> Personal Finance Intelligent System — AI & ML-Powered Financial Intelligence Dashboard  
> Engineered with discipline and analytical precision — **VH24 aka Vinay Hulsurkar**

---

## Executive Summary

PFIS is a modular, end-to-end financial analytics platform that transforms raw bank transaction data into structured intelligence, risk insights, predictive forecasts, and executive-ready reports.

It is not a static dashboard. It is a financial intelligence engine — built around real Indian bank statement formats, real UPI transaction noise, and real spending behavior. Every module is independently testable, every parameter is config-driven, and every output is traceable back to a data decision.

Core capabilities:

- Multi-format ingestion — PDF, CSV, Excel
- Intelligent merchant normalisation from messy UPI strings
- Unsupervised ML anomaly detection via Isolation Forest
- Composite financial health scoring (0–100)
- Recurring transaction and subscription detection
- Predictive expense and savings forecasting with confidence intervals
- Per-category budget tracking with alerts
- Goal-based savings tracker
- Automated insight generation
- Executive PDF report export

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│                  UI Layer                        │
│          Streamlit — app.py                      │
│   Overview · Transactions · Categories ·         │
│   Forecast · Goals                               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│             Business Logic Layer                 │
│                  utils/                          │
│                                                  │
│  data_loader      categorizer    aggregator      │
│  anomaly_detector health_score   recurring       │
│  forecasting      savings_pred   insights        │
│  report_generator                                │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         Statistical & ML Layer                   │
│   Isolation Forest · Linear Regression           │
│   Statistical Thresholding · Rule Heuristics     │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│          Configuration Layer                     │
│                config.py                         │
│  All thresholds, weights, budgets, merchant map  │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│            Data Input Layer                      │
│       PDF · CSV · Excel (.xlsx / .xls)           │
└─────────────────────────────────────────────────┘
```

This layered separation ensures the UI layer never contains business logic, the ML layer never touches the config, and every module can be swapped or extended independently.

---

## File Format Support

PFIS accepts three input formats natively:

**PDF bank statements**
The PDF parser is calibrated for the specific layout used by Indian savings account statements — multi-line UPI descriptions wrapped across rows, signed rupee amounts, date format `04 Feb '26`, and a five-column structure of DATE | DETAILS | REF NO. | AMOUNT | BALANCE. The parser reconstructs split description lines, strips page headers and footers, and handles both straight and typographic apostrophes in year notation.

**CSV**
Any bank CSV export with `date`, `description`, and `amount` columns. Amount can be signed (negative = debit) or unsigned — the parser infers direction from sign. Rupee symbols, commas, and whitespace in amount strings are cleaned automatically.

**Excel (.xlsx / .xls)**
Same column requirements as CSV. Multi-sheet workbooks are handled — only the first sheet is read.

---

## Core System Capabilities

### 1 — Transaction Intelligence Engine

**Ingestion and cleaning**
- Required column enforcement with descriptive error messages
- Currency symbol and comma stripping from amount fields
- `(123)` parenthesis-format negative number support
- Date parsing with `errors="coerce"` and null row removal
- Deduplication on date + description + amount
- Chronological sorting

**Merchant normalisation**
This was the most significant upgrade from v1. Raw UPI strings look like:

```
UPI Debit-ZOMATO LIMITED-zomato-order@ptbl-YESB0PTMUPI-155524826119-Zomato Payment
UPI Debit-NITIN A ZADPE-amzn0026735883@apl-604291961603
UPI Debit-Mr Om Sanjay Shikare-omshikare7077@okaxis-603568388030-Payment from slice
```

The categoriser extracts the entity name from the UPI string using a regex that isolates the human-readable segment between `UPI Debit/Credit-` and the UPI handle. It then applies the merchant map from `config.py`. If the entity name does not match, the UPI handle itself is checked — which catches opaque codes like `amzn0026735883@apl` mapping to Amazon. Over 50 Indian merchants are pre-mapped covering food, shopping, travel, entertainment, bills, investments, and loans.

**Transaction type assignment**
Based solely on the `is_credit` flag derived from amount sign. Positive amount = Income, negative = Expense. This correctly handles all bank statement conventions — no guessing based on category names.

**Time feature engineering**
- `year`, `month_number`, `month_name`
- `year_month` period string for grouping
- `week`, `day_of_week`, `day` for behavioural analysis

---

### 2 — Anomaly and Risk Detection

**Large transaction detection**

```
threshold = mean(expenses) + k × std(expenses)
```

`k` is configurable via `BIG_TRANSACTION_MULTIPLIER` in `config.py`. Applied only to expense transactions to prevent salary credits from distorting the mean. Flags stored in `is_large` boolean column.

**Isolation Forest anomaly detection**

Scikit-learn's `IsolationForest` applied to expense amounts only. Requires a minimum of 10 expense transactions to be meaningful. Contamination rate configurable via `ANOMALY_CONTAMINATION`. Flags stored in `is_anomaly` boolean column. These flags feed directly into the health score penalty calculations.

---

### 3 — Financial Health Scoring Engine (0–100)

```
Final Score = BASE_HEALTH_SCORE
            + savings_contribution      (up to +40)
            - large_transaction_penalty (up to -20)
            - anomaly_penalty           (up to -10)
            - concentration_penalty     (up to -10)
            → clamped to [0, 100]
```

Best achievable score is 100 (BASE=60, full savings contribution=40, zero penalties). The v1 bug where the maximum was 80 is corrected.

**Savings contribution** scales linearly — a savings ratio of 30% earns the full 40 points. Below 0% (spending more than income) the contribution goes negative.

**Large transaction penalty** is proportional to the ratio of large transactions among all expenses.

**Anomaly penalty** is proportional to the anomaly ratio among all expenses.

**Concentration penalty** is proportional to the fraction of total expense going to a single category. A portfolio spread across many categories incurs no penalty; one category dominating at 80%+ incurs the full penalty.

All five constants (`BASE_HEALTH_SCORE`, `MAX_SAVINGS_CONTRIBUTION`, `MAX_LARGE_TXN_PENALTY`, `MAX_ANOMALY_PENALTY`, `MAX_CONCENTRATION_PENALTY`) are tunable in `config.py` with no code changes required.

**Health Score Labels**

| Score | Status |
|-------|--------|
| 80–100 | Excellent Financial Health |
| 60–79  | Financially Stable |
| 40–59  | Some Financial Risk |
| 0–39   | High Financial Risk |

---

### 4 — Recurring Transaction Detection

New in v4.0. Detects subscriptions, EMIs, and regular peer transfers automatically.

A transaction group is considered recurring if:
- The same merchant appears across at least `RECURRING_MIN_OCCURRENCES` months
- Amounts match within `RECURRING_AMOUNT_TOLERANCE` (default ±5%)
- Occurrences span multiple distinct calendar months

Output includes: merchant name, category, average amount, frequency, active months, typical day of month, first and last seen dates. The Goals page uses this data to show total monthly committed spend, which reduces your effective savings capacity.

All three parameters are configurable in `config.py`.

---

### 5 — Predictive Analytics

**Expense forecasting**

```
Expense(t) = β0 + β1 × t
```

Linear regression on monthly aggregated expense with a continuous time index. Available for total expenses or any individual category. Produces a 3-month forecast (configurable via `FORECAST_PERIODS`) with 95% confidence intervals derived from residual standard deviation:

```
CI = prediction ± (1.96 × std(residuals))
```

Requires at least 2 months of historical data.

**Savings forecasting**

Same linear model applied to monthly net savings (`Income − Expense`). Historical savings are visualised as a bar chart with green/red bars for positive/negative months. Forecast values shown with confidence interval bounds surfaced as metric card tooltips.

---

### 6 — Budget Intelligence

**Global budget planner**
User inputs a monthly budget target. System shows average monthly expense vs budget, with over/under delta as a metric.

**Per-category budget tracking**
Default category budgets are defined in `config.py` under `DEFAULT_CATEGORY_BUDGETS`. The Categories page compares average monthly spend per category against its budget, showing usage percentage and a 🟢/🟡/🔴 status. Over-budget categories are surfaced as a warning.

---

### 7 — Savings Goal Tracker

User inputs a target savings amount and timeline in months. The system:

- Calculates required monthly savings to hit the goal
- Compares against current average monthly savings
- Renders a progress bar showing projected attainment in the target window
- States whether the goal is on track or behind pace, with exact gap
- Overlays the 3-month savings forecast to show near-term trajectory
- Lists recurring committed expenses as context for what's reducing savings capacity

---

### 8 — Automated Insight Engine

Rule-based, deterministic, data-driven. Each insight is generated only when its data condition is met — no filler text.

Insights produced:
- Savings rate classification with benchmark comparison and absolute improvement suggestion
- Top spending category with percentage of total expenses
- Spending concentration warning when one category exceeds 50% of expenses
- Highest single-merchant spend
- Anomaly count with page reference
- Large transaction count and total value
- Monthly savings volatility warning when std dev exceeds 50% of mean savings
- Investment presence check — classifies as healthy (≥10% of income) or suggests scaling up
- Missing investment detection

---

### 9 — Executive PDF Report

Generated with ReportLab on A4 paper. Contents:

- Title and period
- Financial summary table (income, expense, net savings, health score)
- Health score breakdown table (savings ratio, large txn ratio, anomaly ratio, concentration)
- Expenses by category table
- All automated insights as bullet points
- PFIS footer

Tables use alternating row fills, dark headers, and consistent Arial typography. No charts are embedded in the current version — this is a known limitation noted in the roadmap.

---

## Project Structure

```
pfis/
│
├── app.py                          # UI layer — Streamlit pages and layout
├── config.py                       # Central config — all tuneable parameters
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   └── config.toml                 # Dark theme enforcement at framework level
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # Multi-format ingestion and cleaning
│   ├── categorizer.py              # Merchant normalisation and categorisation
│   ├── anomaly_detector.py         # Statistical + Isolation Forest detection
│   ├── aggregator.py               # Time features and aggregation helpers
│   ├── health_score.py             # Composite 0-100 scoring engine
│   ├── forecasting.py              # Linear regression expense forecasting
│   ├── savings_prediction.py       # Linear regression savings forecasting
│   ├── recurring.py                # Subscription and EMI detection
│   ├── insights.py                 # Rule-based insight generation
│   └── report_generator.py         # ReportLab PDF export
│
└── assets/
    ├── sample_transactions.csv     # 4-month CSV sample (Nov 2025 – Feb 2026)
    ├── sample_transactions.xlsx    # Same data as formatted Excel workbook
    └── sample_transactions.pdf     # Same data in bank statement PDF format
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI | Streamlit | Interactive dashboard and navigation |
| Visualisation | Plotly | Charts, gauges, and time series |
| Data | Pandas, NumPy | Manipulation and numerical computation |
| ML | Scikit-learn | Isolation Forest, Linear Regression |
| PDF ingestion | pdfplumber | Bank statement parsing |
| PDF export | ReportLab | Executive report generation |
| Spreadsheet | openpyxl | Excel read/write |

---

## Mathematical Foundations

**Large Transaction Threshold**
```
x > μ + kσ    where k = BIG_TRANSACTION_MULTIPLIER (default 2.0)
```

**Isolation Forest**
Anomaly score based on average path length required to isolate a point across an ensemble of random trees. Shorter path = more anomalous.

**Health Score**
```
S = 60 + min(40, (r_s / 0.30) × 40)
      - min(20, r_L × 20)
      - min(10, r_A × 10)
      - min(10, r_C × 10)
S = clamp(S, 0, 100)

r_s = savings ratio
r_L = large transaction ratio among expenses
r_A = anomaly ratio among expenses
r_C = top category concentration ratio
```

**Expense Forecast**
```
ŷ(t) = β̂0 + β̂1 · t
CI   = ŷ(t) ± 1.96 · σ_residual
```

**Savings Forecast**
Same form applied to monthly net savings series.

---

## Engineering Principles

- **Modular architecture** — each util is a standalone, independently importable module
- **Config-driven behaviour** — no magic numbers anywhere in code, all constants in `config.py`
- **Defensive ingestion** — every parse step uses coerce, not raise; meaningful errors surfaced to UI
- **Correct sign handling** — amount sign determines transaction direction, not category keywords
- **Separation of computation and UI** — `app.py` contains zero calculations
- **Explainable ML** — Isolation Forest used only for detection; scoring uses interpretable ratios
- **Deterministic outputs** — same input always produces the same score, insights, and forecast
- **Dark-first design** — `.streamlit/config.toml` enforces dark mode at framework level before CSS loads

---

## Installation and Setup

**Clone**
```bash
git clone https://github.com/KaizenVH24/VH-Personal_Finance_Intelligent_System.git
cd VH-Personal_Finance_Intelligent_System
```

**Virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**Install dependencies**
```bash
pip install -r requirements.txt
```

**Run**
```bash
streamlit run app.py
```

The `.streamlit/config.toml` in the project root will automatically apply the dark theme. No manual theme selection required.

---

## Sample Data

Three sample files are included in `assets/` covering November 2025 through February 2026 (771 transactions, ~₹2.6L income, ~₹2.5L expenses across 4 months).

| File | Format | Use |
|------|--------|-----|
| `sample_transactions.csv` | 4 columns: date, description, amount, balance | Direct upload to PFIS |
| `sample_transactions.xlsx` | Transactions sheet + Monthly Summary sheet | Upload or open in Excel |
| `sample_transactions.pdf` | Bank statement layout — same column structure as real statements | Tests the PDF parser end-to-end |

Transaction types covered: daily interest credits, monies transfers, Zerodha trades, loan EMIs (Suryoday, MoneyView), food delivery (Zomato, Swiggy), e-commerce (Flipkart, Amazon), transport (Indian Railways, Metro, Uber, Rapido), subscriptions (Netflix, Spotify), utilities (electricity, mobile recharge), bill payments, salary credits, peer UPI transfers, and cashback credits.

---

## Known Limitations

- PDF parser is calibrated for a specific bank statement layout. Other banks with different column ordering or date formats will need adjustments to `_DATE_RE` and `_TXN_END_RE` in `data_loader.py`.
- Forecasting uses linear regression. With only 1–2 months of data the forecast is a straight extrapolation and the confidence intervals will be wide.
- Recurring detection requires at least 2 months of data to produce meaningful results.
- PDF report does not embed charts. Chart-embedded PDF export is on the roadmap.
- No persistent storage — all analysis is session-scoped. Multi-month comparison requires uploading a combined statement.

---

## Roadmap

- Prophet-based seasonal forecasting to replace linear regression
- Charts embedded in PDF report via Plotly image export
- Real-time bank API ingestion
- PostgreSQL backend for persistent multi-month storage
- User authentication and session management
- KMeans behavioural clustering for spending archetype detection
- Multi-user analytics with isolated data namespaces
- REST API backend separated from Streamlit UI
- Parser extension for additional bank statement formats

---

## Interview Talking Points

> Built a modular financial intelligence platform that ingests raw PDF bank statements, normalises messy UPI merchant strings, detects anomalies with Isolation Forest, scores financial health with a configurable composite model, identifies recurring subscriptions and EMIs, forecasts expenses and savings with confidence intervals, and exports an executive PDF report — all in under 15 modules with no hardcoded values.

Demonstrates:

- Real-world unstructured data handling (PDF parsing, UPI string normalisation)
- Unsupervised ML applied to a practical problem
- Composite scoring system design with tunable weights
- Clean separation of concerns across a multi-module Python project
- Config-driven architecture that supports system tuning without code changes
- End-to-end product thinking from raw data to downloadable report

---

## Author

**Vinay Hulsurkar (VH24)**  
Computer Engineering  
Focused on Data Science and Intelligent Systems

Built with discipline and long-term vision.

- LeetCode — https://leetcode.com/u/vinayhulsurkar24/
- LinkedIn — https://www.linkedin.com/in/vinayhulsurkar
- Instagram — https://www.instagram.com/vinayhulsurkar

---

## License

This project is licensed under the MIT License.