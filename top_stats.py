import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error


def show():
    st.title("Top-run-scorer in All format")
    st.write("Displaying top run-scorers with runs, batting average, strike rate, and other stats.")

    # --- Database Connection ---
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Thrasher@49",  # Change to your MySQL password
            database="cricket"
        )
        if conn.is_connected():
            st.success("✅ Connected to MySQL Database")
    except Error as e:
        st.error(f"❌ Error connecting to MySQL: {e}")
        return

    # --- Fetch Data ---
    query = """
    SELECT 
        rank_no,
        player_name,
        country,
        format,
        matches,
        runs,
        highest_score,
        hundreds,
        fifties,
        fours,
        sixes,
        batting_avg,
        strike_rate
    FROM top_run_scorers_all_format
    ORDER BY rank_no ASC;
    """

    try:
        df = pd.read_sql(query, conn)

        if df.empty:
            st.warning("⚠️ No data found in the database.")
        else:
            # --- Display Table ---
            st.subheader("📊 Top Run Scorers Table")
            st.dataframe(df)

            # --- Bar Chart of Runs ---
            st.subheader("🏏 Runs Scored by Players")
            st.bar_chart(df.set_index("player_name")["runs"])

            # --- Optional Scatter Plot ---
            # import altair as alt
            # st.subheader("Batting Avg vs Strike Rate")
            # chart = alt.Chart(df).mark_circle(size=100).encode(
            #     x='batting_avg',
            #     y='strike_rate',
            #     color='country',
            #     tooltip=['player_name', 'runs', 'matches', 'batting_avg', 'strike_rate']
            # ).interactive()
            # st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to fetch data: {e}")

    finally:
        if conn.is_connected():
            conn.close()
