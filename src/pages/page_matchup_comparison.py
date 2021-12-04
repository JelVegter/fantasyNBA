# ---------------------------------------------#
# ------------  PAGE 3 - Matchups -------------#
# ---------------------------------------------#
import streamlit as st
from src.league import league
from src.playergroup import OtherPlayerGroup
from src.teams import FANTASY_TEAMS
from src.tables import table_roster


def app():
    # Side bar
    with st.sidebar:
        SELECTED_TEAM_STR_1 = st.sidebar.selectbox(
            label="Fantasy Team 1", options=FANTASY_TEAMS
        )
        SELECTED_TEAM_STR_2 = st.sidebar.selectbox(
            label="Fantasy Team 2", options=FANTASY_TEAMS
        )

        a, b = st.columns(2)
        PERIOD = a.selectbox(label="Week", options=["This Week", "Next Week"])
        INJURED_PLAYERS = b.selectbox(label="Injured Players", options=["Hide", "Show"])

    if PERIOD == "This Week":
        PERIOD = "Pot.Week"
    else:
        PERIOD = "Pot.NextWeek"

    INJURED_PLAYERS = bool(INJURED_PLAYERS == "hide")

    SELECTED_TEAM_1 = [t for t in league.teams if t.team_name in SELECTED_TEAM_STR_1][0]
    SELECTED_TEAM_2 = [t for t in league.teams if t.team_name in SELECTED_TEAM_STR_2][0]

    c, d = st.columns(2)
    c.title(f"{SELECTED_TEAM_1.team_name}")
    roster_players = table_roster(
        SELECTED_TEAM_1, small=True, hide_injured=INJURED_PLAYERS
    )
    c.dataframe(roster_players, height=400, width=1050)

    other_roster = OtherPlayerGroup(team=SELECTED_TEAM_1)
    matchup_points = other_roster.estimate_points(
        period=PERIOD, hide_injured=INJURED_PLAYERS
    )
    c.write(f"Project Points for {SELECTED_TEAM_STR_1}: {matchup_points}")

    d.title(f"{SELECTED_TEAM_2.team_name}")
    roster_players = table_roster(
        SELECTED_TEAM_2, small=True, hide_injured=INJURED_PLAYERS
    )
    d.dataframe(roster_players, height=400, width=1050)

    other_roster = OtherPlayerGroup(team=SELECTED_TEAM_2)
    matchup_points = other_roster.estimate_points(
        period=PERIOD, hide_injured=INJURED_PLAYERS
    )
    d.write(f"Project Points for {SELECTED_TEAM_STR_2}: {matchup_points}")
