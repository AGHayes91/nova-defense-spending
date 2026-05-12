import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Defense Awards Mockup", layout="wide")
st.title("🛡️ DoD Award Impact: 2019 - 2025")
st.markdown("---")

def fetch_data(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json().get('results', [])
    except:
        return []
    return []

# --- TOP SECTION: HISTORICAL TREND ---
st.subheader("📈 National DoD Spending Growth (2019-2025)")
hist_payload = {
    "group": "fiscal_year",
    "filters": {
        "time_period": [{"start_date": "2018-10-01", "end_date": "2025-09-30"}],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
    }
}
hist_results = fetch_data("https://usaspending.gov", hist_payload)

if hist_results:
    df_hist = pd.DataFrame([{"Year": i['time_period']['fiscal_year'], "Amount": float(i['aggregated_amount'])} for i in hist_results])
    df_hist = df_hist[df_hist['Year'].astype(int) <= 2025].sort_values("Year")
    st.plotly_chart(px.area(df_hist, x="Year", y="Amount", height=350), use_container_width=True)

st.markdown("---")

# --- BOTTOM SECTION: TOP COMPANIES 2024-25 ---
st.subheader("🏆 Top Award Winners (FY 2024 - 2025)")
# We combine 2024 and 2025 data for a broader snapshot
company_payload = {
    "category": "recipient",
    "filters": {
        "time_period": [
            {"start_date": "2023-10-01", "end_date": "2025-09-30"}
        ],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
    },
    "limit": 15
}
company_results = fetch_data("https://usaspending.gov", company_payload)

if company_results:
    df_companies = pd.DataFrame(company_results)
    # Visualizing the top winners
    fig = px.bar(
        df_companies, 
        x='amount', 
        y='name', 
        orientation='h', 
        color='amount',
        labels={'name': 'Company', 'amount': 'Total Award Amount ($)'},
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Award data is processing. Note that DoD has a 90-day reporting delay for contract data.")
