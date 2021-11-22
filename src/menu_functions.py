from pprint import pprint
from src.schedule import Schedule
from src.league import MY_TEAM
from src.playergroup import (
    MyPlayerGroup,
    OtherPlayerGroup,
    FreeAgentPlayerGroup,
    choose_team,
)
from src.players import FREE_AGENTS, retrieve_free_agents
from src.streaming import find_optimal_solution
from src.teams import TEAMS

SCHEDULE = Schedule(2022)


def press_key_to_continue(test: bool = False) -> None:
    input("Press Enter to continue")


# FREE PLAYER FUNCTIONS
def print_free_players(hide_injured: bool) -> None:
    free_agents = FreeAgentPlayerGroup(players=FREE_AGENTS)
    free_agents.show_free_agents(sort="Score", hide_injured=hide_injured)
    press_key_to_continue()


def print_and_search_free_player() -> None:
    searched_player = input("Player last name: ").lower()
    free_agent_list = retrieve_free_agents()
    searched_player_list = [
        fa for fa in free_agent_list if searched_player in fa.name.lower()
    ]
    if len(searched_player_list) > 0:
        free_agents = FreeAgentPlayerGroup(searched_player_list)
        free_agents.show_free_agents(sort="Score", hide_injured=False)
    else:
        print("No matching player found")
    press_key_to_continue()


def print_and_search_free_player_teams() -> None:
    searched_teams = input("Team abbreviations: ").lower()
    searched_teams = searched_teams.split(",")
    if len(searched_teams) > 1:
        searched_teams = [t.strip().lower() for t in searched_teams]
    teams = [
        team.lower()
        for team in TEAMS
        for searched_team in searched_teams
        if searched_team.lower() in team.lower()
    ]
    free_agent_list = retrieve_free_agents()
    searched_player_in_teams_list = [
        fa for fa in free_agent_list if fa.proTeam.lower() in teams
    ]
    if len(searched_player_in_teams_list) > 0:
        free_agents = FreeAgentPlayerGroup(searched_player_in_teams_list)
        free_agents.show_free_agents(sort="Score", hide_injured=False)
    else:
        print("No matching teams")
    press_key_to_continue()


def print_free_player_suggestions(me: bool) -> None:
    if me is True:
        my_roster = MyPlayerGroup(MY_TEAM)
        my_roster.suggest_trades()
    else:
        choice = choose_team()
        other_roster = OtherPlayerGroup(choice)
        other_roster.suggest_trades()
    press_key_to_continue()


def print_optimal_streaming_flow(max_slots: int, max_trades: int, week: str):
    find_optimal_solution(max_slots=max_slots, max_trades=max_trades, week=week)
    press_key_to_continue()


# ROSTER STAT FUNCTIONS
def print_roster_stats(me: bool) -> None:
    if me is True:
        my_roster = MyPlayerGroup(MY_TEAM)
        pprint(my_roster.retrieve_stats())
    else:
        choice = choose_team()
        other_roster = OtherPlayerGroup(choice)
        pprint(other_roster.retrieve_stats())
    press_key_to_continue()


# MATCHUP COMPARISON FUNCTIONS
def print_matchup_comparison(me: bool) -> None:
    if me is True:
        my_roster = MyPlayerGroup(MY_TEAM)
        my_roster.compare_matchup(period="Pot.Week")
    else:
        choice = choose_team()
        other_roster = OtherPlayerGroup(choice)
        other_roster.compare_matchup(period="Pot.Week")
    press_key_to_continue()


# SCHEDULE FUNCTIONS
def print_team_schedules(week: str) -> None:
    pprint(SCHEDULE.teams_playing_per_day(sort="Total", week=week))
    press_key_to_continue()


# SCHEDULE FUNCTIONS
def refresh_schedule_data() -> None:
    SCHEDULE.refresh_data()
    press_key_to_continue()
