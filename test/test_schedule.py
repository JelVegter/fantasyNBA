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
    assert games.shape[1] == 5


@pytest.mark.parametrize(
    ("x", "y", "value"), [(0, 0, 0), (0, 2, "IND"), (29, 0, "SAS"), (29, 1, 0)]
)
def test_teams_games_per_day(x, y, value):
    SCHEDULE = Schedule(2022)
    games = teams_games_per_day(schedule=SCHEDULE.schedule, week=48)
    assert isinstance(games, DataFrame)
    assert games.shape[0] == 30
    assert games.shape[1] == 10
    assert games.iloc[x, y] == value
