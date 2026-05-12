import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ... (Previous header code)

@st.cache_data
def get_dod_data():
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    nova_counties = ["Arlington", "Fairfax", "Loudoun", "Alexandria"]
    
    payload = {
        "filters": {
            "time_period": [{"start_date": "2025-10-01", "end_date": "2026-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [
                {"country": "USA", "state": "VA", "county": c} for c in nova_counties
            ],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        # Use more specific field names standard to the API
        "fields": ["Recipient Name", "Award Amount", "primary_place_of_performance_county_name", "Description"],
        "limit": 100
    }
    response = requests.post(url, json=payload)
    data = response.json().get('results', [])
    return pd.DataFrame(data)

df = get_dod_data()

# SAFETY CHECK: If the column is missing, use a fallback
county_col = 'primary_place_of_performance_county_name'
if county_col not in df.columns:
    # If the API returned a different name, try to find it or use a placeholder
    potential_cols = [col for col in df.columns if 'county' in col.lower()]
    county_col = potential_cols[0] if potential_cols else None

if county_col:
    st.sidebar.header("Filter Results")
    selected_county = st.sidebar.multiselect("Select Counties", df[county_col].unique(), default=df[county_col].unique())
    filtered_df = df[df[county_col].isin(selected_county)]
else:
    st.error("Could not find county data in the API response.")
    filtered_df = df
