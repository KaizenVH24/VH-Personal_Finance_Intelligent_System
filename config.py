# ================================================================
# PFIS — Personal Finance Intelligent System
# config.py — single source of truth for all tuneable values
# ================================================================

APP_TITLE    = "PFIS - Personal Finance Intelligent System"
APP_SUBTITLE = "AI & ML powered intelligent finance system."
FOOTER_TEXT  = "Copyright 2026 PFIS"

# ── Anomaly / large-transaction thresholds ──────────────────────
BIG_TRANSACTION_MULTIPLIER = 2.0    # threshold = mean + k*std
ANOMALY_CONTAMINATION      = 0.05   # Isolation Forest contamination

# ── Health score weights ────────────────────────────────────────
BASE_HEALTH_SCORE         = 60
MAX_SAVINGS_CONTRIBUTION  = 40
MAX_LARGE_TXN_PENALTY     = 20
MAX_ANOMALY_PENALTY       = 10
MAX_CONCENTRATION_PENALTY = 10

# ── Forecasting ─────────────────────────────────────────────────
FORECAST_PERIODS      = 3
CONFIDENCE_MULTIPLIER = 1.96    # z-score for 95% CI

# ── Budget defaults ─────────────────────────────────────────────
DEFAULT_MONTHLY_BUDGET = 30_000.0

DEFAULT_CATEGORY_BUDGETS = {
    "Food":          5_000.0,
    "Travel":        3_000.0,
    "Shopping":      4_000.0,
    "Entertainment": 2_000.0,
    "Bills":         5_000.0,
    "EMI / Loan":   10_000.0,
    "Investments":   5_000.0,
}

# ── Recurring-detection parameters ──────────────────────────────
RECURRING_AMOUNT_TOLERANCE = 0.05   # 5% variation is still "same"
RECURRING_MIN_OCCURRENCES  = 2
RECURRING_DAY_WINDOW       = 5      # ±5 days counts as "same date"

# ================================================================
# CSV / EXCEL COLUMN ALIAS MAPS
# Handles the many ways banks name their columns.
# All keys are lower-stripped. First match wins.
# ================================================================

# Maps alias → canonical name used internally
DATE_ALIASES = {
    "date", "value date", "value_date", "txn date", "txn_date",
    "transaction date", "transaction_date", "posting date", "posting_date",
    "trans date", "trans_date", "booking date", "booking_date",
    "tran date", "tran_date", "trade date", "trade_date",
    "valuedate", "transactiondate",
}

DESCRIPTION_ALIASES = {
    "description", "particulars", "narration", "details", "remarks",
    "txn description", "txn_description", "transaction description",
    "transaction_description", "transaction details", "transaction_details",
    "transaction remarks", "transaction_remarks", "trans description",
    "trans_description", "tran description", "tran_description",
    "memo", "narrative", "chq / ref no.", "chq/ref no.", "ref no.",
    "description/narration", "narration/description",
    "transaction narration", "payment description", "particular",
}

AMOUNT_ALIASES = {
    "amount", "txn amount", "txn_amount", "transaction amount",
    "transaction_amount", "net amount", "net_amount",
    "amt", "trans amt",
}

DEBIT_ALIASES = {
    "debit", "dr", "withdrawal", "withdrawals", "debit amount",
    "debit_amount", "dr amount", "dr_amount", "withdraw",
    "debits", "debit(inr)", "debit (inr)", "dr(inr)", "dr (inr)",
    "withdrawal amt (inr)", "withdrawal amt(inr)",
    "withdrawals (inr)", "debit amt", "debit_amt",
    "dr amt", "dr_amt",
}

CREDIT_ALIASES = {
    "credit", "cr", "deposit", "deposits", "credit amount",
    "credit_amount", "cr amount", "cr_amount",
    "deposits/credits", "credit(inr)", "credit (inr)",
    "cr(inr)", "cr (inr)", "deposit amt (inr)", "deposit amt(inr)",
    "credits (inr)", "credit amt", "credit_amt",
    "cr amt", "cr_amt",
}

BALANCE_ALIASES = {
    "balance", "running balance", "available balance",
    "closing balance", "balance (inr)", "balance(inr)",
    "current balance", "avl balance", "bal",
}

