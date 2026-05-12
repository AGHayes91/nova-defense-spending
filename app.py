import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="NOVA Defense Tracker", layout="wide", page_icon="🛡️")
st.title("🛡️ DoD Award Impact on Northern Virginia")
st.markdown("Analyzing federal contracts in Arlington, Fairfax, Alexandria, and Loudoun.")

# 2. Sidebar Controls
st.sidebar.header("Settings")
# Allow user to switch years since FY2026 data is currently limited
target_year = st.sidebar.selectbox("Select Fiscal Year", [2026, 2025, 2024], index=1)

# 3. Data Fetching Function
@st.cache_data
def get_dod_data(year):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    # Using UPPERCASE as the API is often case-sensitive for geographic filters
    nova_counties = ["ARLINGTON", "FAIRFAX", "LOUDOUN", "ALEXANDRIA"]
    
    payload = {
        "filters": {
            "time_period": [{"start_date": f"{year-1}-10-01", "end_date": f"{year}-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense (DOD)"}],
            "place_of_performance_locations": [
                {"country": "USA", "state": "VA", "county": c} for c in nova_counties
            ],
            "award_type_codes": ["A", "B", "C", "D"] # Focus on Contracts
        },
        "fields": ["Recipient Name", "Award Amount", "Place of Performance County", "Description"],
        "limit": 100
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        results = response.json().get('results', [])
        return pd.DataFrame(results)
    except Exception as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()

# 4. Process and Display Data
df = get_dod_data(target_year)

if df.empty:
    st.warning(f"No results found for FY{target_year}. Try switching to 2025 in the sidebar.")
else:
    # --- SMART COLUMN MAPPING ---
    # Automatically finds the right column even if the API renames it
    county_col = next((c for c in df.columns if 'county' in c.lower()), None)
    amount_col = next((c for c in df.columns if 'amount' in c.lower()), None)
    recipient_col = next((c for c in df.columns if 'recipient' in c.lower()), "Recipient Name")

    if county_col and amount_col:
        # Dashboard Layout
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader(f"Spending by County (FY{target_year})")
            fig_pie = px.pie(df, values=amount_col, names=county_col, hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("Top Contractors")
            top_df = df.groupby(recipient_col)[amount_col].sum().sort_values(ascending=False).head(10).reset_index()
            fig_bar = px.bar(top_df, x=amount_col, y=recipient_col, orientation='h', color=amount_col)
            st.plotly_chart(fig_bar, use_container_width=True)

        # Detailed Table
        st.divider()
        st.subheader("Raw Award Data")
        st.dataframe(df[[recipient_col, amount_col, county_col, 'Description']].sort_values(by=amount_col, ascending=False))
    else:
        st.error("The API returned data, but column names were unexpected. Check logs.")
        st.write("Found columns:", df.columns.tolist())
