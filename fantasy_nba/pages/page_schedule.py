# ---------------------------------------------#
# ------------  PAGE 2 - Schedule -------------#
# ---------------------------------------------#
import streamlit as st

from fantasy_nba.league import league
from fantasy_nba.schedule import Schedule
from fantasy_nba.tables import table_free_agents, table_roster, table_schedule
from fantasy_nba.teams import FANTASY_TEAMS


def app():
    # Sidebar
    SCHEDULE = Schedule(2022)

    with st.sidebar:
        SELECTED_TEAM_STR = st.sidebar.selectbox(
            label="Select Fantasy Team", options=FANTASY_TEAMS
        )
        a, b = st.columns(2)
        SHOW_PLAYERS = a.number_input(
            "Show Players", format="%i", min_value=10, max_value=50, step=5
        )
        # INJURED_PLAYERS = b.checkbox(label="Injured Players", )
        INJURED_PLAYERS = b.selectbox(label="Injured Players", options=["Hide", "Show"])

        c, d = st.columns(2)
        SEARCHED_PLAYER = c.text_input(label="Search Player")
        SEARCHED_TEAMS = d.text_input(label="Search Teams")

        PERIOD = st.sidebar.selectbox(label="Week", options=["This Week", "Next Week"])
    SELECTED_TEAM = [t for t in league.teams if t.team_name in SELECTED_TEAM_STR][0]

    st.title("Schedule")
    schedule = table_schedule(SCHEDULE, SEARCHED_TEAMS, week=PERIOD)
    st.dataframe(schedule, height=400, width=1050)

    e, f = st.columns(2)
    e.title("Free Agents")
    free_agents = table_free_agents(
        INJURED_PLAYERS, SHOW_PLAYERS, SEARCHED_PLAYER, SEARCHED_TEAMS, small=True
    )
    e.dataframe(free_agents, height=400)

    f.title("Roster Players")
    roster_players = table_roster(SELECTED_TEAM, small=True)
    f.dataframe(roster_players, height=400)
