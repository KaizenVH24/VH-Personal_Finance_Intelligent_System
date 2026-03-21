"""
app.py — PFIS main application
Clean, minimal Streamlit UI with full financial intelligence pipeline.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from config import (
    APP_TITLE, APP_SUBTITLE, FOOTER_TEXT,
    DEFAULT_MONTHLY_BUDGET, DEFAULT_CATEGORY_BUDGETS,
    CHART_COLORS, CATEGORY_ORDER,
)
from utils.data_loader       import load_data
from utils.categorizer       import apply_categorization, assign_transaction_type
from utils.anomaly_detector  import detect_large_transactions, detect_anomalies
from utils.aggregator        import add_time_features, monthly_category_summary, merchant_summary, monthly_cashflow
from utils.health_score      import calculate_financial_health_score, monthly_health_trend
from utils.forecasting       import forecast_next_months
from utils.savings_prediction import predict_savings
from utils.recurring         import detect_recurring, monthly_recurring_total
from utils.insights          import generate_insights
from utils.report_generator  import generate_pdf_report


# ── page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Base ── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"],
    .main,
    .main > div { background: #0A0A0A !important; color: #E5E7EB; }

    /* Sidebar */
    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"] {
        background: #111111 !important;
        border-right: 1px solid #1F1F1F;
    }

    /* Top header bar */
    [data-testid="stHeader"] { background: #0A0A0A !important; }

    /* Block container spacing */
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* All text defaults */
    p, span, div, label, li { color: #D1D5DB; }
    h1, h2, h3, h4, h5, h6  { color: #F9FAFB !important; font-weight: 600; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #141414 !important;
        border: 1px solid #2A2A2A;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    [data-testid="stMetricLabel"] { font-size: 0.78rem; color: #6B7280 !important; font-weight: 500; }
    [data-testid="stMetricValue"] { font-size: 1.5rem;  color: #F9FAFB !important; font-weight: 700; }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }

    /* Divider */
    hr { border: none; border-top: 1px solid #1F1F1F; margin: 1.5rem 0; }

    /* Inputs, selects, text areas */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-baseweb="select"] > div,
    [data-baseweb="input"]  > div,
    [data-baseweb="textarea"] textarea {
        background: #1A1A1A !important;
        border-color: #2A2A2A !important;
        color: #E5E7EB !important;
    }
    [data-baseweb="select"] svg { fill: #9CA3AF; }

    /* Dropdown menu */
    [data-baseweb="popover"] [role="listbox"],
    [data-baseweb="menu"]    { background: #1A1A1A !important; border: 1px solid #2A2A2A; }
    [data-baseweb="option"]  { background: #1A1A1A !important; color: #E5E7EB !important; }
    [data-baseweb="option"]:hover { background: #252525 !important; }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #141414;
        border: 1px dashed #2A2A2A;
        border-radius: 8px;
    }
    [data-testid="stFileUploader"] label { color: #9CA3AF !important; }

    /* Tabs */
    [data-testid="stTabs"] [role="tablist"] { background: #111111; border-bottom: 1px solid #1F1F1F; }
    [data-testid="stTabs"] [role="tab"]     { color: #6B7280 !important; }
    [data-testid="stTabs"] [aria-selected="true"] { color: #F9FAFB !important; border-bottom: 2px solid #3B82F6; }

    /* DataFrames / tables */
    [data-testid="stDataFrame"]             { border-radius: 8px; overflow: hidden; }
    [data-testid="stDataFrame"] table       { background: #141414 !important; }
    [data-testid="stDataFrame"] thead th   { background: #1A1A1A !important; color: #9CA3AF !important; border-bottom: 1px solid #2A2A2A; }
    [data-testid="stDataFrame"] tbody td   { background: #141414 !important; color: #D1D5DB !important; border-bottom: 1px solid #1A1A1A; }
    [data-testid="stDataFrame"] tbody tr:hover td { background: #1F1F1F !important; }

    /* Alert / info / success / warning / error boxes */
    [data-testid="stAlert"]                       { border-radius: 8px; }
    div[data-baseweb="notification"]              { background: #1A1A1A !important; border-left-width: 3px; }

    /* Radio buttons in sidebar */
    [data-testid="stRadio"] label              { color: #D1D5DB !important; font-size: 0.9rem; }
    [data-testid="stRadio"] [role="radio"] div { border-color: #3B82F6 !important; }

    /* Caption text */
    [data-testid="stCaptionContainer"],
    small, .caption { color: #6B7280 !important; }

    /* Progress bar */
    [data-testid="stProgressBar"] > div > div { background: #3B82F6; }
    [data-testid="stProgressBar"] > div       { background: #1F1F1F; }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background: #1A1A1A !important;
        border: 1px solid #2A2A2A !important;
        color: #E5E7EB !important;
        border-radius: 8px;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: #252525 !important;
        border-color: #3B82F6 !important;
    }

    /* Insight cards */
    .insight-card {
        background: #141414;
        border-left: 3px solid #3B82F6;
        border-radius: 0 8px 8px 0;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        color: #D1D5DB;
    }

    /* Scrollbar */
    ::-webkit-scrollbar       { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0A0A0A; }
    ::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #3A3A3A; }
</style>
""", unsafe_allow_html=True)


