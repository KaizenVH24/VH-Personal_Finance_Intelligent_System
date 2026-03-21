# ================================================================
# PFIS — Personal Finance Intelligent System
# config.py — single source of truth for all tuneable values
# ================================================================

APP_TITLE     = "PFIS"
APP_SUBTITLE  = "Personal Finance Intelligent System"
FOOTER_TEXT   = "Copyright 2026 PFIS"

# ── Anomaly / large-transaction thresholds ──────────────────────
BIG_TRANSACTION_MULTIPLIER = 2.0    # threshold = mean + k*std
ANOMALY_CONTAMINATION      = 0.05   # Isolation Forest contamination

# ── Health score weights ────────────────────────────────────────
# Formula: BASE + savings_contribution - penalties  → clamp(0, 100)
# Best case: 60 + 40 - 0  = 100
# Worst:     60 - 40(neg) - 40 penalties → clamped to 0
BASE_HEALTH_SCORE        = 60
MAX_SAVINGS_CONTRIBUTION = 40   # full 40 pts at savings_ratio ≥ 0.30
MAX_LARGE_TXN_PENALTY    = 20
MAX_ANOMALY_PENALTY      = 10
MAX_CONCENTRATION_PENALTY= 10

# ── Forecasting ─────────────────────────────────────────────────
FORECAST_PERIODS      = 3
CONFIDENCE_MULTIPLIER = 1.96    # z-score for 95% CI

# ── Budget defaults ─────────────────────────────────────────────
DEFAULT_MONTHLY_BUDGET = 30_000.0

DEFAULT_CATEGORY_BUDGETS = {
    "Food":         5_000.0,
    "Travel":       3_000.0,
    "Shopping":     4_000.0,
    "Entertainment":2_000.0,
    "Bills":        5_000.0,
    "EMI / Loan":  10_000.0,
    "Investments":  5_000.0,
}

# ── Recurring-detection parameters ──────────────────────────────
RECURRING_AMOUNT_TOLERANCE  = 0.05   # 5 % variation is still "same"
RECURRING_MIN_OCCURRENCES   = 2
RECURRING_DAY_WINDOW        = 5      # ±5 days counts as "same date"

# ── Merchant normalisation map ──────────────────────────────────
# key  : regex pattern matched against lower-cased raw description
# value: (display_name, category)
MERCHANT_MAP = {
    # ── Food & Delivery
    r"zomato":                          ("Zomato",               "Food"),
    r"swiggy":                          ("Swiggy",               "Food"),
    r"blinkit":                         ("Blinkit",              "Food"),
    r"dunzo":                           ("Dunzo",                "Food"),
    r"mcdonald":                        ("McDonald's",           "Food"),
    r"domino":                          ("Domino's",             "Food"),
    r"burger king":                     ("Burger King",          "Food"),
    r"kfc":                             ("KFC",                  "Food"),
    r"starbucks":                       ("Starbucks",            "Food"),
    r"cafe coffee|ccd":                 ("CCD",                  "Food"),

    # ── Shopping
    r"amazon|amzn":                     ("Amazon",               "Shopping"),
    r"flipkart":                        ("Flipkart",             "Shopping"),
    r"myntra":                          ("Myntra",               "Shopping"),
    r"meesho":                          ("Meesho",               "Shopping"),
    r"ajio":                            ("Ajio",                 "Shopping"),
    r"nykaa":                           ("Nykaa",                "Shopping"),
    r"snapdeal":                        ("Snapdeal",             "Shopping"),
    r"bigbasket":                       ("BigBasket",            "Shopping"),
    r"jiomart":                         ("JioMart",              "Shopping"),

    # ── Travel
    r"uber":                            ("Uber",                 "Travel"),
    r"ola\b":                           ("Ola",                  "Travel"),
    r"rapido":                          ("Rapido",               "Travel"),
    r"iruts|irctc|indian railways":     ("Indian Railways",      "Travel"),
    r"metro cca|pune metro":            ("Pune Metro",           "Travel"),
    r"paytm.*travel|ircts":             ("Indian Railways",      "Travel"),
    r"petrol|bpcl|hpcl|iocl|reliance petro": ("Fuel",           "Travel"),
    r"makemytrip|mmt":                  ("MakeMyTrip",           "Travel"),
    r"goibibo":                         ("Goibibo",              "Travel"),

    # ── Entertainment
    r"netflix":                         ("Netflix",              "Entertainment"),
    r"hotstar|disney":                  ("Disney+ Hotstar",      "Entertainment"),
    r"spotify":                         ("Spotify",              "Entertainment"),
    r"youtube.*premium":                ("YouTube Premium",      "Entertainment"),
    r"prime.*video|primevideo|amazon prime": ("Amazon Prime",    "Entertainment"),
    r"bookmyshow":                      ("BookMyShow",           "Entertainment"),
    r"pvr|inox":                        ("Cinema",               "Entertainment"),
    r"sony.*liv|sonyliv":               ("SonyLIV",              "Entertainment"),

    # ── Bills & Utilities
    r"bescom|msedcl|tpddl|electricity": ("Electricity",         "Bills"),
    r"airtel|jio\b|vodafone|vi\b|bsnl": ("Mobile / Internet",   "Bills"),
    r"water bill|bwssb":                ("Water Bill",           "Bills"),
    r"indane|hp gas|bharat gas":        ("Gas Bill",             "Bills"),
    r"bill payment":                    ("Bill Payment",         "Bills"),
    r"insurance|lic\b":                 ("Insurance",            "Bills"),

    # ── Investments
    r"zerodha|iccl.*zerodha|zerodha.*iccl|zerodha.*broking": ("Zerodha", "Investments"),
    r"groww":                           ("Groww",                "Investments"),
    r"kuvera":                          ("Kuvera",               "Investments"),
    r"neft.*zerodha|zerodha.*neft":     ("Zerodha (NEFT)",       "Investments"),

    # ── Loans & EMIs
    r"suryoday":                        ("Suryoday (Loan)",      "EMI / Loan"),
    r"moneyview":                       ("MoneyView (Loan)",     "EMI / Loan"),
    r"bajaj finserv|bajajfinserv":      ("Bajaj Finserv",        "EMI / Loan"),
    r"hdfc.*loan|hdfc.*emi":            ("HDFC Loan",            "EMI / Loan"),
    r"\brepayment\b":                   ("Loan Repayment",       "EMI / Loan"),

    # ── Income signals
    r"interest cr|interest credit":     ("Bank Interest",        "Income"),
    r"monies transfer":                 ("Bank Interest",        "Income"),
    r"bhimcashback|cashback":           ("Cashback",             "Income"),
    r"salary|payroll":                  ("Salary",               "Income"),
    r"neft credit|imps credit":         ("Bank Transfer In",     "Income"),
}

CATEGORY_ORDER = [
    "Food", "Shopping", "Travel", "Entertainment",
    "Bills", "EMI / Loan", "Investments", "Others",
]

CHART_COLORS = {
    "Food":          "#F97316",
    "Shopping":      "#8B5CF6",
    "Travel":        "#3B82F6",
    "Entertainment": "#EC4899",
    "Bills":         "#6B7280",
    "EMI / Loan":    "#EF4444",
    "Investments":   "#10B981",
    "Others":        "#94A3B8",
    "Income":        "#22C55E",
}