import streamlit as st
import pandas as pd
import plotly.express as px

from config import APP_TITLE, APP_SUBTITLE, FOOTER_TEXT
from utils.data_loader import load_data
from utils.categorizer import apply_categorization
from utils.anomaly_detector import detect_large_transactions
from utils.aggregator import add_time_features, monthly_summary
from utils.anomaly_detector import detect_large_transactions, detect_anomalies
from utils.categorizer import apply_categorization, assign_transaction_type
from utils.health_score import calculate_financial_health_score


st.set_page_config(page_title=APP_TITLE, layout="wide")

# Header
st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Transactions", "Category Analysis"]
)

uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:

    df = load_data(uploaded_file)
    df = apply_categorization(df)
    df = assign_transaction_type(df)
    df, threshold = detect_large_transactions(df)
    df = detect_anomalies(df)
    df = add_time_features(df)


    if page == "Dashboard":

        st.subheader("📊 Financial Overview")

        col1, col2, col3 = st.columns(3)

        total_income = df[df["transaction_type"] == "Income"]["amount"].sum()
        total_expense = df[df["transaction_type"] == "Expense"]["amount"].sum()
        net_savings = total_income - total_expense

        col1.metric("Total Income", f"₹ {total_income:,.2f}")
        col2.metric("Total Expense", f"₹ {total_expense:,.2f}")
        col3.metric("Net Savings", f"₹ {net_savings:,.2f}")

        st.divider()
        st.subheader("🧠 Financial Health Score")

        score, breakdown = calculate_financial_health_score(df)

        col1, col2 = st.columns([1,2])

        with col1:
            st.metric("Health Score", f"{score} / 100")

        with col2:
            st.write("### Breakdown")
            st.write(f"Savings Ratio: {breakdown['Savings Ratio']}%")
            st.write(f"Large Transactions Count: {breakdown['Large Transactions']}")
            st.write(f"AI Anomalies: {breakdown['Anomalies']}")
            st.write(f"Top Category Concentration: {breakdown['Top Category Ratio']}%")

        if score >= 80:
            st.success("Excellent Financial Stability")
        elif score >= 60:
            st.info("Financially Stable but Room for Optimization")
        elif score >= 40:
            st.warning("Financial Risk Detected – Monitor Spending")
        else:
            st.error("High Financial Risk – Immediate Attention Recommended")

        st.divider()

        # Category Distribution
        st.subheader("Category Distribution (Income vs Expense)")

        category_data = (
            df.groupby(["transaction_type", "category"])["amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            category_data,
            x="category",
            y="amount",
            color="transaction_type",
            barmode="group"
        )

        st.plotly_chart(fig, use_container_width=True)


        # Monthly Trend
        st.subheader("Monthly Spending Trend")

        monthly_data = (
            df[df["transaction_type"] == "Expense"]
            .groupby(["year", "month_number", "month"])["amount"]
            .sum()
            .reset_index()
            .sort_values(["year", "month_number"])
        )

        monthly_data["year_month"] = (
            monthly_data["month"].astype(str) + " " + monthly_data["year"].astype(str)
        )


        fig2 = px.bar(
            monthly_data,
            x="year_month",
            y="amount",
            color="year"
        )

        st.plotly_chart(fig2, use_container_width=True)


    elif page == "Transactions":

        st.subheader("📋 All Transactions")

        st.dataframe(df)

        st.subheader("🚨 Flagged Large Transactions")

        st.subheader("🧠 AI-Detected Anomalies")

        anomaly_df = df[df["is_anomaly"] == True]

        if anomaly_df.empty:
            st.success("No anomalies detected by AI model.")
        else:
            st.dataframe(anomaly_df)


        large_df = df[df["is_large"] == True]

        if large_df.empty:
            st.success("No unusually large transactions detected.")
        else:
            st.dataframe(large_df)

    elif page == "Category Analysis":

        monthly_cat = (
            df.groupby(["transaction_type", "year", "month_number", "month", "category"])["amount"]
            .sum()
            .reset_index()
            .sort_values(["year", "month_number"])
        )

        monthly_cat["year_month"] = (
            monthly_cat["month"].astype(str) + " " + monthly_cat["year"].astype(str)
        )


        fig3 = px.bar(
            monthly_cat,
            x="year_month",
            y="amount",
            color="category",
            facet_row="transaction_type"
        )

        st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Please upload a transaction CSV file from the sidebar.")

st.markdown("---")
st.caption(FOOTER_TEXT)