# ================================================================
# MERCHANT NORMALISATION MAP
# key  : regex pattern matched against lower-cased raw description
# value: (display_name, category)
# ================================================================
MERCHANT_MAP = {
    # ── Food & Delivery
    r"zomato":                               ("Zomato",             "Food"),
    r"swiggy":                               ("Swiggy",             "Food"),
    r"blinkit":                              ("Blinkit",            "Food"),
    r"dunzo":                                ("Dunzo",              "Food"),
    r"mcdonald":                             ("McDonald's",         "Food"),
    r"domino":                               ("Domino's",           "Food"),
    r"burger\s*king":                        ("Burger King",        "Food"),
    r"\bkfc\b":                              ("KFC",                "Food"),
    r"starbucks":                            ("Starbucks",          "Food"),
    r"cafe\s*coffee|ccd":                    ("CCD",                "Food"),
    r"bigbasket":                            ("BigBasket",          "Food"),
    r"jiomart":                              ("JioMart",            "Food"),
    r"instamart|insta\s*mart":               ("Instamart",          "Food"),
    r"zepto":                                ("Zepto",              "Food"),

    # ── Shopping
    r"amazon|amzn":                          ("Amazon",             "Shopping"),
    r"flipkart":                             ("Flipkart",           "Shopping"),
    r"myntra":                               ("Myntra",             "Shopping"),
    r"meesho":                               ("Meesho",             "Shopping"),
    r"ajio":                                 ("Ajio",               "Shopping"),
    r"nykaa":                                ("Nykaa",              "Shopping"),
    r"snapdeal":                             ("Snapdeal",           "Shopping"),
    r"tata\s*cliq|tatacliq":                 ("Tata CLiQ",          "Shopping"),
    r"croma":                                ("Croma",              "Shopping"),

    # ── Travel
    r"\buber\b":                             ("Uber",               "Travel"),
    r"\bola\b":                              ("Ola",                "Travel"),
    r"rapido":                               ("Rapido",             "Travel"),
    r"ircts|irctc|indian\s*railways":        ("Indian Railways",    "Travel"),
    r"metro\s*cca|pune\s*metro|metro\s*rail":("Metro Rail",         "Travel"),
    r"petrol|bpcl|hpcl|iocl|reliance\s*petro": ("Fuel",            "Travel"),
    r"makemytrip|mmt":                       ("MakeMyTrip",         "Travel"),
    r"goibibo":                              ("Goibibo",            "Travel"),
    r"yatra":                                ("Yatra",              "Travel"),
    r"redbus":                               ("RedBus",             "Travel"),
    r"indigo|air\s*india|spicejet|vistara":  ("Air Travel",         "Travel"),

    # ── Entertainment
    r"netflix":                              ("Netflix",            "Entertainment"),
    r"hotstar|disney":                       ("Disney+ Hotstar",    "Entertainment"),
    r"spotify":                              ("Spotify",            "Entertainment"),
    r"youtube.*premium":                     ("YouTube Premium",    "Entertainment"),
    r"prime.*video|primevideo|amazon\s*prime":("Amazon Prime",      "Entertainment"),
    r"bookmyshow":                           ("BookMyShow",         "Entertainment"),
    r"\bpvr\b|\binox\b":                     ("Cinema",             "Entertainment"),
    r"sony.*liv|sonyliv":                    ("SonyLIV",            "Entertainment"),
    r"zee5|zee\s*5":                         ("ZEE5",               "Entertainment"),
    r"jiocinema|jio\s*cinema":               ("JioCinema",          "Entertainment"),
    r"mxplayer|mx\s*player":                 ("MX Player",          "Entertainment"),

    # ── Bills & Utilities
    r"bescom|msedcl|tpddl|electricity|mahadiscom": ("Electricity",  "Bills"),
    r"airtel|jio\b|vodafone|\bvi\b|bsnl":    ("Mobile / Internet",  "Bills"),
    r"water\s*bill|bwssb":                   ("Water Bill",         "Bills"),
    r"indane|hp\s*gas|bharat\s*gas":         ("Gas Bill",           "Bills"),
    r"bill\s*payment|bill\s*pay":            ("Bill Payment",       "Bills"),
    r"insurance|\blic\b":                    ("Insurance",          "Bills"),
    r"bbps":                                 ("Utility Bill",       "Bills"),

    # ── Investments
    r"zerodha|iccl.*zerodha|zerodha.*iccl|zerodha.*broking": ("Zerodha",   "Investments"),
    r"\bgroww\b":                            ("Groww",              "Investments"),
    r"kuvera":                               ("Kuvera",             "Investments"),
    r"coin\s*by\s*zerodha|coin.*zerodha":    ("Zerodha Coin",       "Investments"),
    r"neft.*zerodha|zerodha.*neft":          ("Zerodha (NEFT)",     "Investments"),
    r"upstox":                               ("Upstox",             "Investments"),
    r"smallcase":                            ("Smallcase",          "Investments"),
    r"mutual\s*fund|mf.*sip|\bsip\b":        ("Mutual Fund",        "Investments"),
    r"\bppf\b|\bnps\b":                      ("PPF / NPS",          "Investments"),

    # ── Loans & EMIs
    r"moneyview":                            ("MoneyView (Loan)",   "EMI / Loan"),
    r"bajaj\s*finserv|bajajfinserv":         ("Bajaj Finserv",      "EMI / Loan"),
    r"hdfc.*loan|hdfc.*emi":                 ("HDFC Loan",          "EMI / Loan"),
    r"\brepayment\b":                        ("Loan Repayment",     "EMI / Loan"),
    r"emi\b|e\.m\.i":                        ("EMI",                "EMI / Loan"),
    r"iifl|india\s*infoline":                ("IIFL Loan",          "EMI / Loan"),

    # ── Income signals
    r"interest\s*cr|interest\s*credit":      ("Bank Interest",      "Income"),
    r"monies\s*transfer":                    ("Bank Interest",      "Income"),
    r"bhimcashback|cashback":                ("Cashback",           "Income"),
    r"\bsalary\b|payroll":                   ("Salary",             "Income"),
    r"neft\s*credit|imps\s*credit":          ("Bank Transfer In",   "Income"),
    r"dividend":                             ("Dividend",           "Income"),
    r"refund":                               ("Refund",             "Income"),
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