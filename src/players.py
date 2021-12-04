"""Module containing functions to retrieve and calculcate player related info"""
from typing import List
from pandas import DataFrame
from espn_api.basketball import Player
from src.league import league


def refresh_free_agents(size: int):
    global FREE_AGENTS
    FREE_AGENTS = league.free_agents(size=size)
    print("Refreshed: FREE_AGENTS")
    return FREE_AGENTS


FREE_AGENTS = league.free_agents(100)

# def retrieve_free_agents() -> List[Player]:
#     """Function to retrieve current free agents"""
#     fa_list = list(FREE_AGENTS)
#     return fa_list


def calculate_points(points: dict):
    """Function to convert stats into points"""
    point_counter = 0
    point_counter += points["FGM"] * 2
    point_counter -= points["FGA"]
    point_counter += points["FTM"]
    point_counter -= points["FTA"]
    try:
        point_counter += points["3PTM"]
    except:
        pass
    point_counter += points["REB"]
    point_counter += points["AST"] * 2
    point_counter += points["STL"] * 4
    point_counter += points["BLK"] * 4
    point_counter -= points["TO"] * 2
    point_counter += points["PTS"]
    return round(point_counter, 2)


def convert_score_columns_headers(column_header):
    """Function to convert column names"""
    year = column_header[2:6]
    stat_type_dict = {
        "00": "Fs",
        "10": "Proj",
        "01": "7_d",
        "02": "15_d",
        "03": "30_d",
    }
    stat_type = stat_type_dict[column_header[:2]]
    return "".join(stat_type + "." + year)


def calculate_weighted_score(weights: dict, scores: DataFrame) -> float:
    """Function to calculated a weighted score"""
    weight_counter = 0
    score_counter = 0
    for key, value in weights.items():
        if scores[key] > 0:
            score_counter += scores[key] * value
            weight_counter += value
    try:
        return round(score_counter / weight_counter, 2)
    except:
        return 0.00


def score_weights():
    weights = {
        "projected_total_2022.avg": 20,
        "total_2022.avg": 20,
        "last_7_2022.avg": 20,
        "last_15_2022.avg": 15,
        "last_30_2022.avg": 10,
    }
    return weights


def player_scores(players: List[Player], weights: dict) -> DataFrame:
    """Function to calculate scores for some players"""
    scores_dict = {}
    for fa in players:
        stats_dict = fa.stats
        temp_dict = {}
        for period, scores in stats_dict.items():
            for avg_total, scores_ in scores.items():
                try:
                    temp_dict[period] = calculate_points(scores_)
                    temp_dict[period + "." + avg_total] = calculate_points(scores_)
                except:
                    pass
        scores_dict[fa.name] = temp_dict
    scores = DataFrame.from_dict(scores_dict, orient="index")
    scores.reset_index(inplace=True, drop=False)
    scores = scores.rename(columns={"index": "Player"})

    scores["Score"] = scores.apply(
        lambda x: calculate_weighted_score(weights, x), axis=1
    )
    columns_to_keep = [
        "Player",
        "Score",
        "total_2022.avg",
        "total_2022.total",
        "projected_total_2022.avg",
        "projected_total_2022.total",
        "last_30_2022.avg",
    ]
    return scores[columns_to_keep]


def player_info(players: List[Player]) -> DataFrame:
    """Function to retrieve player info for some players"""
    info_dict = dict()
    for player in players:
        info_dict[player.name] = (
            player.proTeam,
            player.position,
            player.injuryStatus,
            player.injured,
        )
    info = DataFrame.from_dict(info_dict, orient="index")
    info.reset_index(inplace=True, drop=False)
    info.columns = ["Player", "Team", "Position", "Status", "Injured"]
    info = info.drop(columns=["Injured"])
    return info


def retrieve_player_data(players: List[Player]) -> DataFrame:
    """Function to retrieve scores and info of players are combine these"""
    weights = score_weights()
    scores = player_scores(players, weights)
    info = player_info(players)
    data = info.merge(scores, how="outer", on="Player")
    return data


def main():
    """Main function for testing"""
    # print(retrieve_free_agents())
    FREE_AGENTS = refresh_free_agents(100)
    players = league.teams[2].roster
    print(retrieve_player_data(players))


if __name__ == "__main__":
    main()
