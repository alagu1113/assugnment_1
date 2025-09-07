import streamlit as st

st.set_page_config(page_title="Cricbuzz LiveStats", layout="wide")
st.markdown("CRICKET_STATS")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Live Matches", "Top Stats", "SQL Queries", "CRUD Operations"])

# Page routing
if page == "Live Matches":
    import pages.live_matches as live
    live.show()

elif page == "Top Stats":
    import pages.top_stats as top
    top.show()

elif page == "SQL Queries":
    import pages.sql_queries as sq
    sq.show()

elif page == "CRUD Operations":
    import pages.crud_operations as crud
    crud.show()
