import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Tracker", layout="wide")
st.title("🛡️ DoD Award Impact on Northern Virginia")

# 1. Sidebar - Use 2024 as the reliable test year
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=2)

@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    # We pull all VA records to ensure we don't miss anything due to strict county formatting
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [{"country": "USA", "state": "VA"}],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
        "limit": 1000 
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        st.error(f"API Error: {response.status_code}")
        return pd.DataFrame()
        
    return pd.DataFrame(response.json().get('results', []))

df_va = get_dod_data(target_year)

# 2. Local filter for our specific NOVA target areas
# Using uppercase because the API standardized results this way
nova_list = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]

if not df_va.empty:
    # Safely find the county column
    county_col = next((c for c in df_va.columns if 'county' in c.lower()), "Place of Performance County")
    
    # Filter the Virginia results for our specific NOVA counties
    df_va[county_col] = df_va[county_col].fillna("UNKNOWN").str.upper()
    df = df_va[df_va[county_col].isin(nova_list)].copy()
    
    if not df.empty:
        st.success(f"Found {len(df)} awards for Northern Virginia in FY{target_year}.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.pie(df, values='Award Amount', names=county_col, title="Spending by County"))
        with col2:
            st.plotly_chart(px.bar(df.nlargest(10, 'Award Amount'), x='Award Amount', y='Recipient Name', orientation='h', title="Top Recipients"))
            
        st.dataframe(df.sort_values('Award Amount', ascending=False))
    else:
        st.warning(f"No NOVA matches in top results. Try increasing the search limit or checking 2024.")
else:
    st.error("The API returned no data for Virginia in this timeframe.")
