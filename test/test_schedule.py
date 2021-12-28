from src.schedule import Schedule, schedule_builder, teams_games_per_day
from pandas import DataFrame
import pytest


def test_Schedule_teams_playing_per_day():
    SCHEDULE = Schedule(2022)
    teams_playing_per_day = SCHEDULE.teams_playing_per_day()
    assert teams_playing_per_day.shape[0] == 30
    assert teams_playing_per_day.shape[1] == 10
    assert teams_playing_per_day["Sun"].sort_values()[-1] != ""


def test_schedule_builder():
    games = schedule_builder(year=2022, months=["october"])
    assert isinstance(games, DataFrame)
    assert games.shape[0] == 93
    assert games.shape[1] == 7


@pytest.mark.parametrize(
    ("x", "y", "value"), [(0, 0, 0), (0, 6, "@CHA"), (29, 6, "TOR"), (29, 1, 0)]
)
def test_teams_games_per_day(x, y, value):
    SCHEDULE = Schedule(2022)
    games = teams_games_per_day(schedule=SCHEDULE.schedule, week=48)
    print(games)
    assert isinstance(games, DataFrame)
    assert games.shape[0] == 30
    assert games.shape[1] == 10
    assert games.iloc[x, y] == value


if __name__ == "__main__":
    # SCHEDULE = Schedule(2022)
    # print(SCHEDULE.schedule)
    year = 2022
    MONTHS = ["october", "november", "december", "january", "february"]
    schedule_builder(year, MONTHS)
