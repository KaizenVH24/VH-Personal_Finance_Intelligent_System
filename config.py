# ==============================
#  Application Branding
# ==============================

APP_TITLE = "Personal Finance Intelligent System"
APP_SUBTITLE = "AI & ML-Powered Financial Intelligence Dashboard"
FOOTER_TEXT = "Built with Discipline and Intelligence | VH24"


# ==============================
#  Statistical Settings
# ==============================

# Large transaction threshold = mean + (MULTIPLIER * std)
BIG_TRANSACTION_MULTIPLIER = 2

# Isolation Forest contamination rate
ANOMALY_CONTAMINATION = 0.05


# ==============================
#  Financial Health Scoring
# ==============================

BASE_HEALTH_SCORE = 50
MAX_SAVINGS_CONTRIBUTION = 30
MAX_LARGE_TXN_PENALTY = 10
MAX_ANOMALY_PENALTY = 10
MAX_CONCENTRATION_PENALTY = 10


# ==============================
#  Forecasting Settings
# ==============================

FORECAST_PERIODS = 3

# 95% confidence interval multiplier
CONFIDENCE_MULTIPLIER = 1.96


# ==============================
#  Budget Settings
# ==============================

DEFAULT_MONTHLY_BUDGET = 30000.0

# ==============================
#  Transaction Categories
# ==============================

CATEGORY_KEYWORDS = {
    "Salary": ["salary", "credit from company", "monthly credit"],
    "Food": ["swiggy", "zomato", "mcdonald", "dominos", "restaurant"],
    "Shopping": ["amazon", "flipkart", "myntra"],
    "Travel": ["uber", "ola", "irctc", "petrol"],
    "Bills": ["electricity", "water", "gas bill", "recharge"],
    "Entertainment": ["netflix", "hotstar", "movie"]
}
