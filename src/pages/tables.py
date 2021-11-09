import streamlit as st
from typing import List
from league import league
from playergroup import MyPlayerGroup, OtherPlayerGroup, FreeAgentPlayerGroup, choose_team
from players import FREE_AGENTS, retrieve_free_agents
from streaming import find_optimal_solution
from teams import TEAMS
from schedule import SCHEDULE, Schedule


# @st.cache
def build_free_agents():
    return FreeAgentPlayerGroup(players=FREE_AGENTS)
free_agents = build_free_agents()


def hover(hover_color="#013220"):
        return dict(selector="tr:hover",
                    props=[("background-color", "%s" % hover_color)])
styles = [
    hover(),
    dict(selector="th", props=[("font-size", "150%"),
                            ("text-align", "center")]),
    dict(selector="caption", props=[("caption-side", "bottom")])
]

def highlight_X(value):
    if value == "X":
        color = "#013220"
    else:
        color = "Black"
    return "background-color: %s" % color



def table_free_agents(INJURED_PLAYERS: str, SHOW_PLAYERS: int, SEARCHED_PLAYER, SEARCHED_TEAMS: str, small: bool=False):
    free_agent_list = free_agents.players
    player_stats = free_agents.retrieve_stats(hide_injured=INJURED_PLAYERS)
    

    searched_player_list = [fa.name for fa in free_agent_list if SEARCHED_PLAYER in fa.name.lower()]
    if len(SEARCHED_PLAYER) > 0:
        player_stats = player_stats.loc[player_stats['Player'].isin(searched_player_list)]

    searched_teams = SEARCHED_TEAMS.split(',')
    searched_teams = list(map(lambda x: x.lower(), searched_teams))
    if len(searched_teams) > 0:
        searched_teams = [t.strip().lower() for t in searched_teams]
    teams = [team.lower() for team in TEAMS for searched_team in searched_teams if searched_team.lower() in team.lower()]
    searched_player_in_teams_list = [fa.name for fa in free_agent_list if fa.proTeam.lower() in teams]
    if len(searched_player_in_teams_list) > 0:
        player_stats = player_stats.loc[player_stats['Player'].isin(searched_player_in_teams_list)]

    if small is True:
        player_stats = player_stats[["Player","Team", "Status", "Score", "Today", "Next3Days", "Pot.Week", "Pot.NextWeek"]]

    
    player_stats = player_stats.head(SHOW_PLAYERS)
    

    player_stats =(
        player_stats.style
        .format(
        {"Score":"{:.1f}",
        "Fs.2022.avg":"{:.1f}",
        "Fs.2022.total":"{:.1f}",
        "Proj.2022.avg":"{:.1f}",
        "Proj.2022.total":"{:.1f}",
        "30_d.2022.avg":"{:.1f}",
        "Pot.Week":"{:.1f}",
        "Pot.NextWeek":"{:.1f}"})
        .bar(subset=['Score',"Pot.Week","Pot.NextWeek"], color='#013220')
        .hide_index()
        .set_table_styles(styles)
        .set_caption("Hover to highlight.")
    )
    return player_stats




def table_roster(SELECTED_TEAM: OtherPlayerGroup, small: bool=False, hide_injured: bool=True):
    other_roster = OtherPlayerGroup(team=SELECTED_TEAM)
    roster_stats = other_roster.retrieve_stats(hide_injured=hide_injured)

    if small is True:
        roster_stats = roster_stats[["Player","Team", "Status", "Score", "Today", "Next3Days", "Pot.Week", "Pot.NextWeek"]]

    roster_stats =(
        roster_stats.style
        .format(
        {"Score":"{:.1f}",
        "Fs.2022.avg":"{:.1f}",
        "Fs.2022.total":"{:.1f}",
        "Proj.2022.avg":"{:.1f}",
        "Proj.2022.total":"{:.1f}",
        "30_d.2022.avg":"{:.1f}",
        "Pot.Week":"{:.1f}",
        "Pot.NextWeek":"{:.1f}"})
        .bar(subset=['Score',"Pot.Week","Pot.NextWeek"], color='#013220')
        .hide_index()
        .set_table_styles(styles)
        .set_caption("Hover to highlight.")
    )
    return roster_stats




def table_schedule(SCHEDULE: Schedule, SEARCHED_TEAMS: str, week: str):
    schedule = SCHEDULE.teams_playing_per_day(sort="Total", week=week)
    schedule.reset_index(inplace=True, drop=False)
    schedule = schedule.rename(columns={'index':'Team'})
    weekdays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    searched_teams = SEARCHED_TEAMS.split(',')
    searched_teams = list(map(lambda x: x.lower(), searched_teams))
    if len(searched_teams) > 0:
        searched_teams = [t.strip().lower() for t in searched_teams]
    searched_teams = [team.upper() for team in TEAMS for searched_team in searched_teams if searched_team.upper() in team.upper()]
    if len(searched_teams) > 0:
        schedule = schedule[schedule["Team"].isin(searched_teams)]


    schedule =(
        schedule.style
        .hide_index()
        .set_table_styles(styles)
        .set_caption("Hover to highlight.")
        .applymap(highlight_X)
    )
    return schedule