# ── plotly theme helper ──────────────────────────────────────────────────────
def _fig_style(fig):
    fig.update_layout(
        paper_bgcolor="#141414",
        plot_bgcolor="#141414",
        font=dict(family="Inter, sans-serif", size=12, color="#D1D5DB"),
        margin=dict(t=30, b=30, l=10, r=10),
        legend=dict(bgcolor="#1A1A1A", bordercolor="#2A2A2A", borderwidth=1,
                    font=dict(color="#D1D5DB")),
        xaxis=dict(gridcolor="#1F1F1F", showline=False,
                   tickfont=dict(color="#6B7280"), title_font=dict(color="#9CA3AF")),
        yaxis=dict(gridcolor="#1F1F1F", showline=False,
                   tickfont=dict(color="#6B7280"), title_font=dict(color="#9CA3AF")),
    )
    return fig


# ── sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Statement",
        type=["csv", "xlsx", "xls", "pdf"],
        help="Supports Slice PDF, or any CSV/Excel with date, description, amount columns.",
    )

    st.divider()

    page = st.radio(
        "Navigate",
        ["Overview", "Transactions", "Categories", "Forecast", "Goals"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(FOOTER_TEXT)


# ── no file uploaded ─────────────────────────────────────────────────────────
if not uploaded_file:
    st.markdown("## Upload a bank statement to begin")
    st.markdown("""
    **Supported formats**
    - Bank PDF statements
    - Any bank's CSV export with `date`, `description`, `amount` columns
    - Excel (.xlsx / .xls) in the same format

    **What you get**
    - Merchant-level spend categorisation
    - Financial health score (0–100)
    - Anomaly and large transaction detection
    - Recurring subscription detection
    - 3-month expense and savings forecast
    - Savings goal tracker
    - Downloadable PDF report
    """)
    st.stop()


# ── data pipeline ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Analysing your statement…")
def run_pipeline(file_bytes, file_name):
    import io
    fake_file = io.BytesIO(file_bytes)
    fake_file.name = file_name

    df = load_data(fake_file)
    df = apply_categorization(df)
    df = assign_transaction_type(df)
    df, threshold = detect_large_transactions(df)
    df = detect_anomalies(df)
    df = add_time_features(df)
    return df, threshold


try:
    file_bytes = uploaded_file.read()
    df, large_threshold = run_pipeline(file_bytes, uploaded_file.name)
except Exception as e:
    st.error(f"Could not parse the file: {e}")
    st.info("For PDFs, make sure it's a Bank statement. For CSV/Excel, ensure columns named `date`, `description`, and `amount` exist.")
    st.stop()

if df.empty:
    st.warning("No transactions found in the uploaded file. Check the format and try again.")
    st.stop()

# ── derived aggregates (computed once, used across pages) ─────────────────────
total_income   = df[df["transaction_type"] == "Income"]["amount"].sum()
total_expense  = df[df["transaction_type"] == "Expense"]["amount"].sum()
net_savings    = total_income - total_expense
savings_ratio  = net_savings / total_income if total_income else 0

score, breakdown       = calculate_financial_health_score(df)
insights               = generate_insights(df)
cashflow               = monthly_cashflow(df)
merchant_totals        = merchant_summary(df, top_n=10)
recurring_df           = detect_recurring(df)
monthly_committed      = monthly_recurring_total(recurring_df)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
if page == "Overview":

    # ── top metrics ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income",  f"₹ {total_income:,.0f}")
    c2.metric("Total Expense", f"₹ {total_expense:,.0f}")
    c3.metric("Net Savings",   f"₹ {net_savings:,.0f}",
              delta=f"{savings_ratio*100:.1f}% of income")
    c4.metric("Health Score",  f"{score} / 100")

    st.divider()

    # ── health score + cashflow ──────────────────────────────────
    left, right = st.columns([1, 2])

    with left:
        st.markdown("#### Financial Health")

        # Score gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            gauge=dict(
                axis=dict(range=[0, 100], tickwidth=1),
                bar=dict(color="#2563EB"),
                steps=[
                    dict(range=[0,  40], color="#3D1515"),
                    dict(range=[40, 60], color="#3D2E00"),
                    dict(range=[60, 80], color="#0F2D1A"),
                    dict(range=[80,100], color="#0A3320"),
                ],
            ),
            number=dict(font=dict(size=36)),
        ))
        fig_gauge.update_layout(height=200, margin=dict(t=10, b=10, l=20, r=20),
                                paper_bgcolor="#141414",
                                font=dict(color="#D1D5DB"))
        st.plotly_chart(fig_gauge, use_container_width=True)

        if score >= 80:
            st.success("Excellent Financial Health")
        elif score >= 60:
            st.info("Financially Stable")
        elif score >= 40:
            st.warning("Some Financial Risk")
        else:
            st.error("High Financial Risk")

        st.markdown("**Score Breakdown**")
        for k, v in breakdown.items():
            if k == "note":
                continue
            st.markdown(f"<small style='color:#6B7280'>{k}</small>  \n**{v}**", unsafe_allow_html=True)

    with right:
        st.markdown("#### Monthly Cash Flow")
        if not cashflow.empty:
            fig_cf = go.Figure()
            fig_cf.add_bar(x=cashflow["year_month"], y=cashflow["Income"],
                           name="Income",  marker_color="#22C55E")
            fig_cf.add_bar(x=cashflow["year_month"], y=cashflow["Expense"],
                           name="Expense", marker_color="#EF4444")
            fig_cf.add_scatter(x=cashflow["year_month"], y=cashflow["Savings"],
                               mode="lines+markers", name="Net Savings",
                               line=dict(color="#2563EB", width=2))
            fig_cf.update_layout(barmode="group", height=280)
            st.plotly_chart(_fig_style(fig_cf), use_container_width=True)

    st.divider()

    # ── top merchants + health trend ─────────────────────────────
    left2, right2 = st.columns([1, 1])

    with left2:
        st.markdown("#### Top Merchants by Spend")
        if not merchant_totals.empty:
            fig_merch = px.bar(
                merchant_totals.sort_values("amount"),
                x="amount", y="merchant",
                orientation="h",
                labels={"amount": "₹ Spent", "merchant": ""},
                color_discrete_sequence=["#2563EB"],
            )
            fig_merch.update_layout(height=320, showlegend=False)
            st.plotly_chart(_fig_style(fig_merch), use_container_width=True)

    with right2:
        st.markdown("#### Health Score Trend")
        trend = monthly_health_trend(df)
        if not trend.empty:
            fig_trend = px.line(
                trend, x="year_month", y="score",
                markers=True,
                labels={"year_month": "", "score": "Health Score"},
                color_discrete_sequence=["#2563EB"],
            )
            fig_trend.update_traces(line_width=2, marker_size=7)
            fig_trend.update_layout(height=320, yaxis_range=[0, 100])
            st.plotly_chart(_fig_style(fig_trend), use_container_width=True)

    st.divider()

    # ── insights ─────────────────────────────────────────────────
    st.markdown("#### Insights")
    for insight in insights:
        st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

    st.divider()

    # ── PDF download ─────────────────────────────────────────────
    st.markdown("#### Export Report")
    pdf = generate_pdf_report(df, score, breakdown, insights)
    st.download_button(
        label="Download PDF Report",
        data=pdf,
        file_name="PFIS_Report_VH24.pdf",
        mime="application/pdf",
        use_container_width=False,
    )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTIONS
