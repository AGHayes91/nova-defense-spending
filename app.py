@st.cache_data
def get_historical_trends():
    url = "https://usaspending.gov"
    payload = {
        "group": "fiscal_year",
        "filters": {
            "time_period": [{"start_date": "2018-10-01", "end_date": "2026-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        }
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        # 1. Check if the status code is 200 (Success)
        r.raise_for_status() 
        
        # 2. Safely parse JSON
        json_data = r.json()
        results = json_data.get('results', [])
        
        if not results:
            st.warning("The API returned a successful but empty response.")
            return pd.DataFrame()

        data = [{"Year": i['time_period']['fiscal_year'], "Amount": float(i['aggregated_amount'])} for i in results]
        return pd.DataFrame(data).sort_values("Year")
        
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP Error: {err}")
    except requests.exceptions.JSONDecodeError:
        st.error("Received an invalid response from the API. It may be down or experiencing high traffic.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
    
    return pd.DataFrame()
