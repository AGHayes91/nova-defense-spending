import streamlit as st
import requests
import pandas as pd

# Safe Fetch function
def safe_fetch(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=10)
        # 1. Check if the status is OK (200)
        if response.status_code != 200:
            st.error(f"API Error {response.status_code}")
            return None
        
        # 2. Check if the content is actually JSON
        if "application/json" not in response.headers.get("Content-Type", ""):
            st.error("API returned non-JSON data. It might be rate-limiting you.")
            return None
            
        return response.json()
    except Exception as e:
        st.error(f"Request failed: {e}")
        return None

# Example usage for your Trend Data
url = "https://usaspending.gov"
payload = {
    "group": "fiscal_year",
    "filters": {
        "time_period": [{"start_date": "2018-10-01", "end_date": "2026-09-30"}],
        "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
    }
}

data = safe_fetch(url, payload)
if data:
    results = data.get('results', [])
    # ... process results ...
