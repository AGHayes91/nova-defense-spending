import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="NOVA Defense Tracker", layout="wide", page_icon="🛡️")
st.title("🛡️ DoD Award Impact & Historical Trends")
st.markdown("Analyzing federal contracts from 2019 to 2026 for Northern Virginia and National trends.")

# 2. Global Settings & API Functions
BASE_URL = "https://api.usaspending.gov/api/v2/search/"

@st.cache_data
def get_historical_trends():
    """Fetches total DoD obligations by fiscal year (2019-2026)"""
    url = f"{BASE_URL}spending_over_time/"
    payload = {
        "group": "fiscal_year",
        "filters": {
            "time_period": [{"start_date": "2018-10-01", "end_date": "2026-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200: return pd.DataFrame()
    
    results = response.json().get('results', [])
    data = [{"Year": r['time_period']['fiscal_year'], "Amount": float(r['aggregated_amount'])} for r in results]
    return pd.DataFrame(data).sort_values("Year")

@st.cache_data
def get_categorical_breakdown(category, year):
    """Fetches spending by category (recipient, state, or county)"""
    url = f"{BASE_URL}spending_by_category/"
    payload = {
        "category": category,
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "limit": 10
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200: return pd.DataFrame()
    return pd.DataFrame(response.json().get('results', []))

# 3. Sidebar - Year Control for Leaderboards
st.sidebar.header("Dashboard Filters")
target_year = st.sidebar.selectbox("Leaderboard Fiscal Year",, index=2)

# 4. App Tabs
tab_trend, tab_leader, tab_geo = st.tabs(["📈 Historical Trends", "🏆 Top Winners", "🗺️ Regional Impact"])

with tab_trend:
    st.subheader("DoD Obligations Over Time (2019–2026)")
    hist_df = get_historical_trends()
    if not hist_df.empty:
        fig = px.area(hist_df, x="Year", y="Amount", title="Total National DoD Spending Growth")
        st.plotly_chart(fig, use_container_width=True)
        st.info("Note: FY 2026 data is partially reported as of May 2026.")
    else:
        st.error("Could not load historical data.")

with tab_leader:
    st.subheader(f"Top 10 Award Winners (FY {target_year})")
    winners_df = get_categorical_breakdown('recipient', target_year)
    if not winners_df.empty:
        fig_winners = px.bar(winners_df, x='amount', y='name', orientation='h', 
                             color='amount', labels={'name': 'Recipient', 'amount': 'Total ($)'})
        st.plotly_chart(fig_winners, use_container_width=True)
        st.dataframe(winners_df[['name', 'amount']])
    else:
        st.warning("No recipient data found for this year.")

with tab_geo:
    st.subheader(f"Geographic Spending (FY {target_year})")
    geo_col1, geo_col2 = st.columns(2)
    
    with geo_col1:
        st.markdown("**By State (USA)**")
        states_df = get_categorical_breakdown('state', target_year)
        if not states_df.empty:
            st.plotly_chart(px.choropleth(states_df, locations='code', locationmode="USA-states", 
                                          color='amount', scope="usa"), use_container_width=True)
            
    with geo_col2:
        st.markdown("**NOVA Impact (Fairfax, Arlington, Loudoun)**")
        # Direct VA filter for local analysis
        payload_va = {
            "filters": {
                "time_period": [{"start_date": f"{target_year-1}-10-01", "end_date": f"{target_year}-09-30"}],
                "place_of_performance_locations": [{"country": "USA", "state": "VA"}],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
            },
            "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
            "limit": 50
        }
        res_va = requests.post(f"{BASE_URL}spending_by_award/", json=payload_va)
        if res_va.status_code == 200:
            df_va = pd.DataFrame(res_va.json().get('results', []))
            nova_fips = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]
            df_nova = df_va[df_va['Place of Performance County'].str.upper().isin(nova_fips)] if not df_va.empty else pd.DataFrame()
            if not df_nova.empty:
                st.dataframe(df_nova[['Recipient Name', 'Award Amount', 'Place of Performance County']])
            else:
                st.write("No major NOVA contracts in the top VA results for this year.")
