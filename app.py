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
from utils.forecasting import forecast_next_months
from utils.health_score import calculate_financial_health_score, monthly_health_trend
from utils.savings_prediction import predict_savings
from utils.insights import generate_insights
from utils.report_generator import generate_pdf_report


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
        
        
        st.subheader("📈 Financial Health Trend")

        trend_df = monthly_health_trend(df)

        import plotly.express as px

        fig_health = px.line(
            trend_df,
            x=trend_df.index,
            y="score",
            markers=True
        )

        fig_health.update_layout(
            xaxis_title="Month Index",
            yaxis_title="Health Score"
        )

        st.plotly_chart(fig_health, use_container_width=True)

        st.divider()
        st.subheader("💰 Budget Planner")

        monthly_budget = st.number_input(
            "Enter Your Monthly Budget (₹)",
            min_value=0.0,
            value=30000.0,
            step=1000.0
        )

        total_expense = df[df["transaction_type"] == "Expense"]["amount"].sum()
        months_count = df[["year", "month_number"]].drop_duplicates().shape[0]

        if months_count > 0:
            avg_monthly_expense = total_expense / months_count
        else:
            avg_monthly_expense = 0

        st.write(f"Average Monthly Expense: ₹ {avg_monthly_expense:,.2f}")

        difference = monthly_budget - avg_monthly_expense

        if difference > 0:
            st.success(f"You are under budget by ₹ {difference:,.2f}")
        else:
            st.error(f"You are exceeding budget by ₹ {abs(difference):,.2f}")


        st.divider()
        st.subheader("🔮 Expense Forecasting")

        categories = df[df["transaction_type"] == "Expense"]["category"].unique()
        selected_category = st.selectbox(
            "Select Category (or choose Total Expense)",
            ["Total"] + list(categories)
        )

        if selected_category == "Total":
            forecast_result = forecast_next_months(df)
        else:
            forecast_result = forecast_next_months(df, category=selected_category)

        if forecast_result is None:
            st.info("Not enough data for forecasting.")
        else:
            historical_data, forecast_df = forecast_result

            import plotly.graph_objects as go

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=historical_data["time_index"],
                y=historical_data["amount"],
                mode='lines+markers',
                name="Historical Expense"
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df["future_index"],
                y=forecast_df["predicted_expense"],
                mode='lines+markers',
                name="Predicted Expense"
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df["future_index"],
                y=forecast_df["upper_bound"],
                mode='lines',
                name="Upper Confidence",
                line=dict(dash='dash')
            ))

            fig.add_trace(go.Scatter(
                x=forecast_df["future_index"],
                y=forecast_df["lower_bound"],
                mode='lines',
                name="Lower Confidence",
                line=dict(dash='dash')
            ))

            fig.update_layout(
                xaxis_title="Time Index",
                yaxis_title="Expense Amount"
            )

            st.plotly_chart(fig, use_container_width=True)


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

        st.subheader("💹 Savings Forecast (Next 3 Months)")

        savings_pred = predict_savings(df)

        if savings_pred is None:
            st.info("Not enough data for savings prediction.")
        else:
            for i, value in enumerate(savings_pred, 1):
                st.write(f"Month +{i}: ₹ {round(value,2)}")

        st.subheader("🤖 Automated Financial Insights")

        insights = generate_insights(df)

        for insight in insights:
            st.write("•", insight)

        st.subheader("📄 Download Executive Report")

        pdf_buffer = generate_pdf_report(df, score, breakdown, insights)

        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="PFIS_Report_VH24.pdf",
            mime="application/pdf"
        )

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
