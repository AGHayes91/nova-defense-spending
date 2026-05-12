import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="DoD Spending Dashboard", layout="wide")
st.title("🛡️ DoD Spending & Impact: 2019 - 2025")
st.markdown("---")

# 2. Resilient Data Fetcher
def fetch_data(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json().get('results', [])
    except Exception:
        return []
    return []

# --- SECTION 1: NATIONAL GROWTH TREND ---
st.subheader("📈 National DoD Spending Growth (2019 - 2025)")
hist_payload = {
    "group": "fiscal_year",
    "filters": {
        "time_period": [{"start_date": "2018-10-01", "end_date": "2025-09-30"}],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
    }
}
hist_res = fetch_data("https://usaspending.gov", hist_payload)

if hist_res:
    df_hist = pd.DataFrame([
        {"Year": i['time_period']['fiscal_year'], "Amount": float(i['aggregated_amount'])} 
        for i in hist_res
    ])
    # Ensure we only visualize up to the capped 2025 year
    df_hist = df_hist[df_hist['Year'].astype(int) <= 2025].sort_values("Year")
    st.plotly_chart(px.area(df_hist, x="Year", y="Amount", height=350, color_discrete_sequence=['#1f77b4']), use_container_width=True)

st.markdown("---")

# --- SECTION 2: TOP AWARD WINNERS (2024-25) ---
st.subheader("🏆 Top Award Winners (FY 2024 - 2025)")
company_payload = {
    "category": "recipient",
    "filters": {
        "time_period": [{"start_date": "2023-10-01", "end_date": "2025-09-30"}],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
    },
    "limit": 15
}
company_res = fetch_data("https://usaspending.gov", company_payload)

if company_res:
    df_comp = pd.DataFrame(company_res)
    # Aggregating and visualizing top performers
    fig = px.bar(
        df_comp, 
        x='amount', 
        y='name', 
        orientation='h', 
        color='amount',
        labels={'name': 'Recipient', 'amount': 'Total Award Amount ($)'},
        color_continuous_scale='Blues',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Award data is currently processing or subject to the standard 90-day reporting delay.")
