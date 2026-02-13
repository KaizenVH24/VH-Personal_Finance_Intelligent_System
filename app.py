import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config import (
    APP_TITLE,
    APP_SUBTITLE,
    FOOTER_TEXT,
    DEFAULT_MONTHLY_BUDGET
)

from utils.data_loader import load_data
from utils.categorizer import apply_categorization, assign_transaction_type
from utils.anomaly_detector import detect_large_transactions, detect_anomalies
from utils.aggregator import add_time_features
from utils.health_score import calculate_financial_health_score, monthly_health_trend
from utils.forecasting import forecast_next_months
from utils.savings_prediction import predict_savings
from utils.insights import generate_insights
from utils.report_generator import generate_pdf_report


st.set_page_config(page_title=APP_TITLE, layout="wide")

st.title(APP_TITLE)
st.caption(APP_SUBTITLE)

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Transactions", "Category Analysis"]
)

uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:

    # ============================
    # DATA PIPELINE
    # ============================
    df = load_data(uploaded_file)
    df = apply_categorization(df)
    df = assign_transaction_type(df)
    df, threshold = detect_large_transactions(df)
    df = detect_anomalies(df)
    df = add_time_features(df)

    total_income = df[df["transaction_type"] == "Income"]["amount"].sum()
    total_expense = df[df["transaction_type"] == "Expense"]["amount"].sum()
    net_savings = total_income - total_expense

    score, breakdown = calculate_financial_health_score(df)
    insights = generate_insights(df)

    # ============================
    # DASHBOARD
    # ============================
    if page == "Dashboard":

        st.subheader("Financial Overview")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income", f"₹ {total_income:,.2f}")
        col2.metric("Total Expense", f"₹ {total_expense:,.2f}")
        col3.metric("Net Savings", f"₹ {net_savings:,.2f}")

        st.divider()

        # ================= Health Score =================
        st.subheader("Financial Health Score")

        col1, col2 = st.columns([1, 2])
        col1.metric("Health Score", f"{score} / 100")

        with col2:
            st.write("### Breakdown")
            for key, value in breakdown.items():
                st.write(f"{key}: {value}")

        if score >= 80:
            st.success("Excellent Financial Stability")
        elif score >= 60:
            st.info("Financially Stable")
        elif score >= 40:
            st.warning("Financial Risk Detected")
        else:
            st.error("High Financial Risk")

        st.divider()

        # ================= Health Trend =================
        st.subheader("Financial Health Trend")

        trend_df = monthly_health_trend(df)

        fig_health = px.line(
            trend_df,
            x="month",
            y="score",
            markers=True
        )

        st.plotly_chart(fig_health, use_container_width=True)

        st.divider()

        # ================= Budget Planner =================
        st.subheader("Budget Planner")

        monthly_budget = st.number_input(
            "Enter Monthly Budget (₹)",
            min_value=0.0,
            value=DEFAULT_MONTHLY_BUDGET,
            step=1000.0
        )

        months_count = df[["year", "month_number"]].drop_duplicates().shape[0]
        avg_monthly_expense = total_expense / months_count if months_count > 0 else 0

        st.write(f"Average Monthly Expense: ₹ {avg_monthly_expense:,.2f}")

        difference = monthly_budget - avg_monthly_expense

        if difference > 0:
            st.success(f"Under budget by ₹ {difference:,.2f}")
        else:
            st.error(f"Over budget by ₹ {abs(difference):,.2f}")

        st.divider()

        # ================= Expense Forecast =================
        st.subheader("Expense Forecast")

        categories = df[df["transaction_type"] == "Expense"]["category"].unique()
        selected_category = st.selectbox(
            "Select Category",
            ["Total"] + list(categories)
        )

        if selected_category == "Total":
            forecast_result = forecast_next_months(df)
        else:
            forecast_result = forecast_next_months(df, category=selected_category)

        if forecast_result:
            historical_data, forecast_df = forecast_result

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=historical_data["year_month"],
                y=historical_data["amount"],
                mode="lines+markers",
                name="Historical"
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df["year_month"],
                y=forecast_df["predicted_expense"],
                mode="lines+markers",
                name="Forecast"
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df["year_month"],
                y=forecast_df["upper_bound"],
                mode="lines",
                line=dict(dash="dash"),
                name="Upper CI"
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df["year_month"],
                y=forecast_df["lower_bound"],
                mode="lines",
                line=dict(dash="dash"),
                name="Lower CI"
            ))


            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # ================= Savings Forecast =================
        st.subheader("Savings Forecast")

        savings_result = predict_savings(df)

        if savings_result:
            historical_savings, forecast_savings = savings_result

            for idx, value in enumerate(forecast_savings["predicted_savings"], 1):
                st.write(f"Month +{idx}: ₹ {round(value, 2)}")

        st.divider()

        # ================= Insights =================
        st.subheader("Automated Insights")

        for insight in insights:
            st.write("•", insight)

        st.divider()

        # ================= PDF =================
        st.subheader("Download Executive Report")

        pdf_buffer = generate_pdf_report(df, score, breakdown, insights)

        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="PFIS_Report_VH24.pdf",
            mime="application/pdf"
        )

    # ============================
    # TRANSACTIONS PAGE
    # ============================
    elif page == "Transactions":

        st.subheader("All Transactions")
        st.dataframe(df)

        st.subheader("Large Transactions")
        st.dataframe(df[df["is_large"]])

        st.subheader("Anomalies")
        st.dataframe(df[df["is_anomaly"]])

    # ============================
    # CATEGORY ANALYSIS
    # ============================
    elif page == "Category Analysis":

        monthly_cat = (
            df.groupby(["transaction_type", "year_month", "category"])["amount"]
            .sum()
            .reset_index()
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
    st.info("Upload a transaction CSV file to begin.")

st.markdown("---")
st.caption(FOOTER_TEXT)
