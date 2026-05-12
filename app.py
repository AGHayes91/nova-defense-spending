import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="DOD Spending Tracker", layout="wide")
st.title("🛡️ Department of Defense National Awards")

# 1. Sidebar - Use 2024 because it is a "complete" and verified data year
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=2)

@st.cache_data
def get_verified_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    # Payload stripped to absolute essentials
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "award_type_codes": ["A", "B", "C", "D"],
            # Broadening the agency name filter
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance State Code", "Description"],
        "limit": 100,
        "sort": "Award Amount",
        "order": "desc"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        st.error(f"Error {response.status_code}: {response.text}")
        return pd.DataFrame()
        
    return pd.DataFrame(response.json().get('results', []))

df = get_verified_data(target_year)

if not df.empty:
    st.success(f"Success! Loaded top 100 national awards for FY{target_year}.")
    
    # Quick Visualization
    st.subheader("Major Awards by State")
    state_df = df.groupby('Place of Performance State Code')['Award Amount'].sum().reset_index()
    st.plotly_chart(px.bar(state_df, x='Award Amount', y='Place of Performance State Code', orientation='h'))
    
    st.dataframe(df)
else:
    st.warning(f"No results found for FY{target_year}. Try switching to 2024 in the sidebar.")
