import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# App Header
st.set_page_config(page_title="NOVA Defense Spending Tracker", layout="wide")
st.title("🛡️ DoD Award Impact on Northern Virginia CRE")
st.markdown("Analyzing FY2026 defense contracts in Arlington, Fairfax, Alexandria, and Loudoun.")

# 1. Fetch Data from USAspending API
@st.cache_data # Caches data so it doesn't reload on every click
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
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County Name", "Description"],
        "limit": 100
    }
    response = requests.post(url, json=payload)
    return pd.DataFrame(response.json()['results'])

df = get_dod_data()

# 2. Sidebar Filters
st.sidebar.header("Filter Results")
selected_county = st.sidebar.multiselect("Select Counties", df['Place of Performance County Name'].unique(), default=df['Place of Performance County Name'].unique())

filtered_df = df[df['Place of Performance County Name'].isin(selected_county)]

# 3. Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Spending by County")
    fig_city = px.pie(filtered_df, values='Award Amount', names='Place of Performance County Name', hole=0.4)
    st.plotly_chart(fig_city)

with col2:
    st.subheader("Top Contractors")
    top_contractors = filtered_df.groupby('Recipient Name')['Award Amount'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_bar = px.bar(top_contractors, x='Award Amount', y='Recipient Name', orientation='h', color='Award Amount')
    st.plotly_chart(fig_bar)

# 4. Raw Data Display
st.subheader("Detailed Award List")
st.dataframe(filtered_df[['Recipient Name', 'Award Amount', 'Place of Performance County Name', 'Description']])
