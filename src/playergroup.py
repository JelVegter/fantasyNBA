from typing import List, Optional
from pprint import pprint
from pandas import DataFrame
from src.schedule import team_games_to_play
from src.teams import TEAMS
from src.league import league
from src.players import FREE_AGENTS, retrieve_player_data


def choose_team() -> Optional[int]:
    """Function to make team selection"""
    for option, team in enumerate(league.teams):
        print(option, team)
    choice = int(input("Choose team: "))
    if choice >= len(league.teams):
        print("Error, invalid choice")
        choose_team()
    return choice


class PlayerGroup:
    """Class containing a group of players"""

    def retrieve_stats(
        self, sort: str = "Score", hide_injured: bool = False
    ) -> DataFrame:
        """Method to retrieve stats for a group of players"""
        stats = retrieve_player_data(self.players).sort_values(by=sort, ascending=False)
        games = team_games_to_play(TEAMS)
        stats_and_games = stats.merge(games, how="left", on="Team")
        stats_and_games["Pot.Week"] = (
            stats_and_games["Score"] * stats_and_games["ThisWeekAmp"]
        )
        stats_and_games["Pot.3Days"] = (
            stats_and_games["Score"] * stats_and_games["Next3DaysAmp"]
        )
        stats_and_games["Pot.NextWeek"] = (
            stats_and_games["Score"] * stats_and_games["NextWeekAmp"]
        )
        if hide_injured:
            stats_and_games = stats_and_games.loc[stats_and_games["Status"] != "OUT"]
        stats_and_games.reset_index(inplace=True, drop=True)
        return stats_and_games


class OtherPlayerGroup(PlayerGroup):
    """Class with a group of players"""

    def __init__(self, team) -> None:
        self.team = team
        self.players = self.team.roster

    def estimate_points(
        self, period: str = "Pot.Week", hide_injured: bool = False
    ) -> float:
        """Method to estimate points in a given period, Pot.Week or Pot.NextWeek"""
        estimated_points = PlayerGroup.retrieve_stats(self)
        if hide_injured:
            estimated_points = estimated_points.loc[estimated_points["Status"] != "OUT"]
        return round(estimated_points[period].sum(), 2)

    def compare_matchup(self, period: str = "Pot.Week") -> None:
        """Method to compare projected points of a team compared to my roster"""
        my_points = self.estimate_points(period=period, hide_injured=True)
        choice = choose_team()
        matchup = OtherPlayerGroup(choice)
        matchup_points = matchup.estimate_points(period=period, hide_injured=True)
        print(f"{self.team} points: {my_points}")
        print(f"{matchup.team} points: {matchup_points}")

    def suggest_trades(self, sort: str = "Score") -> None:
        free_players = FreeAgentPlayerGroup(FREE_AGENTS)
        free_agent_stats = free_players.retrieve_stats(sort=sort, hide_injured=True)
        best_free_agent = free_agent_stats[sort].max()
        roster_stats = PlayerGroup.retrieve_stats(self, sort=sort, hide_injured=False)
        worst_roster_player = roster_stats[sort].min()
        better_free_agents = free_agent_stats.loc[
            free_agent_stats[sort] > worst_roster_player
        ]
        worse_roster_players = roster_stats.loc[roster_stats[sort] < best_free_agent]
        pprint(worse_roster_players.head(10))
        print()
        pprint(better_free_agents.head(15))


class FreeAgentPlayerGroup(PlayerGroup):
    """Class with a group of players, specifically free agents"""

    def __init__(self, players: List) -> None:
        self.players = players

    def show_free_agents(self, sort: str, hide_injured: bool) -> None:
        """Method to print free agents based on certain parameters"""
        pprint(
            PlayerGroup.retrieve_stats(self, sort=sort, hide_injured=hide_injured).head(
                100
            )
        )


def main():
    # Create a schedule to test

    # Test MyPlayerGroup Child Class
    # my_roster = MyPlayerGroup(2)
    # print(my_roster.players)
    # print(my_roster.retrieve_stats())
    # print(my_roster.estimate_points(period='Pot.Week'))
    # my_roster.compare_matchup(period='Pot.Week')
    # my_roster.suggest_trades()

    # Test OtherPlayerGroup Child Class -- choose team before class and init with choice
    # choice = choose_team()
    # other_roster = OtherPlayerGroup(2)
    # print(other_roster.team)
    # print(other_roster.players)
    # print(other_roster.retrieve_stats())
    # other_roster.compare_matchup(period='Pot.Week')
    # other_roster.suggest_trades()

    # Test FreeAgentPlayerGroup Child Class
    free_agents = FreeAgentPlayerGroup(players=FREE_AGENTS)
    free_agents.show_free_agents(sort="Score", hide_injured=False)


if __name__ == "__main__":
    main()
