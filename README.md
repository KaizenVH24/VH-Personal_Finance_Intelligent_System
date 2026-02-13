# 💰 Personal Finance Intelligent System (PFIS)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Machine Learning](https://img.shields.io/badge/ML-IsolationForest-green)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> AI-Powered Financial Intelligence Dashboard  
> Built with discipline and intelligence — **VH24**

---

## 🚀 Overview

Personal Finance Intelligent System (PFIS) is a full-stack financial analytics platform designed to transform raw bank transaction data into intelligent financial insights.

The system performs:

- Transaction categorization
- Anomaly detection using machine learning
- Predictive forecasting
- Financial health scoring
- Budget comparison
- Automated executive reporting

This project demonstrates end-to-end data engineering, machine learning integration, and product-level thinking in fintech systems.

---

## Core Capabilities

### Transaction Intelligence Engine
- Rule-based transaction categorization
- Automatic Income vs Expense separation
- Weekly / Monthly / Yearly aggregation
- Statistical large transaction detection
- ML-based anomaly detection using Isolation Forest

---

### Financial Health Scoring System

Composite Financial Health Score (0–100) based on:

- Savings ratio
- Spending concentration risk
- Large transaction frequency
- Anomaly frequency
- Stability indicators

Includes:
- Overall health score
- Monthly health trend visualization

---

### Predictive Analytics Module

- Total monthly expense forecasting
- Category-wise expense forecasting
- Savings prediction model
- 95% confidence interval bands
- Trend-based linear regression modeling

---

### Budget Planning Module

- Custom monthly budget input
- Average expense comparison
- Over-budget / under-budget analysis
- Financial risk feedback

---

### Automated Insight Engine

Generates system-driven financial commentary:

- Spending discipline analysis
- Highest expense category detection
- Risk alerts
- Savings behavior summary

---

### Executive Report Generator

Downloadable PDF report including:

- Income / Expense summary
- Net savings
- Financial health score
- Risk breakdown
- Automated insights

Designed for executive-level presentation.

---

## Project Architecture

```
personal-finance-intelligent-system/
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── utils/
│   ├── data_loader.py
│   ├── categorizer.py
│   ├── anomaly_detector.py
│   ├── aggregator.py
│   ├── health_score.py
│   ├── forecasting.py
│   ├── savings_prediction.py
│   ├── insights.py
│   ├── report_generator.py
│
├── assets/
│   ├── sample_transactions.csv
│   ├── sample_transactions_large.csv
│
└── venv/ (ignored)
```

---

## 🛠️ Tech Stack

- **Python**
- **Pandas**
- **NumPy**
- **Scikit-learn**
- **Streamlit**
- **Plotly**
- **ReportLab**

---

## Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/KaizenVH24/VH-Personal_Finance_Intelligent_System.git
cd VH-Personal_Finance_Intelligent_System
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate environment:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run Application

```bash
streamlit run app.py
```

---

## Sample Datasets

Located in `/assets`:

- `sample_transactions.csv`
- `sample_transactions_large.csv`

Both contain multi-month income and expense data for testing.

---

## Financial Modeling Approach

### Large Transaction Detection
Statistical threshold:
```
mean + k * standard deviation
```

### Anomaly Detection
Unsupervised ML using:
```
Isolation Forest
```

### Forecasting Model
Time-indexed Linear Regression:
```
Expense ~ Time
```

Confidence bands calculated using residual standard deviation.

### Financial Health Score
Weighted composite scoring model:

- Base Score
- Savings Contribution
- Risk Penalties
- Concentration Risk Adjustment

Explainable and modular.

---

## Design Principles

- Modular architecture
- Separation of UI and business logic
- Explainable ML models
- Reproducible environment
- Fintech-inspired system design
- Clean and scalable code structure

---

## Demonstrated Concepts

This project showcases:

- Data preprocessing & cleaning
- Feature engineering
- Unsupervised learning
- Time-series forecasting
- Risk modeling
- Dashboard engineering
- Report automation
- Full-stack integration

---

## Future Roadmap

- Prophet-based advanced forecasting
- Real-time transaction ingestion
- Database integration (PostgreSQL)
- User authentication system
- Cloud deployment (AWS / Streamlit Cloud)
- Goal-based financial planning engine
- Behavioral spending clustering

---

## Interview Discussion Points

If asked about the project:

> Built an intelligent financial analytics system integrating anomaly detection, forecasting, composite health scoring, and automated reporting using modular Python architecture and Streamlit.

Demonstrates:
- ML integration
- Data-driven decision modeling
- Product-level thinking
- Clean engineering practices

---

## Author

**Vinay Hulsurkar (VH24)**  
Computer Engineering  
Focused on Data Science & Intelligent Systems

Built with discipline and long-term vision.
- Leetcode - https://leetcode.com/u/vinayhulsurkar24/
- LinkedIn - https://www.linkedin.com/in/vinayhulsurkar
- Instagram - https://www.instagram.com/vinayhulsurkar
---

## License

This project is licensed under the MIT License.
