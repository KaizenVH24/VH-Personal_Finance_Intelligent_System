import streamlit as st
import pandas as pd
import plotly.express as px

from config import APP_TITLE, APP_SUBTITLE, FOOTER_TEXT
from utils.data_loader import load_data
from utils.categorizer import apply_categorization
from utils.anomaly_detector import detect_large_transactions
from utils.aggregator import add_time_features, monthly_summary
from utils.anomaly_detector import detect_large_transactions, detect_anomalies


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
    df, threshold = detect_large_transactions(df)
    df = detect_anomalies(df)
    df = add_time_features(df)


    if page == "Dashboard":

        st.subheader("📊 Financial Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Transactions", len(df))
        col2.metric("Total Expense", f"₹ {df['amount'].sum():,.2f}")
        col3.metric("Large Transaction Threshold", f"₹ {threshold:,.2f}")

        st.divider()

        # Category Distribution
        st.subheader("Category Distribution")

        category_data = df.groupby("category")["amount"].sum().reset_index()
        fig = px.pie(category_data, values="amount", names="category")
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Monthly Trend
        st.subheader("Monthly Spending Trend")

        monthly_data = (
            df.groupby(["year", "month", "month_number"])["amount"]
            .sum()
            .reset_index()
            .sort_values(["year", "month_number"])
        )

        fig2 = px.bar(
            monthly_data,
            x="month",
            y="amount",
            color="year",
            barmode="group"
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

        st.subheader("📈 Category-wise Monthly Breakdown")

        monthly_cat = monthly_summary(df)

        fig3 = px.bar(
            monthly_cat,
            x="month",
            y="amount",
            color="category",
            barmode="group"
        )

        st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Please upload a transaction CSV file from the sidebar.")

st.markdown("---")
st.caption(FOOTER_TEXT)
