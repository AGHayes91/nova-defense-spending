import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NOVA Defense Tracker", layout="wide")
st.title("🛡️ DoD Award Impact on Northern Virginia")

# Default to 2024 to ensure data is visible immediately
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=2)

@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    
    # Payload for all DoD awards in the State of Virginia
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
        return pd.DataFrame()
        
    return pd.DataFrame(response.json().get('results', []))

df_va = get_dod_data(target_year)

# Define our target NOVA counties (DOD data often uses uppercase)
nova_list = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA CITY"]

if not df_va.empty:
    # Filter the Virginia results for our specific NOVA counties locally
    df = df_va[df_va['Place of Performance County'].str.upper().isin(nova_list)].copy()
    
    if not df.empty:
        st.success(f"Success! Found {len(df)} awards for Northern Virginia in FY{target_year}.")
        
        # Display Visuals
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, values='Award Amount', names='Place of Performance County', title="Spending Distribution")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            top_10 = df.nlargest(10, 'Award Amount')
            fig_bar = px.bar(top_10, x='Award Amount', y='Recipient Name', orientation='h', title="Top 10 Recipients")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.dataframe(df.sort_values('Award Amount', ascending=False))
    else:
        st.warning(f"Found VA data, but no specific matches for NOVA in the top results for {target_year}.")
else:
    st.error(f"No data returned from the API for FY{target_year}. Try 2024.")
