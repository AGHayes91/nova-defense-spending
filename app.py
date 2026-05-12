import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Tracker", layout="wide")
st.title("🛡️ DoD Award Impact on Northern Virginia")

# Select 2024 to guarantee data visibility despite reporting lags
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=2)

@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    # Combined FIPS: VA (51) + County Code (013, 059, 107, 510)
    nova_fips = ["51013", "51059", "51107", "51510"]
    
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [
                {"country": "USA", "state": "VA", "county": fips[-3:]} for fips in nova_fips
            ],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
        "limit": 100
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return pd.DataFrame()
        
    return pd.DataFrame(response.json().get('results', []))

df = get_dod_data(target_year)

if not df.empty:
    st.success(f"Loaded {len(df)} awards for FY{target_year}")
    
    # Find columns dynamically
    county_col = next((c for c in df.columns if 'county' in c.lower()), "Place of Performance County")
    amount_col = next((c for c in df.columns if 'amount' in c.lower()), "Award Amount")
    
    # Visuals
    fig = px.pie(df, values=amount_col, names=county_col, title="Spending by County")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)
else:
    st.warning(f"No results found for FY{target_year}. Switch to 2024 in the sidebar to see verified data.")
