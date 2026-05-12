import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Tracker", layout="wide", page_icon="🛡️")
st.title("🛡️ DoD Award Impact on Northern Virginia")

# 1. Sidebar - Let's try 2024 if 2025/2026 are still empty due to reporting lags
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=1)

@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    # Broaden the search: Get all DoD awards in VA for the year, then filter locally
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [{"country": "USA", "state": "VA"}],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
        "limit": 1000 # Increase limit to ensure we catch NOVA records
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json().get('results', [])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame()

df_raw = get_dod_data(target_year)

# 2. Local Filtering for NOVA Counties
nova_counties = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]

if not df_raw.empty:
    # Use the 'Smart Mapper' to find the county column regardless of its exact API key
    county_col = next((c for c in df_raw.columns if 'county' in c.lower()), None)
    
    if county_col:
        # Standardize to uppercase for matching
        df_raw[county_col] = df_raw[county_col].str.upper()
        df = df_raw[df_raw[county_col].str.contains('|'.join(nova_counties), na=False)].copy()
        
        if df.empty:
            st.warning(f"No specific matches for NOVA found in the first 1000 VA records for {target_year}. Try 2024.")
        else:
            st.success(f"Success! Found {len(df)} awards in Northern Virginia.")
            
            # Simple Visualization
            fig = px.bar(df.head(15), x='Award Amount', y='Recipient Name', color='Place of Performance County', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df[['Recipient Name', 'Award Amount', 'Place of Performance County', 'Description']])
    else:
        st.error("Could not find geographic data in API response.")
else:
    st.warning("The API returned zero results for the State of Virginia in this timeframe.")
