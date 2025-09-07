import streamlit as st
from db_connection import execute, read_sql

def add_player(name, role, bat, bowl, Country):
    query = """
        INSERT INTO players (FullName, Role, BattingStyle, BowlingStyle, Country)
        VALUES (%s, %s, %s, %s,%s)
    """
    execute(query, (name, role, bat, bowl, Country))

def update_player(pid, name, role, bat, bowl, Country):
    query = """
        UPDATE players
        SET FullName=%s, Role=%s, BattingStyle=%s, BowlingStyle=%s, Country=%s
        WHERE id=%s
    """
    execute(query, (name, role, bat, bowl, Country, pid))

def show_players():
    df = read_sql("SELECT * FROM players")
    st.dataframe(df)

def show():
    st.title("⚡ CRUD Operations - Players")

    menu = ["Add Player", "View Players", "Update Player", "Delete Player"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Player":
        st.subheader("Add New Player")

        FullName = st.text_input("Full Name")
        Role = st.selectbox("Role", ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper"])
        BattingStyle = st.selectbox("Batting Style", ["Right-hand bat", "Left-hand bat", "N/A"])
        BowlingStyle = st.selectbox("Bowling Style", [
            "Right-arm fast", "Right-arm Medium-Fast", "Right-arm off-spin", 
            "Right-arm leg-spin", "Left-arm fast", "Left-arm Medium-Fast", 
            "Left-arm off-spin", "Left-arm Leg-spin", "N/A", "No_bowling"
        ])
        Country = st.selectbox("Country", ["England", "New zealand", "South Africa", "Afghanistan", "West Indies", "Bangladesh","India", "Australia", "pakistan", "Srilanka"])

        if st.button("Add Player"):
            if FullName:
                add_player(FullName, Role, BattingStyle, BowlingStyle, Country)
                st.success(f"✅ Player '{FullName}' added successfully!")
            else:
                st.error("⚠️ Please enter the Full Name")

    elif choice == "View Players":
        st.subheader("Players List")
        show_players()

    elif choice == "Update Player":
        st.subheader("Update Player (by id)")
        pid = st.number_input("Enter Player id to update", min_value=1, step=1)

        FullName = st.text_input("Full Name (Updated)")
        Role = st.selectbox("Role (Updated)", ["Batsman", "Bowler", "All-Rounder", "Wicket-Keeper"])
        BattingStyle = st.selectbox("Batting Style (Updated)", ["Right-hand bat", "Left-hand bat", "N/A"])
        BowlingStyle = st.selectbox("Bowling` Style (Updated)", [
            "Right-arm fast", "Right-arm Medium-Fast", "Right-arm off-spin", 
            "Right-arm leg-spin", "Left-arm fast", "Left-arm Medium-Fast", 
            "Left-arm off-spin", "Left-arm Leg-spin", "N/A", "No_bowling"
        ])
        Country = st.selectbox("Country", ["England", "New zealand", "South Africa", "Afghanistan", "West Indies", "Bangladesh","India", "Australia", "pakistan", "Srilanka"])

        if st.button("Update Player"):
            if FullName:
                update_player(pid, FullName, Role, BattingStyle, BowlingStyle, Country)
                st.success(f"✅ Player with id {pid} updated successfully!")
            else:
                st.error("⚠️ Please enter the Full Name")

    elif choice == "Delete Player":
        st.subheader("Delete Player (by id)")
        pid = st.number_input("Player id to delete", min_value=1, step=1)
        if st.button("Delete"):
            try:
                execute("DELETE FROM players WHERE id=%s", (pid,))
                st.success(f"✅ Player with id {pid} deleted")
            except Exception as e:
                st.error(str(e))
