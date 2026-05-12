import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# 1. Page Config
st.set_page_config(page_title="NOVA Defense Tracker", layout="wide", page_icon="🛡️")
st.title("🛡️ DoD Award Impact & Historical Trends (2019-2025)")

# 2. Sidebar - Removed 2026 to ensure data stability
target_year = st.sidebar.selectbox("Fiscal Year for Details", [2025, 2024, 2023, 2022, 2021, 2020, 2019], index=0)

# 3. Resilient API Fetcher
def fetch_usaspending(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code == 200 and "application/json" in r.headers.get("Content-Type", ""):
            return r.json()
        elif r.status_code == 429:
            st.error("Rate limit hit. Please wait 5 minutes.")
    except Exception as e:
        st.error(f"Connection Error: {e}")
    return None

tab1, tab2, tab3 = st.tabs(["📈 Historical Trends", "🏆 Top Winners", "📍 Regional Impact"])

# --- TAB 1: HISTORICAL TRENDS (2019-2025) ---
with tab1:
    st.subheader("National DoD Spending (2019 - 2025)")
    hist_payload = {
        "group": "fiscal_year",
        "filters": {
            "time_period": [{"start_date": "2018-10-01", "end_date": "2025-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        }
    }
    hist_data = fetch_usaspending("https://usaspending.gov", hist_payload)
    
    if hist_data and 'results' in hist_data:
        df_hist = pd.DataFrame([
            {"Year": i['time_period']['fiscal_year'], "Amount": float(i['aggregated_amount'])} 
            for i in hist_data['results']
        ]).sort_values("Year")
        # Ensure we only show up to 2025
        df_hist = df_hist[df_hist['Year'].astype(int) <= 2025]
        st.plotly_chart(px.area(df_hist, x="Year", y="Amount", title="DoD Obligations Over Time"), use_container_width=True)
    else:
        st.info("Trend data is taking a moment to load. Try refreshing.")

# --- TAB 2: TOP WINNERS ---
with tab2:
    st.subheader(f"Top 10 Recipients (FY {target_year})")
    win_payload = {
        "category": "recipient",
        "filters": {
            "time_period": [{"start_date": f"{target_year-1}-10-01", "end_date": f"{target_year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "limit": 10
    }
    win_data = fetch_usaspending("https://usaspending.gov", win_payload)
    if win_data and 'results' in win_data:
        df_winners = pd.DataFrame(win_data['results'])
        st.plotly_chart(px.bar(df_winners, x='amount', y='name', orientation='h', color='amount'), use_container_width=True)

# --- TAB 3: REGIONAL IMPACT ---
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**State Spending Map**")
        state_payload = win_payload.copy()
        state_payload["category"] = "state"
        state_data = fetch_usaspending("https://usaspending.gov", state_payload)
        if state_data and 'results' in state_data:
            df_state = pd.DataFrame(state_data['results'])
            st.plotly_chart(px.choropleth(df_state, locations='code', locationmode="USA-states", color='amount', scope="usa"), use_container_width=True)

    with col2:
        st.markdown("**NOVA Local Contracts**")
        nova_counties = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]
        nova_payload = {
            "filters": {
                "time_period": [{"start_date": f"{target_year-1}-10-01", "end_date": f"{target_year}-09-30"}],
                "place_of_performance_locations": [{"country": "USA", "state": "VA"}],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
            },
            "fields": ["Recipient Name", "Award Amount", "Place of Performance County"],
            "limit": 100
        }
        nova_data = fetch_usaspending("https://usaspending.gov", nova_payload)
        if nova_data and 'results' in nova_data:
            df_nova = pd.DataFrame(nova_data['results'])
            df_nova = df_nova[df_nova['Place of Performance County'].str.upper().isin(nova_counties)]
            st.dataframe(df_nova)
