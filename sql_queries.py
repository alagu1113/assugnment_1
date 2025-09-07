import streamlit as st
import pandas as pd
import mysql.connector

# --- Database connection ---
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Thrasher@49",   # change if needed
        database="cricket"
    )

# --- Fetch players by country ---
def get_players_by_country(country):
    conn = create_connection()
    df = pd.read_sql("SELECT * FROM players WHERE Country = %s", conn, params=(country,))
    conn.close()
    return df

# --- Fetch latest matches ---
def get_latest_matches(limit=30):
    conn = create_connection()
    query = """
        SELECT status, team1, team2, venue, city, Start_date
        FROM recent_matches
        ORDER BY Start_date DESC
        LIMIT %s
    """
    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    return df

# --- Get countries ---
def get_countries():
    conn = create_connection()
    df = pd.read_sql("SELECT DISTINCT Country FROM players", conn)
    conn.close()
    return df['Country'].tolist()

# --- Fetch top ODI run scorers ---
def get_top_odi_scorers(limit=10):
    conn = create_connection()
    query = """
        SELECT PlayerName AS Player, Runs, BattingAverage AS Avg, Centuries
        FROM topodiscorers
        ORDER BY Runs DESC
        LIMIT %s
    """
    df = pd.read_sql(query, conn, params=(limit,))
    conn.close()
    return df

# --- Fetch countries from stadiums ---
def get_stadium_countries():
    conn = create_connection()
    df = pd.read_sql("SELECT DISTINCT country FROM grounds ORDER BY country", conn)
    conn.close()
    return df['country'].tolist()

# --- Fetch stadiums with filter & sorting ---
def get_stadiums(country=None, sort_order="Highest First"):
    conn = create_connection()
    query = """
        SELECT venue AS venue, city AS city, country AS country, capacity AS capacity
        FROM grounds
        WHERE capacity > 50000
    """
    if country and country != "All":
        query += f" AND country = '{country}'"

    if sort_order == "Highest First":
        query += " ORDER BY capacity DESC"
    else:
        query += " ORDER BY capacity ASC"

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Fetch team wins ---
def get_team_wins():
    conn = create_connection()
    query = """
        SELECT winning_team AS Team, COUNT(*) AS TotalWins
        FROM matches
        WHERE winning_team NOT IN ('No result', 'Match draw')
        GROUP BY winning_team
        ORDER BY TotalWins DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Fetch highest individual scores ---
def get_highest_individual_scores():
    conn = create_connection()
    query = """
        SELECT h.format AS Format, h.player AS Player, h.score AS HighestScore
        FROM highest_individual_scores h
        INNER JOIN (
            SELECT format, MAX(score) AS max_score
            FROM highest_individual_scores
            GROUP BY format
        ) AS sub
        ON h.format = sub.format AND h.score = sub.max_score
        ORDER BY FIELD(h.format, 'Test','ODI','T20I');
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Fetch cricket series in 2024 ---
def get_series_2024():
    conn = create_connection()
    query = """
        SELECT 
            series_name AS series_name,
            host_country AS host_country,
            match_type AS match_type,
            start_date AS start_date,
            total_matches AS total_matches
        FROM series_2024
        WHERE YEAR(start_date) = 2024
        ORDER BY start_date ASC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- Fetch All-Rounders (1000+ runs & 50+ wickets) ---
def get_allrounders():
    conn = create_connection()
    query = """
        SELECT player_name, runs, wickets, formats
        FROM allrounders
        WHERE runs > 1000 AND wickets > 50
        ORDER BY runs DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
# --- Fetch Player Roles Count ---
def get_player_roles():
    conn = create_connection()
    query = """
        SELECT Role AS role, COUNT(*) AS player_count
        FROM players
        GROUP BY Role
        ORDER BY player_count DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
# --- Fetch last 20 completed matches ---
def get_last_20_matches():
    conn = create_connection()
    query = """
        SELECT 
            series_name AS series_name,
            team1 AS team1,
            team2 AS team2,
            winning_team AS winning_team,
            status AS Margin,
            victory_type_desc AS victory_type,
            venue AS venue
        FROM matches
        WHERE winning_team IS NOT NULL
        ORDER BY start_date DESC
        LIMIT 20;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
