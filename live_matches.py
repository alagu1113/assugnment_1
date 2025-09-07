import streamlit as st
import requests
import pandas as pd
import base64

def show():
    st.title("🏏 Live Matches")
    st.write("Live matches will be shown here...")

    # --- Cricbuzz API request ---
    url = "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live"
    headers = {
        "x-rapidapi-key": "3da7add0b5mshdb5fac3a4f08ba4p16d1c6jsn1ab2180e5be5",
        "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        matches_list = []
        for match_type in data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                series_info = series.get("seriesAdWrapper", {})
                series_name = series_info.get("seriesName")

                for match in series_info.get("matches", []):
                    match_info = match.get("matchInfo", {})

                    if match_info.get("stateTitle") == "In Progress":
                        venue_info = match_info.get("venueInfo", {})
                        match_score = match.get("matchScore", {})

                        # Get team1 score
                        team1_score_data = match_score.get("team1Score", {}).get("inngs1", {})
                        team1_score = f"{team1_score_data.get('runs', 0)}/{team1_score_data.get('wickets', 0)} ({team1_score_data.get('overs', 0)} ov)"

                        # Get team2 score
                        team2_score_data = match_score.get("team2Score", {}).get("inngs1", {})
                        if team2_score_data:
                            team2_score = f"{team2_score_data.get('runs', 0)}/{team2_score_data.get('wickets', 0)} ({team2_score_data.get('overs', 0)} ov)"
                        else:
                            team2_score = "-"

                        matches_list.append({
                            "Team1": match_info.get("team1", {}).get("teamName"),
                            "Team1 Score": team1_score,
                            "Team2": match_info.get("team2", {}).get("teamName"),
                            "Team2 Score": team2_score,
                            "Series Name": series_name,
                            "Match": match_info.get("matchDesc"),
                            "Match Format": match_info.get("matchFormat"),
                            "State": match_info.get("stateTitle"),
                            "Status": match_info.get("status"),
                            "Venue": venue_info.get("ground"),
                            "City": venue_info.get("city")
                        })

        if matches_list:
            df = pd.DataFrame(matches_list)
            st.dataframe(df)
        else:
            st.info("ℹ️ No matches currently in progress.")

    except Exception as e:
        st.error(f"❌ Failed to fetch live data: {e}")
