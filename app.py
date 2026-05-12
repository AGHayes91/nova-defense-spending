import time

def safe_fetch(url, payload):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=15)
            
            # Handle Rate Limiting (429)
            if response.status_code == 429:
                wait_time = (2 ** attempt) * 5 # Exponential backoff
                st.warning(f"Rate limited. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            # Verify successful response and JSON content
            if response.status_code == 200 and "application/json" in response.headers.get("Content-Type", ""):
                return response.json()
            else:
                st.error(f"API Error {response.status_code}: Received non-JSON response.")
                return None
                
        except Exception as e:
            st.error(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return None
