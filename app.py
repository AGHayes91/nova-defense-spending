import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Tracker", layout="wide")
st.title("🛡️ DoD Award Impact on Northern Virginia")

# Select 2024 or 2025 to ensure we see data despite reporting lags
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=1)

@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    # Correct FIPS Codes for NOVA: 
    # Arlington (013), Fairfax (059), Loudoun (107), Alexandria City (510)
    nova_fips = ["013", "059", "107", "510"]
    
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [
                {"country": "USA", "state": "VA", "county": fips} for fips in nova_fips
            ],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
        "limit": 100
    }
    
    response = requests.post(url, json=payload)
    # If this fails, it will now print the exact error message from the API
    if response.status_code != 200:
        st.error(f"API Error {response.status_code}: {response.text}")
        return pd.DataFrame()
        
    return pd.DataFrame(response.json().get('results', []))

df = get_dod_data(target_year)

if not df.empty:
    st.success(f"Loaded {len(df)} awards for FY{target_year}")
    
    # Find the right columns automatically
    county_col = next((c for c in df.columns if 'county' in c.lower()), "Place of Performance County")
    amount_col = next((c for c in df.columns if 'amount' in c.lower()), "Award Amount")
    
    st.plotly_chart(px.pie(df, values=amount_col, names=county_col, title="Spending by County"))
    st.dataframe(df)
else:
    st.warning("No results found. This is often due to the 90-day DOD reporting lag.")