# ════════════════════════════════════════════════════════════════════════════
elif page == "Transactions":

    st.markdown("### Transactions")

    # ── filters ──────────────────────────────────────────────────
    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])

    with f1:
        search = st.text_input("Search merchant or description", placeholder="e.g. Zomato, Zerodha")
    with f2:
        type_filter = st.selectbox("Type", ["All", "Income", "Expense"])
    with f3:
        cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
        cat_filter = st.selectbox("Category", cats)
    with f4:
        date_range = st.date_input(
            "Date range",
            value=(df["date"].min().date(), df["date"].max().date()),
            min_value=df["date"].min().date(),
            max_value=df["date"].max().date(),
        )

    # Apply filters
    filtered = df.copy()

    if search:
        mask = (
            filtered["merchant"].str.contains(search, case=False, na=False) |
            filtered["description"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    if type_filter != "All":
        filtered = filtered[filtered["transaction_type"] == type_filter]

    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]

    if len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        filtered = filtered[(filtered["date"] >= start) & (filtered["date"] <= end)]

    # ── transaction table ────────────────────────────────────────
    display_cols = ["date", "merchant", "category", "amount", "transaction_type", "is_large", "is_anomaly"]
    display_cols = [c for c in display_cols if c in filtered.columns]

    st.markdown(f"**{len(filtered):,} transactions**")
    st.dataframe(
        filtered[display_cols].rename(columns={
            "date": "Date", "merchant": "Merchant", "category": "Category",
            "amount": "Amount (₹)", "transaction_type": "Type",
            "is_large": "Large?", "is_anomaly": "Anomaly?",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ── flagged transactions ─────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["Large Transactions", "Anomalies", "Recurring"])

    with tab1:
        large = df[df["is_large"] == True]
        if large.empty:
            st.info("No large transactions detected.")
        else:
            st.caption(f"Threshold: ₹ {large_threshold:,.0f} (mean + 2×std of expenses)")
            st.dataframe(
                large[["date","merchant","category","amount"]].rename(columns={
                    "date":"Date","merchant":"Merchant","category":"Category","amount":"Amount (₹)"
                }),
                hide_index=True, use_container_width=True,
            )

    with tab2:
        anomalies = df[df["is_anomaly"] == True]
        if anomalies.empty:
            st.info("No anomalous transactions detected.")
        else:
            st.caption("Detected using Isolation Forest (unsupervised ML).")
            st.dataframe(
                anomalies[["date","merchant","category","amount"]].rename(columns={
                    "date":"Date","merchant":"Merchant","category":"Category","amount":"Amount (₹)"
                }),
                hide_index=True, use_container_width=True,
            )

    with tab3:
        if recurring_df.empty:
            st.info("No recurring transactions detected. Upload multiple months of data for better detection.")
        else:
            st.caption(f"Estimated monthly committed spend: ₹ {monthly_committed:,.0f}")
            st.dataframe(
                recurring_df[[
                    "merchant","category","amount","frequency",
                    "months_active","likely_day","first_seen","last_seen"
                ]].rename(columns={
                    "merchant":"Merchant","category":"Category","amount":"Avg Amount (₹)",
                    "frequency":"Count","months_active":"Months Active",
                    "likely_day":"Typical Day","first_seen":"First","last_seen":"Last",
                }),
                hide_index=True, use_container_width=True,
            )


# ════════════════════════════════════════════════════════════════════════════
# PAGE: CATEGORIES
# ════════════════════════════════════════════════════════════════════════════
elif page == "Categories":

    st.markdown("### Category Analysis")

    expense_df = df[df["transaction_type"] == "Expense"]
    if expense_df.empty:
        st.warning("No expense transactions found.")
        st.stop()

    # ── monthly stacked bar ──────────────────────────────────────
    st.markdown("#### Monthly Spend by Category")
    monthly_cat = monthly_category_summary(df)

    if not monthly_cat.empty:
        color_map = {k: v for k, v in CHART_COLORS.items()}
        fig_stack = px.bar(
            monthly_cat, x="year_month", y="amount", color="category",
            labels={"year_month": "", "amount": "₹ Spent", "category": "Category"},
            color_discrete_map=color_map,
        )
        fig_stack.update_layout(barmode="stack", height=350, legend_title_text="")
        st.plotly_chart(_fig_style(fig_stack), use_container_width=True)

    st.divider()

    # ── pie + budget table ───────────────────────────────────────
    left, right = st.columns([1, 1])

    cat_totals = expense_df.groupby("category")["amount"].sum().reset_index()
    cat_totals = cat_totals.sort_values("amount", ascending=False)

    with left:
        st.markdown("#### Spend Distribution")
        fig_pie = px.pie(
            cat_totals, values="amount", names="category",
            color="category", color_discrete_map=CHART_COLORS,
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=320, showlegend=False)
        st.plotly_chart(_fig_style(fig_pie), use_container_width=True)

    with right:
        st.markdown("#### Budget vs Actual")
        months_count = df[["year", "month_number"]].drop_duplicates().shape[0] or 1

        budget_rows = []
        for _, row in cat_totals.iterrows():
            cat    = row["category"]
            actual = row["amount"]
            avg_mo = actual / months_count
            budget = DEFAULT_CATEGORY_BUDGETS.get(cat, None)

            if budget:
                pct    = (avg_mo / budget) * 100
                status = "🟢" if pct < 80 else ("🟡" if pct < 100 else "🔴")
                budget_rows.append({
                    "Category":          cat,
                    "Avg Monthly (₹)":   f"{avg_mo:,.0f}",
                    "Budget (₹)":        f"{budget:,.0f}",
                    "Usage":             f"{pct:.0f}%",
                    "Status":            status,
                })

        if budget_rows:
            st.dataframe(
                pd.DataFrame(budget_rows),
                hide_index=True,
                use_container_width=True,
            )

            # Alerts for over-budget categories
            alerts = [r for r in budget_rows if r["Status"] == "🔴"]
            if alerts:
                st.warning(f"**Over budget in {len(alerts)} categor{'ies' if len(alerts)>1 else 'y'}:** " +
                           ", ".join(r["Category"] for r in alerts))
        else:
            st.info("No budget data configured. Edit DEFAULT_CATEGORY_BUDGETS in config.py.")

    st.divider()

    # ── weekday spending pattern ─────────────────────────────────
    st.markdown("#### Spending by Day of Week")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_spend = (
        expense_df.groupby("day_of_week")["amount"].sum()
        .reindex(day_order, fill_value=0)
        .reset_index()
    )
    fig_day = px.bar(
        day_spend, x="day_of_week", y="amount",
        labels={"day_of_week": "", "amount": "₹ Spent"},
        color_discrete_sequence=["#2563EB"],
    )
    fig_day.update_layout(height=260)
    st.plotly_chart(_fig_style(fig_day), use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE: FORECAST
# ════════════════════════════════════════════════════════════════════════════
elif page == "Forecast":

    st.markdown("### Forecast")
    st.caption("Linear trend model on monthly aggregates. Works best with 3+ months of data.")

    # ── expense forecast ─────────────────────────────────────────
    st.markdown("#### Expense Forecast")

    cats = ["Total"] + sorted(df[df["transaction_type"] == "Expense"]["category"].unique().tolist())
    sel_cat = st.selectbox("Category", cats, key="fc_cat")
    cat_arg = None if sel_cat == "Total" else sel_cat

    fc_result = forecast_next_months(df, category=cat_arg)

    if fc_result:
        hist, fcast = fc_result
        fig_fc = go.Figure()
        fig_fc.add_trace(go.Scatter(
            x=hist["year_month"], y=hist["amount"],
            mode="lines+markers", name="Historical",
            line=dict(color="#2563EB", width=2),
        ))
        fig_fc.add_trace(go.Scatter(
            x=fcast["year_month"], y=fcast["predicted_expense"],
            mode="lines+markers", name="Forecast",
            line=dict(color="#F97316", width=2, dash="dot"),
        ))
        fig_fc.add_trace(go.Scatter(
            x=pd.concat([fcast["year_month"], fcast["year_month"][::-1]]),
            y=pd.concat([fcast["upper_bound"], fcast["lower_bound"][::-1]]),
            fill="toself", fillcolor="rgba(249,115,22,0.1)",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI",
        ))
        fig_fc.update_layout(height=300)
        st.plotly_chart(_fig_style(fig_fc), use_container_width=True)

        col1, col2, col3 = st.columns(3)
        for i, (_, row) in enumerate(fcast.iterrows()):
            [col1, col2, col3][i].metric(
                row["year_month"],
                f"₹ {row['predicted_expense']:,.0f}",
                help=f"Range: ₹{row['lower_bound']:,.0f} – ₹{row['upper_bound']:,.0f}",
            )
    else:
        st.info("Need at least 2 months of data to generate a forecast.")

    st.divider()

    # ── savings forecast ─────────────────────────────────────────
    st.markdown("#### Savings Forecast")
    sv_result = predict_savings(df)

    if sv_result:
        sv_hist, sv_fcast = sv_result

        fig_sv = go.Figure()
        fig_sv.add_trace(go.Bar(
            x=sv_hist["year_month"], y=sv_hist["savings"],
            name="Actual Savings",
            marker_color=["#22C55E" if v >= 0 else "#EF4444" for v in sv_hist["savings"]],
        ))
        fig_sv.add_trace(go.Scatter(
            x=sv_fcast["year_month"], y=sv_fcast["predicted_savings"],
            mode="lines+markers", name="Forecast",
            line=dict(color="#2563EB", width=2, dash="dot"),
        ))
        fig_sv.update_layout(height=280)
        st.plotly_chart(_fig_style(fig_sv), use_container_width=True)

        # Show CI band explicitly
        cols = st.columns(len(sv_fcast))
        for i, (_, row) in enumerate(sv_fcast.iterrows()):
            cols[i].metric(
                row["year_month"],
                f"₹ {row['predicted_savings']:,.0f}",
                help=f"Range: ₹{row['lower_bound']:,.0f} – ₹{row['upper_bound']:,.0f}",
            )
    else:
        st.info("Need at least 2 months of data to forecast savings.")

    st.divider()

    # ── budget planner ───────────────────────────────────────────
    st.markdown("#### Budget Planner")
    monthly_budget = st.number_input(
        "Monthly Budget (₹)", min_value=0.0,
        value=float(DEFAULT_MONTHLY_BUDGET), step=1000.0,
    )
    months_count       = df[["year","month_number"]].drop_duplicates().shape[0] or 1
    avg_monthly_expense= total_expense / months_count

    b1, b2, b3 = st.columns(3)
    b1.metric("Your Budget",          f"₹ {monthly_budget:,.0f}")
    b2.metric("Avg Monthly Expense",  f"₹ {avg_monthly_expense:,.0f}")
    diff = monthly_budget - avg_monthly_expense
    b3.metric("Difference",           f"₹ {abs(diff):,.0f}",
              delta=f"{'Under' if diff>=0 else 'Over'} budget")


# ════════════════════════════════════════════════════════════════════════════
# PAGE: GOALS
# ════════════════════════════════════════════════════════════════════════════
elif page == "Goals":

    st.markdown("### Savings Goals")

    g1, g2 = st.columns(2)
    with g1:
        goal_amount = st.number_input("Target Savings Amount (₹)",
                                      min_value=1000.0, value=50_000.0, step=5000.0)
    with g2:
        goal_months = st.number_input("Target Timeline (months)",
                                      min_value=1, max_value=60, value=6)

    required_monthly = goal_amount / goal_months

    st.divider()

    # Current savings capacity
    months_count  = df[["year","month_number"]].drop_duplicates().shape[0] or 1
    avg_monthly_savings = net_savings / months_count

    col1, col2, col3 = st.columns(3)
    col1.metric("Goal Amount",         f"₹ {goal_amount:,.0f}")
    col2.metric("Required per Month",  f"₹ {required_monthly:,.0f}")
    col3.metric("Current Avg Savings", f"₹ {avg_monthly_savings:,.0f}")

    st.divider()

    # Progress assessment
    if avg_monthly_savings <= 0:
        st.error("Your current savings are zero or negative. This goal is not achievable without reducing expenses or increasing income.")
    else:
        projected_months = goal_amount / avg_monthly_savings
        projected_amount_in_target = avg_monthly_savings * goal_months

        progress = min(1.0, projected_amount_in_target / goal_amount)
        st.markdown(f"#### Goal Progress Projection")
        st.progress(progress, text=f"{progress*100:.0f}% — Projected ₹ {projected_amount_in_target:,.0f} in {goal_months} months")

        if avg_monthly_savings >= required_monthly:
            st.success(
                f"On track. At your current savings rate of ₹ {avg_monthly_savings:,.0f}/month, "
                f"you'll hit ₹ {goal_amount:,.0f} in **{projected_months:.1f} months**."
            )
        else:
            gap = required_monthly - avg_monthly_savings
            st.warning(
                f"Behind pace. You need ₹ {gap:,.0f} more per month to hit this goal in {goal_months} months. "
                f"At the current rate, it'll take **{projected_months:.1f} months**."
            )

        # Forecast overlay
        sv_result = predict_savings(df)
        if sv_result:
            _, sv_fcast = sv_result
            st.markdown("#### Forecasted Monthly Savings (Next 3 Months)")
            cols = st.columns(len(sv_fcast))
            for i, (_, row) in enumerate(sv_fcast.iterrows()):
                delta_str = "✓ on track" if row["predicted_savings"] >= required_monthly else "✗ below target"
                cols[i].metric(row["year_month"], f"₹ {row['predicted_savings']:,.0f}", delta_str)

    st.divider()

    # Recurring expenses as a context
    if not recurring_df.empty:
        st.markdown("#### Committed Monthly Expenses (Recurring)")
        st.caption(
            f"These ₹ {monthly_committed:,.0f}/month in recurring charges reduce your savings capacity. "
            "Review if any can be cancelled."
        )
        st.dataframe(
            recurring_df[["merchant","category","amount"]].rename(columns={
                "merchant":"Merchant","category":"Category","amount":"Monthly Amount (₹)"
            }),
            hide_index=True, use_container_width=True,
        )


# ── footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(FOOTER_TEXT)