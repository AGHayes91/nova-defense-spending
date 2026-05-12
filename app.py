import requests
import pandas as pd

def fetch_and_save():
    # URL for USAspending
    url_base = "https://usaspending.gov"
    
    # 1. Capture Historical Trends (2019-2025)
    hist_payload = {
        "group": "fiscal_year",
        "filters": {
            "time_period": [{"start_date": "2018-10-01", "end_date": "2025-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        }
    }
    r_hist = requests.post(url_base + "spending_over_time/", json=hist_payload)
    if r_hist.status_code == 200:
        results = r_hist.json().get('results', [])
        df_hist = pd.DataFrame([{"Year": i['time_period']['fiscal_year'], "Amount": float(i['aggregated_amount'])} for i in results])
        df_hist = df_hist[df_hist['Year'].astype(int) <= 2025].sort_values("Year")
        df_hist.to_csv("defense_trends.csv", index=False)
        print("✅ Saved: defense_trends.csv")

    # 2. Capture Top Winners (FY 2024-2025)
    win_payload = {
        "category": "recipient",
        "filters": {
            "time_period": [{"start_date": "2023-10-01", "end_date": "2025-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "limit": 15
    }
    r_win = requests.post(url_base + "spending_by_category/", json=win_payload)
    if r_win.status_code == 200:
        df_winners = pd.DataFrame(r_win.json().get('results', []))
        df_winners.to_csv("top_winners.csv", index=False)
        print("✅ Saved: top_winners.csv")

if __name__ == "__main__":
    fetch_and_save()
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config
st.set_page_config(page_title="DoD Spending Mockup", layout="wide")
st.title("🛡️ DoD Spending & Impact: 2019 - 2025")
st.markdown("---")

# 2. Load Data (SEVERED FEED - Stable for Thursday Meetings)
try:
    df_hist = pd.read_csv('defense_trends.csv')
    df_winners = pd.read_csv('top_winners.csv')
except FileNotFoundError:
    st.error("⚠️ Data files not found. Ensure .csv files are uploaded to GitHub.")
    st.stop()

# --- SECTION 1: NATIONAL GROWTH TREND ---
st.subheader("📈 National DoD Spending Growth (2019 - 2025)")
# Visualizing the historical obligated growth
fig_trend = px.area(
    df_hist, 
    x="Year", 
    y="Amount", 
    height=350, 
    color_discrete_sequence=['#1f77b4'],
    labels={"Amount": "Obligated Amount ($)"}
)
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# --- SECTION 2: TOP AWARD WINNERS ---
st.subheader("🏆 Top Award Winners (FY 2024 - 2025)")
# Federal award data traditionally features major firms like Lockheed Martin or RTX
fig_winners = px.bar(
    df_winners, 
    x='amount', 
    y='name', 
    orientation='h', 
    color='amount',
    labels={'name': 'Recipient', 'amount': 'Total Award Amount ($)'},
    color_continuous_scale='Blues',
    height=500
)
st.plotly_chart(fig_winners, use_container_width=True)

st.caption("Data source: USAspending.gov. Note: DoD contract data has a mandatory 90-day reporting delay.")
