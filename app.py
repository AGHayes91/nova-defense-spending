import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Mockup", layout="wide")
st.title("🛡️ DoD Spending & Impact: 2019 - 2025")
st.markdown("---")

def fetch_data(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200:
            return r.json().get('results', [])
    except:
        return []
    return []

# --- 1. HISTORICAL TREND (TOP SECTION) ---
st.subheader("📈 National DoD Spending Growth")
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

# --- 2. THE SNAPSHOTS (BOTTOM SECTION) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 National Winners (2025)")
    win_payload = {
        "category": "recipient",
        "filters": {
            "time_period": [{"start_date": "2024-10-01", "end_date": "2025-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "limit": 10
    }
    win_results = fetch_data("https://usaspending.gov", win_payload)
    if win_results:
        df_winners = pd.DataFrame(win_results)
        st.plotly_chart(px.bar(df_winners, x='amount', y='name', orientation='h', color='amount', height=400), use_container_width=True)

with col2:
    st.subheader("📍 Northern Virginia Focus")
    nova_counties = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]
    nova_payload = {
        "filters": {
            "time_period": [{"start_date": "2024-10-01", "end_date": "2025-09-30"}],
            "place_of_performance_locations": [{"country": "USA", "state": "VA"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County"],
        "limit": 100
    }
    nova_results = fetch_data("https://usaspending.gov", nova_payload)
    if nova_results:
        df_nova = pd.DataFrame(nova_results)
        df_nova = df_nova[df_nova['Place of Performance County'].str.upper().isin(nova_counties)]
        # Sort and clean for display
        df_display = df_nova.sort_values("Award Amount", ascending=False).head(10)
        st.table(df_display[['Recipient Name', 'Award Amount', 'Place of Performance County']])
