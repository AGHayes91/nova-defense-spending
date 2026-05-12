import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="National DoD Tracker", layout="wide")
st.title("🇺🇸 Top National DoD Awards")

# Let's use 2024 as the default since it's a "complete" data year
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=2)

@st.cache_data
def get_national_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    # Removed ALL location filters to see if we get a response
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance State Code", "Description"],
        "limit": 100,
        "sort": "Award Amount",
        "order": "desc"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        st.error(f"API Error {response.status_code}: {response.text}")
        return pd.DataFrame()
        
    return pd.DataFrame(response.json().get('results', []))

df = get_national_dod_data(target_year)

if not df.empty:
    st.success(f"Success! Loaded {len(df)} largest national awards for FY{target_year}.")
    
    # Show which states are getting the most of these top 100 awards
    st.subheader("Top Awards by State")
    fig = px.bar(df, x='Award Amount', y='Place of Performance State Code', 
                 color='Place of Performance State Code', orientation='h')
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df)
else:
    st.warning("Still no data. This suggests the Agency Name or Time Period format might be the culprit.")
