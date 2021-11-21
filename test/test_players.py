from src.players import (
    retrieve_free_agents,
    player_scores,
    player_info,
    retrieve_player_data,
    calculate_points,
)
import test
from test.mock_objects import MOCK_TEAM, MOCK_PLAYER1, MOCK_PLAYER2
import pytest


def test_retrieve_free_agents_retrieve_data() -> None:
    assert len(retrieve_free_agents()) > 0


@pytest.mark.parametrize(
    ("col", "value"),
    [
        ("Score", 80.06),
        ("total_2022.avg", 76.78999999999999),
        ("total_2022.total", 620.0),
        ("projected_total_2022.avg", 93.5),
        ("projected_total_2022.total", 7147.0),
        ("last_30_2022.avg", 76.78999999999999),
    ],
)
def test_retrieve_player_scores(col, value) -> None:
    weights = {
        "projected_total_2022.avg": 20,
        "total_2022.avg": 20,
        "last_7_2022.avg": 20,
        "last_15_2022.avg": 15,
        "last_30_2022.avg": 10,
    }
    data = player_scores(MOCK_TEAM, weights)
    assert data.shape[0] == len(MOCK_TEAM)
    assert data[col].sum() == value


@pytest.mark.parametrize(
    ("col", "type", "value"),
    [
        ("total_2022", "avg", 41.22),
        ("projected_total_2022", "total", 3958.0),
        ("last_7_2022", "total", 129.0),
        ("last_15_2022", "avg", 40.38),
        ("last_30_2022", "avg", 41.22),
    ],
)
def test_calculate_points(col, type, value) -> None:
    assert calculate_points(MOCK_PLAYER1.stats[col][type]) == value


# def test_retrieve_player_info() -> None:
#     data = player_info(MOCK_TEAM)
#     assert data.shape[0] == len(MOCK_TEAM)
#     assert data.shape[1] == 4
#     assert data.loc[0, "Team"] == "BKN"
#     assert data.loc[0, "Position"] == "PG"
#     assert data.loc[0, "Status"] == "ACTIVE"
#     assert data.loc[1, "Team"] == "TOR"
#     assert data.loc[1, "Position"] == "SG"
#     assert data.loc[1, "Status"] == "ACTIVE"
#
#
# def test_retrieve_player_data() -> None:
#     data = retrieve_player_data(MOCK_TEAM)
#     print(data)
#     assert data["Score"].sum() == 82.07
#     assert data["Fs.2022.avg"].sum() == 76.78999999999999
#     assert data["Fs.2022.total"].sum() == 620.0
#     assert data["Proj.2022.avg"].sum() == 93.5
#     assert data["Proj.2022.total"].sum() == 7147.0
#     assert data["30_d.2022.avg"].sum() == 76.78999999999999
#     assert data.loc[0, "Team"] == "BKN"
#     assert data.loc[0, "Position"] == "PG"
#     assert data.loc[0, "Status"] == "ACTIVE"
#     assert data.loc[1, "Team"] == "TOR"
#     assert data.loc[1, "Position"] == "SG"
#     assert data.loc[1, "Status"] == "ACTIVE"