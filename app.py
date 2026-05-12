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
