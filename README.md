# Personal Finance Intelligent System (PFIS)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive_Dashboard-red)
![Machine Learning](https://img.shields.io/badge/ML-IsolationForest-green)
![Architecture](https://img.shields.io/badge/Architecture-Modular-orange)
![Status](https://img.shields.io/badge/Status-VH_v3.5-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> AI-Powered Financial Intelligence Platform  
> Engineered with discipline and analytical precision — **VH24 aka Vinay Hulsurkar**

---

# Executive Summary

Personal Finance Intelligent System (PFIS) is a modular, end-to-end financial analytics platform that transforms raw bank transaction data into structured intelligence, risk insights, predictive forecasts and executive-ready financial reports.

This system is not a static dashboard, it is a structured financial intelligence engine integrating:

- Data validation and cleansing
- Behavioral transaction categorization
- Statistical anomaly detection
- Composite financial health modeling
- Predictive expense & savings forecasting
- Automated insight generation
- Executive PDF reporting

Built as a production-grade final year project with scalability, explainability and system design principles in mind.

---

# System Architecture Overview

PFIS follows a layered modular architecture:

```
UI Layer (Streamlit)
        ↓
Business Logic Layer (utils/)
        ↓
Statistical & ML Layer
        ↓
Configuration Layer (config.py)
        ↓
Data Input Layer (CSV ingestion)
```

This separation ensures:

- Maintainability
- Scalability
- Config-driven system tuning
- Clean engineering practices
- Interview-defensible structure

---

# Core System Capabilities

---

## 1️⃣ Transaction Intelligence Engine

### ✔ Schema Validation
- Required column enforcement (`date`, `description`, `amount`)
- Currency symbol normalization
- Duplicate removal
- Chronological sorting
- Type coercion and null handling

### ✔ Categorization Framework
- Config-driven keyword classification
- Whole-word regex matching
- Income vs Expense inference
- Refund detection logic
- Extendable category system

### ✔ Time Feature Engineering
- Year, month, ISO week extraction
- `year_month` period construction
- Aggregation-ready time indexing

---

## 2️⃣ Anomaly & Risk Detection Layer

### Large Transaction Detection
Statistical thresholding:
```
Threshold = Mean + (k × Standard Deviation)
```
Configurable multiplier via `config.py`.

### Unsupervised ML Anomaly Detection
- Isolation Forest (Scikit-learn)
- Configurable contamination rate
- Applied only to expense behavior
- Ratio-based penalty modeling

This ensures explainability and risk quantification.

---

## 3️⃣ Financial Health Scoring Engine (0–100)

A composite scoring model incorporating:

- Savings Ratio
- Large Transaction Frequency
- Anomaly Ratio
- Spending Concentration Risk
- Monthly Stability Indicators

Mathematically structured as:

```
Final Score =
Base Score
+ Savings Contribution
- Risk Penalties
- Concentration Adjustment
```

All weights are configurable through `config.py`.

### Output Includes:
- Overall Health Score
- Ratio-based breakdown
- Monthly Health Trend visualization

---

## 4️⃣ Predictive Analytics Module

### Expense Forecasting
- Time-indexed Linear Regression
- Category-wise forecasting
- Future period generation
- Residual-based 95% confidence intervals

Model form:
```
Expense(t) = β0 + β1 × Time
```

### Savings Forecasting
- Derived from Income − Expense
- Trend-based projection
- Confidence interval bands
- Volatility awareness

Forecast horizon configurable.

---

## 5️⃣ Budget Intelligence Module

- Dynamic user-defined budget input
- Average monthly expense calculation
- Over-budget / Under-budget feedback
- Financial behavior signal generation

---

## 6️⃣ Automated Insight Engine

Rule-based financial heuristics generate:

- Savings discipline classification
- Spending concentration warnings
- Anomaly frequency alerts
- Monthly savings volatility detection
- Behavioral risk commentary

Insight generation is deterministic, explainable, and data-driven.

---

## 7️⃣ Executive Report Generator

PDF generation using ReportLab including:

- Income / Expense summary
- Net savings
- Financial health breakdown
- Risk indicators
- Automated insights
- Professional structured layout

Designed for executive presentation.

---

# Project Structure

```
personal-finance-intelligent-system/
│
├── app.py                     # UI Layer
├── config.py                  # Central configuration & system tuning
├── requirements.txt
├── README.md
├── .gitignore
│
├── utils/
│   ├── data_loader.py         # Data validation & cleaning
│   ├── categorizer.py         # Transaction classification
│   ├── anomaly_detector.py    # Statistical + ML anomaly detection
│   ├── aggregator.py          # Time feature engineering
│   ├── health_score.py        # Composite financial scoring
│   ├── forecasting.py         # Expense forecasting
│   ├── savings_prediction.py  # Savings forecasting
│   ├── insights.py            # Insight generation engine
│   ├── report_generator.py    # Executive PDF reporting
│
├── assets/
│   ├── sample_transactions.csv
│   ├── sample_transactions_large.csv
│   ├── Bank_statement.csv
└── venv/ (ignored)
```

---

# Tech Stack

- **Python 3.10+**
- **Pandas** – Data manipulation
- **NumPy** – Numerical computation
- **Scikit-learn** – Isolation Forest & Regression
- **Streamlit** – Interactive UI
- **Plotly** – Data visualization
- **ReportLab** – PDF generation

---

# Mathematical & ML Foundations

### Large Transaction Detection
```
x > μ + kσ
```

### Isolation Forest
Unsupervised anomaly detection using tree isolation depth.

### Forecasting
```
y = β0 + β1t
```

### Confidence Interval
```
Prediction ± (Z × Residual Std Dev)
```

### Health Score
Composite weighted risk model with proportional penalties.

---

# Engineering Principles Applied

- Modular architecture
- Configuration-driven behavior
- Defensive data handling
- Explainable ML modeling
- No hardcoded magic numbers
- Separation of computation & UI
- Deterministic scoring logic
- Maintainable code structure

---

# Installation & Setup

### Clone Repository

```bash
git clone https://github.com/KaizenVH24/VH-Personal_Finance_Intelligent_System.git
cd VH-Personal_Finance_Intelligent_System
```

### Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

---

# Future Expansion Roadmap

- Prophet-based seasonal forecasting
- Real-time API ingestion
- PostgreSQL integration
- User authentication & session handling
- Behavioral clustering using KMeans
- Multi-user financial analytics
- Cloud deployment (AWS / Streamlit Cloud)
- REST API backend separation
- Dashboard theming & UX enhancement

---

# Interview Talking Points

When presenting this project:

> Built a modular financial intelligence platform integrating anomaly detection, predictive modeling, composite scoring systems and executive reporting with configuration-driven architecture.

Demonstrates:

- Machine Learning integration
- Financial risk modeling
- Statistical reasoning
- Data engineering
- System design thinking
- Product-level development maturity

---

# Author

**Vinay Hulsurkar (VH24)**  
Computer Engineering  
Focused on Data Science & Intelligent Systems  

Built with discipline and long-term vision.

- Leetcode - https://leetcode.com/u/vinayhulsurkar24/
- LinkedIn - https://www.linkedin.com/in/vinayhulsurkar
- Instagram - https://www.instagram.com/vinayhulsurkar

---

# 📜 License

This project is licensed under the MIT License.
