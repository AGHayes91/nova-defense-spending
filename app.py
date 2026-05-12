import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Tracker", layout="wide")
st.title("🛡️ DoD Award Impact on Northern Virginia")

@st.cache_data
def get_dod_data():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    # Note: Sometimes 'Fairfax' needs to be 'FAIRFAX' or 'Fairfax County'
    nova_counties = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA"]
    
    payload = {
        "filters": {
            "time_period": [{"start_date": "2025-10-01", "end_date": "2026-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [
                {"country": "USA", "state": "VA", "county": c} for c in nova_counties
            ],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
        "limit": 100
    }
    response = requests.post(url, json=payload)
    return pd.DataFrame(response.json().get('results', []))

df = get_dod_data()

# --- DEBUG & MAPPING SECTION ---
if df.empty:
    st.warning("The API returned no results for FY2026 yet. Try changing the year to 2025 to test.")
else:
    # Look for ANY column that might contain county information
    possible_county_cols = [c for c in df.columns if 'county' in c.lower()]
    
    if possible_county_cols:
        target_col = possible_county_cols[0]
        st.sidebar.success(f"Mapping data using: {target_col}")
        
        selected_county = st.sidebar.multiselect(
            "Select Counties", 
            df[target_col].unique(), 
            default=df[target_col].unique()
        )
        filtered_df = df[df[target_col].isin(selected_county)]
        
        # Display Visuals
        st.plotly_chart(px.pie(filtered_df, values='Award Amount', names=target_col))
        st.dataframe(filtered_df)
    else:
        st.error("County column missing. Here are the columns we DID find:")
        st.write(df.columns.tolist())
        st.write("Raw data sample:", df.head())
