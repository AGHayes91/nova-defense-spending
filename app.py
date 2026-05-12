@st.cache_data
def get_categorical_data(category):
    url = "https://usaspending.gov"
    payload = {
        "category": category, # Options: 'recipient', 'state', 'county'
        "filters": {
            "time_period": [{"start_date": "2018-10-01", "end_date": "2026-09-30"}],
            "agencies": [{"type": "awarding", "tier": "toptier", "name": "Department of Defense"}]
        },
        "limit": 10
    }
    response = requests.post(url, json=payload)
    return pd.DataFrame(response.json().get('results', []))

# UI Tabs for the different views
tab1, tab2, tab3 = st.tabs(["By Company", "By State", "By Region (MSA)"])

with tab1:
    recipients = get_categorical_data('recipient')
    st.plotly_chart(px.bar(recipients, x='amount', y='name', orientation='h', title="Top 10 Recipients (2019-2026)"))

with tab2:
    states = get_categorical_data('state')
    st.plotly_chart(px.choropleth(states, locations='code', locationmode="USA-states", color='amount', scope="usa"))

with tab3:
    counties = get_categorical_data('county') # Use as proxy for local MSA impact
    st.dataframe(counties[['name', 'amount']])
