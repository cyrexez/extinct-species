import streamlit as st

st.set_page_config(page_title="Species Discovery", layout="wide")

# Map codes to full names for the UI
CAT_MAP = {
    "EX": "Extinct", "EW": "Extinct in the Wild", "CR": "Critically Endangered",
    "EN": "Endangered", "VU": "Vulnerable", "NT": "Near Threatened", 
    "LC": "Least Concern", "DD": "Data Deficient", "NE": "Not Evaluated"
}

# Define Navigation
pg = st.navigation([
    st.Page("pages/search.py", title="Search", icon="🔍"),
    st.Page("pages/detail.py", title="Discovery", icon="🌍")
])

pg.run()