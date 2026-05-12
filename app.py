import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="National DoD Tracker", layout="wide")
st.title("🛡️ National DoD Award Winners")

# Fiscal Year Selector
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=2)

@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance State Code", "Description"],
        "limit": 100,
        "sort": "Award Amount",
        "order": "desc"
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return pd.DataFrame()
    return pd.DataFrame(response.json().get('results', []))

df = get_dod_data(target_year)

if not df.empty:
    st.success(f"Showcasing top awards for FY{target_year}")

    # 1. TOP WINNERS LEADERBOARD
    st.header("🏆 Top 10 Recipient Leaderboard")
    
    # Group by recipient to handle multiple awards to the same company
    top_winners = df.groupby('Recipient Name')['Award Amount'].sum().sort_values(ascending=False).head(10).reset_index()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Visual Bar Chart of the winners
        fig = px.bar(top_winners, x='Award Amount', y='Recipient Name', 
                     orientation='h', color='Award Amount',
                     title="Total Award Volume by Recipient")
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Text Leaderboard for quick reading
        st.write("### Top 5 Rankings")
        for i, row in top_winners.head(5).iterrows():
            st.metric(label=f"#{i+1}: {row['Recipient Name']}", value=f"${row['Award Amount']:,.0f}")

    # 2. DETAILED DATA LIST
    st.divider()
    st.subheader("All Top Awards Detail")
    st.dataframe(df[['Recipient Name', 'Award Amount', 'Place of Performance State Code', 'Description']])
else:
    st.warning(f"No results found for FY{target_year}. Try switching to 2024 for verified data.")
