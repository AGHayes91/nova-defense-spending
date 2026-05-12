import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="NOVA Defense Tracker", layout="wide")
st.title("🛡️ DoD Award Impact & Historical Trends")

# 2. Sidebar - Years to analyze
target_year = st.sidebar.selectbox("Leaderboard Fiscal Year", [2024, 2025, 2026], index=0)

# 3. Data Functions with Error Handling
@st.cache_data
def get_historical_trends():
    url = "https://usaspending.gov"
    payload = {
        "group": "fiscal_year",
        "filters": {
            "time_period": [{"start_date": "2018-10-01", "end_date": "2026-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        results = r.json().get('results', [])
        data = [{"Year": i['time_period']['fiscal_year'], "Amount": float(i['aggregated_amount'])} for i in results]
        return pd.DataFrame(data).sort_values("Year")
    except Exception as e:
        st.error(f"Trend Data Error: {e}")
        return pd.DataFrame()

# 4. App Layout
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🏆 Top Winners", "📍 Regional Impact"])

with tab1:
    df_hist = get_historical_trends()
    if not df_hist.empty:
        st.plotly_chart(px.area(df_hist, x="Year", y="Amount", title="DoD Spending Growth (2019-2026)"))
    else:
        st.warning("Trend data currently unavailable from API.")

with tab2:
    st.subheader(f"Top 10 Recipients for FY {target_year}")
    url_cat = "https://usaspending.gov"
    payload_cat = {
        "category": "recipient",
        "filters": {
            "time_period": [{"start_date": f"{target_year-1}-10-01", "end_date": f"{target_year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "limit": 10
    }
    try:
        res_cat = requests.post(url_cat, json=payload_cat)
        df_winners = pd.DataFrame(res_cat.json().get('results', []))
        if not df_winners.empty:
            st.plotly_chart(px.bar(df_winners, x='amount', y='name', orientation='h', color='amount'))
        else:
            st.info("No leaderboard data for this year yet.")
    except Exception as e:
        st.error(f"Leaderboard Error: {e}")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.write("**National State View**")
        payload_state = payload_cat.copy()
        payload_state["category"] = "state"
        try:
            res_state = requests.post(url_cat, json=payload_state)
            df_state = pd.DataFrame(res_state.json().get('results', []))
            if not df_state.empty:
                st.plotly_chart(px.choropleth(df_state, locations='code', locationmode="USA-states", color='amount', scope="usa"))
        except:
            st.write("Map unavailable.")

    with col2:
        st.write("**Northern Virginia Impact**")
        nova_counties = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]
        url_award = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
        payload_nova = {
            "filters": {
                "time_period": [{"start_date": f"{target_year-1}-10-01", "end_date": f"{target_year}-09-30"}],
                "place_of_performance_locations": [{"country": "USA", "state": "VA"}],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
            },
            "fields": ["Recipient Name", "Award Amount", "Place of Performance County"],
            "limit": 100
        }
        try:
            res_nova = requests.post(url_award, json=payload_nova)
            df_nova_raw = pd.DataFrame(res_nova.json().get('results', []))
            if not df_nova_raw.empty:
                df_nova = df_nova_raw[df_nova_raw['Place of Performance County'].str.upper().isin(nova_counties)]
                st.dataframe(df_nova)
            else:
                st.write("No NOVA records found in top 100 VA awards.")
        except:
            st.write("NOVA Data Error.")
