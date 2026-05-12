import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Mockup", layout="wide")
st.title("🛡️ DoD Spending Impact (2019-2025)")

def safe_fetch(url, payload):
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            return r.json().get('results', [])
        st.error(f"API Error {r.status_code}")
    except:
        st.error("Connection failed.")
    return []

# --- 1. HISTORICAL TREND ---
hist_payload = {
    "group": "fiscal_year",
    "filters": {"time_period": [{"start_date": "2018-10-01", "end_date": "2025-09-30"}],
                "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]}
}
hist_res = safe_fetch("https://api.usaspending.gov/api/v2/search/spending_over_time/", hist_payload)

if hist_res:
    df_hist = pd.DataFrame([{"Year": i['time_period']['fiscal_year'], "Amt": float(i['aggregated_amount'])} for i in hist_res])
    st.plotly_chart(px.area(df_hist.sort_values("Year"), x="Year", y="Amt"), use_container_width=True)
else:
    st.warning("No Trend Data Available.")

# --- 2. NOVA FOCUS (Using FIPS for Stability) ---
st.subheader("📍 Northern Virginia Snapshot")
nova_fips = ["013", "059", "107", "510"] # Arlington, Fairfax, Loudoun, Alexandria
nova_payload = {
    "filters": {
        "time_period": [{"start_date": "2024-10-01", "end_date": "2025-09-30"}],
        "place_of_performance_locations": [{"country": "USA", "state": "VA", "county": f} for f in nova_fips],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
    },
    "fields": ["Recipient Name", "Award Amount"],
    "limit": 10
}
nova_res = safe_fetch("https://api.usaspending.gov/api/v2/search/spending_by_award/", nova_payload)

if nova_res:
    st.table(pd.DataFrame(nova_res))
else:
    st.info("No NOVA data found for this period.")
