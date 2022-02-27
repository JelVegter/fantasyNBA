from test.mock_objects import MOCK_PLAYER1, MOCK_PLAYER2, MOCK_TEAM

import pytest

from fantasy_nba.players import calculate_points, player_info, player_scores, retrieve_player_data


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
def test_calculate_points_player1(col, type, value) -> None:
    assert calculate_points(MOCK_PLAYER1.stats[col][type]) == value


@pytest.mark.parametrize(
    ("col", "type", "value"),
    [
        ("total_2022", "avg", 35.57),
        ("projected_total_2022", "total", 3189.0),
        ("last_7_2022", "total", 63.0),
        ("last_15_2022", "avg", 35.67),
        ("last_30_2022", "total", 249.0),
    ],
)
def test_calculate_points_player2(col, type, value) -> None:
    assert calculate_points(MOCK_PLAYER2.stats[col][type]) == value


@pytest.mark.parametrize(
    ("index", "col", "value"),
    [
        (0, "Team", "BKN"),
        (0, "Position", "PG"),
        (0, "Status", "ACTIVE"),
        (1, "Team", "TOR"),
        (1, "Position", "SG"),
        (1, "Status", "ACTIVE"),
    ],
)
def test_retrieve_player_info(index, col, value) -> None:
    data = player_info(MOCK_TEAM)
    assert data.shape[0] == len(MOCK_TEAM)
    assert data.shape[1] == 4
    assert data.loc[index, col] == value


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
def test_retrieve_player_data_values(col, value) -> None:
    data = retrieve_player_data(MOCK_TEAM)
    assert data[col].sum() == value


@pytest.mark.parametrize(
    ("index", "col", "value"),
    [
        (0, "Team", "BKN"),
        (0, "Position", "PG"),
        (0, "Status", "ACTIVE"),
        (1, "Team", "TOR"),
        (1, "Position", "SG"),
        (1, "Status", "ACTIVE"),
    ],
)
def test_retrieve_player_data_info(index, col, value) -> None:
    data = retrieve_player_data(MOCK_TEAM)
    assert data.loc[index, col] == value


### TODO check denver not found
