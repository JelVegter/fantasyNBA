# ---------------------------------------------#
# ----------  PAGE 1 - FREE AGENTS - ----------#
# ---------------------------------------------#
import streamlit as st

from fantasy_nba.league import league
from fantasy_nba.tables import table_free_agents, table_roster
from fantasy_nba.teams import FANTASY_TEAMS


def app():
    # Side bar
    with st.sidebar:
        SELECTED_TEAM_STR = st.sidebar.selectbox(
            label="Select Fantasy Team", options=FANTASY_TEAMS
        )
        a, b = st.columns(2)
        SHOW_PLAYERS = a.number_input(
            "Show Players", format="%i", min_value=10, max_value=50, step=5
        )
        INJURED_PLAYERS = b.selectbox(label="Injured Players", options=["Hide", "Show"])

        c, d = st.columns(2)
        SEARCHED_PLAYER = c.text_input(label="Search Player")
        SEARCHED_TEAMS = d.text_input(label="Search Teams")

    INJURED_PLAYERS = bool(INJURED_PLAYERS == "Hide")
    SELECTED_TEAM = [t for t in league.teams if t.team_name in SELECTED_TEAM_STR][0]

    st.title("Free Agents")
    free_agents = table_free_agents(INJURED_PLAYERS, SHOW_PLAYERS, SEARCHED_PLAYER, SEARCHED_TEAMS)
    st.dataframe(free_agents, height=400, width=1050)

    st.title("Roster Players")
    roster_players = table_roster(SELECTED_TEAM, hide_injured=INJURED_PLAYERS)
    st.dataframe(roster_players, height=400, width=1050)