# --- player comparison ---
def get_player_stats_comparison():
    conn = create_connection()
    query = """
        SELECT 
            player_name,
            SUM(CASE WHEN format='Test' THEN runs ELSE 0 END) AS Test_Runs,
            SUM(CASE WHEN format='ODI' THEN runs ELSE 0 END) AS ODI_Runs,
            SUM(CASE WHEN format='T20I' THEN runs ELSE 0 END) AS T20I_Runs,
            ROUND(AVG(average),2) AS Overall_Avg,
            ROUND(AVG(strike_rate),2) AS Overall_SR
        FROM player_format_stats
        GROUP BY player_name
        HAVING COUNT(DISTINCT format) >= 2
        ORDER BY (Test_Runs + ODI_Runs + T20I_Runs) DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df
# --- Fetch Home vs Away Team Stats with Matches and Losses ---
def get_home_away_stats():
    conn = create_connection()
    query = """
        SELECT 
            team1 AS Team,
            COUNT(*) AS Matches,
            SUM(CASE WHEN team1 = country AND winning_team = team1 THEN 1 ELSE 0 END) AS HomeWins,
            SUM(CASE WHEN team1 <> country AND winning_team = team1 THEN 1 ELSE 0 END) AS AwayWins
        FROM international_matches
        GROUP BY team1
        UNION ALL
        SELECT 
            team2 AS Team,
            COUNT(*) AS Matches,
            SUM(CASE WHEN team2 = country AND winning_team = team2 THEN 1 ELSE 0 END) AS HomeWins,
            SUM(CASE WHEN team2 <> country AND winning_team = team2 THEN 1 ELSE 0 END) AS AwayWins
        FROM international_matches
        GROUP BY team2;
    """
    df = pd.read_sql(query, conn)

    # Aggregate duplicates (team1 and team2 entries)
    df_summary = df.groupby("Team").sum().reset_index()

    # Calculate total wins and losses
    df_summary["TotalWins"] = df_summary["HomeWins"] + df_summary["AwayWins"]
    df_summary["TotalLosses"] = df_summary["Matches"] - df_summary["TotalWins"]
    df_summary["TotalMatches"] = df_summary["Matches"]  # total matches already aggregated

    conn.close()
    return df_summary
#
# --- Fetch player yearly performance (ODI since 2020) ---
def get_player_yearly_stats(min_matches=5):
    conn = create_connection()
    query = """
        SELECT 
            player_name,
            year,
            runs AS total_runs,
            ROUND(runs / matches, 2) AS avg_runs_per_match,
            ROUND(strike_rate, 2) AS avg_strike_rate
        FROM player_odi_yearly_stats
        WHERE year >= 2020
          AND matches >= %s
        ORDER BY player_name, year;
    """
    df = pd.read_sql(query, conn, params=(min_matches,))
    conn.close()
    return df
#
# --- Fetch Toss Advantage Data ---
def get_toss_advantage(team_name):
    conn = create_connection()
    query = f"""
        SELECT
            CASE 
                WHEN toss_winner = batted_first THEN 'Bat First'
                ELSE 'Bowl First'
            END AS toss_decision,
            COUNT(*) AS total_matches,
            SUM(CASE WHEN toss_winner = winning_team THEN 1 ELSE 0 END) AS wins_after_toss
        FROM international_matches
        WHERE toss_winner = '{team_name}'
        GROUP BY toss_decision;
    """
    df = pd.read_sql(query, conn)
    conn.close()
        
    # Calculate win percentage
    if not df.empty:
        df["win_percentage"] = round((df["wins_after_toss"] / df["total_matches"]) * 100, 2)
    return df

# --- Main show function ---
def show():
    st.title("🧩 SQL Queries & Stats Dashboard")

    option = st.sidebar.radio(
        "Select Option",
        [
            "Player Stats",
            "Recent Matches",
            "Top ODI Run Scorers",
            "Large Venues",
            "Team Wins",
            "Highest Individual Scores",	
            "Series 2024",
            "Player Roles", 
            "All-Rounders",
            "Last 20 Matches",
            "Player Format Comparison",
            "Home vs Away Stats",
            "Player Yearly Performance",
            "Toss Advantage",
            "Run SQL Query"
        ]
    )

    # --- Player Stats ---
    if option == "Player Stats":
        countries = get_countries()
        if countries:
            selected_country = st.selectbox("Select a Country", countries)
            if st.button("Show Players"):
                df = get_players_by_country(selected_country)
                if not df.empty:
                    st.dataframe(df)
                else:
                    st.info(f"No players found for {selected_country}")
        else:
            st.warning("No countries found in the database.")

    # --- Recent Matches ---
    elif option == "Recent Matches":
        df_matches = get_latest_matches()
        st.subheader("Latest 30 Matches")
        st.dataframe(df_matches)

        teams = pd.concat([df_matches['team1'], df_matches['team2']]).unique()
        selected_team = st.selectbox("Filter by Team", ["All Teams"] + list(teams))
        if selected_team != "All Teams":
            df_filtered = df_matches[
                (df_matches['team1'] == selected_team) | (df_matches['team2'] == selected_team)
            ]
            st.subheader(f"Matches involving {selected_team}")
            st.dataframe(df_filtered)

    # --- Top ODI Run Scorers ---
    elif option == "Top ODI Run Scorers":
        st.subheader("🏆 Top 10 Highest Run Scorers in ODI Cricket")
        try:
            df_top = get_top_odi_scorers()
            st.dataframe(df_top)
        except Exception as e:
            st.error(f"❌ Failed to fetch top ODI scorers: {e}")

    # --- Large Venues ---
    elif option == "Large Venues":
        st.subheader("🏟️ Cricket Grounds with Capacity > 50,000")
        try:
            sort_order = st.selectbox("Sort by Capacity", ["Highest First", "Lowest First"])
            countries = get_stadium_countries()
            countries.insert(0, "All")
            selected_country = st.selectbox("Select Country", countries)
            df_large = get_stadiums(country=selected_country, sort_order=sort_order)
            if not df_large.empty:
                st.dataframe(df_large, use_container_width=True)
            else:
                st.info("No stadiums found for the selected filters.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")

    # --- Team Wins ---
    elif option == "Team Wins":
        st.subheader("🏏 Cricket Team Wins")
        try:
            df_wins = get_team_wins()
            if not df_wins.empty:
                st.dataframe(df_wins)
                st.bar_chart(df_wins.set_index("Team")["TotalWins"])
            else:
                st.info("No wins data found.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")

    # --- Highest Individual Scores ---
    elif option == "Highest Individual Scores":
        st.subheader("🏏 Highest Individual Batting Scores by Format")
        try:
            df_scores = get_highest_individual_scores()
            if not df_scores.empty:
                st.dataframe(df_scores)
            else:
                st.info("No data found for highest scores.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")

    # --- Series 2024 ---
    elif option == "Series 2024":
        st.subheader("🏆 Cricket Series Starting in 2024")
        try:
            df_series = get_series_2024()
            if not df_series.empty:
                st.dataframe(df_series, use_container_width=True)
            else:
                st.info("No series found for 2024.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")
   # --- All-Rounders ---
    elif option == "All-Rounders":
        st.subheader("🏏 Top All-Rounders (1000+ Runs & 50+ Wickets)")
        try:
            df_allrounders = get_allrounders()
            if not df_allrounders.empty:
                st.dataframe(df_allrounders, use_container_width=True)

                # Runs Chart
                st.subheader("Runs by Player")
                st.bar_chart(df_allrounders.set_index("player_name")["runs"])

                # Wickets Chart
                st.subheader("Wickets by Player")
                st.bar_chart(df_allrounders.set_index("player_name")["wickets"])
            else:
                st.info("No all-rounders found with 1000+ runs and 50+ wickets.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")
    # --- Player Roles ---
    elif option == "Player Roles":
        st.subheader("🏏 Player Count by Playing Role")
        try:
            df_roles = get_player_roles()
            if not df_roles.empty:
                st.dataframe(df_roles, use_container_width=True)

#                # Pie chart
#                st.subheader("Players by Role Pie Chart")
#                fig, ax = plt.subplots()
#                ax.pie(
#                    df_roles["player_count"],
#                    labels=df_roles["role"],
#                    autopct="%1.1f%%",
#                    startangle=90
#                )
#                ax.axis("equal")
#                st.pyplot(fig)
            else:
                st.info("No role data found in the database.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")

# --- Last 20 Matches ---
    elif option == "Last 20 Matches":
        st.subheader("🏏 Last 20 Completed Cricket Matches")
        try:
            df_last20 = get_last_20_matches()
            if not df_last20.empty:
                st.dataframe(df_last20, use_container_width=True)

                # Wins distribution
                st.subheader("Wins Distribution (Last 20 Matches)")
                wins_count = df_last20['winning_team'].value_counts()
                st.bar_chart(wins_count)
            else:
                st.info("No completed matches found in the database.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")
#
    elif option == "Home vs Away Stats":
        st.subheader("🏏 Team Performance: Home vs Away with Matches, Wins, and Losses")
        try:
            df_stats = get_home_away_stats()
            if not df_stats.empty:
                st.dataframe(df_stats, use_container_width=True)

                st.subheader("Home vs Away Wins")
                st.bar_chart(df_stats.set_index("Team")[["HomeWins", "AwayWins"]])

                st.subheader("Total Wins vs Losses")
                st.bar_chart(df_stats.set_index("Team")[["TotalWins", "TotalLosses"]])
            else:
                st.info("No data available for home/away analysis.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")

# --- Player Format Comparison ---
    elif option == "Player Format Comparison":
        st.subheader("🏏 Compare Two Players Across Formats (Runs, Avg, Strike Rate)")
        try:
            df_compare = get_player_stats_comparison()  # <-- Use your existing query function
            if not df_compare.empty:
                players = df_compare["player_name"].tolist()
            
                # Let user pick exactly two players
                selected_players = st.multiselect(
                    "Select two players for comparison", players, default=players[:2]
                )
            
                if len(selected_players) == 2:
                    df_selected = df_compare[df_compare["player_name"].isin(selected_players)]
                    st.dataframe(df_selected, use_container_width=True)

                    # --- Side by Side Charts ---
                    st.subheader("Runs by Format")
                    st.bar_chart(
                        df_selected.set_index("player_name")[["Test_Runs", "ODI_Runs", "T20I_Runs"]]
                    )

                    st.subheader("Overall Batting Average")
                    st.bar_chart(df_selected.set_index("player_name")["Overall_Avg"])

                    st.subheader("Overall Strike Rate")
                    st.bar_chart(df_selected.set_index("player_name")["Overall_SR"])

                elif len(selected_players) < 2:
                    st.info("Please select two players for comparison.")
                else:
                    st.warning("You can only compare two players at a time.")
            else:
                st.info("No players found who played at least 2 formats.")
        except Exception as e:
            st.error(f"MySQL Error: {e}")
#
    elif option == "Player Yearly Performance":
        st.subheader("🏏 Player Yearly Performance (ODI since 2020)")
#

        try:
            min_matches = st.number_input("Minimum matches played in a year", value=5, min_value=1, step=1)
            df_compare = get_player_yearly_stats(min_matches=min_matches)  # same function but we will just use player stats
        
            if df_compare.empty:
                st.warning("No players found meeting the criteria.")
            else:
                player_names = df_compare['player_name'].unique().tolist()
                selected_player = st.selectbox("Select Player", player_names)
            
                if selected_player in player_names:
                    player_df = df_compare[df_compare['player_name'] == selected_player]

                    st.write(f"Performance of **{selected_player}**")
                    st.dataframe(player_df[['year','total_runs','avg_runs_per_match','avg_strike_rate']], use_container_width=True)

                    # --- Runs vs Year ---
                    st.subheader("Total Runs vs Year")
                    st.line_chart(player_df.set_index('year')['total_runs'])

                    # --- Average Runs per Match vs Year ---
                    st.subheader("Average Runs per Match vs Year")
                    st.line_chart(player_df.set_index('year')['avg_runs_per_match'])

                    # --- Strike Rate vs Year ---
                    st.subheader("Strike Rate vs Year")
                    st.line_chart(player_df.set_index('year')['avg_strike_rate'])
                else:
                    st.warning("Player not found. Please enter a valid player name.")

        except Exception as e:
            st.error(f"MySQL Error: {e}")
#
# --- Toss Advantage ---
    elif option == "Toss Advantage":
        st.subheader("🎯 Does Winning the Toss Help Win Matches?")

        try:
            # --- Fetch team list for selector ---
            conn = create_connection()
            team_query = """
                SELECT DISTINCT team1 AS team FROM international_matches
                UNION
                SELECT DISTINCT team2 FROM international_matches
                ORDER BY team;
            """
            teams = pd.read_sql(team_query, conn)["team"].tolist()
            conn.close()

            selected_team = st.selectbox("Select a Team", teams)

            if selected_team:
                toss_df = get_toss_advantage(selected_team)

                if toss_df.empty:
                    st.warning("No data found for this team.")
                else:
                    st.dataframe(toss_df, use_container_width=True)

                    st.bar_chart(
                        toss_df.set_index("toss_decision")["win_percentage"],
                        use_container_width=True
                    )

                    st.write(
                        f"✅ The chart shows how often **{selected_team}** wins matches "
                        "after winning the toss, split by whether they chose to **bat first** or **bowl first**."
                    )

        except Exception as e:
            st.error(f"MySQL Error: {e}")

#
    # --- Keep the rest of your existing options here (Player Stats, Recent Matches, etc.) ---

    # --- Custom SQL Query ---
    elif option == "Run SQL Query":
        st.subheader("Run Custom SQL Query")
        query = st.text_area("Enter your SQL query here:")
        if st.button("Execute Query"):
            if query.strip():
                try:
                    conn = create_connection()
                    df_query = pd.read_sql(query, conn)
                    conn.close()
                    if not df_query.empty:
                        st.dataframe(df_query)
                    else:
                        st.info("Query executed successfully but returned no data.")
                except Exception as e:
                    st.error(f"SQL Query Error: {e}")
