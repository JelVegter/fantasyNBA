"""Module containing functions to retrieve and calculcate player related info"""
from typing import List
from pandas import DataFrame
from espn_api.basketball import Player
from league import league

FREE_AGENTS = league.free_agents(size=100)

def retrieve_free_agents() -> List[Player]:
    """Function to retrieve current free agents"""
    fa_list = list(FREE_AGENTS)
    return fa_list


def calculate_points(points: dict):
    """Function to convert stats into points"""
    point_counter = 0
    point_counter += points['FGM']*2
    point_counter -= points['FGA']
    point_counter += points['FTM']
    point_counter -= points['FTA']
    try:
        point_counter += points['3PTM']
    except:
        pass
    point_counter += points['REB']
    point_counter += points['AST']*2
    point_counter += points['STL']*4
    point_counter += points['BLK']*4
    point_counter -= points['TO']*2
    point_counter += points['PTS']
    return round(point_counter,2)


def convert_score_columns_headers(column_header):
    """Function to convert column names"""
    year = column_header[2:6]
    stat_type_dict = {
        '00':'Fs',
        '10':'Proj',
        '01':'7_d',
        '02':'15_d',
        '03':'30_d',
    }
    stat_type = stat_type_dict[column_header[:2]]
    return ''.join(stat_type+'.'+year)


def calculate_weighted_score(scores: DataFrame) -> float:
    """Function to calculated a weighted score"""
    weights = {
        'Proj.2022.avg': 40,
        'Fs.2022.avg': 30,
        '7_d.2022.avg': 10,
        '15_d.2022.avg': 15,
        '30_d.2022.avg': 25
    }
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


def player_scores(players: List[Player]) -> DataFrame:
    """Function to calculate scores for some players"""
    scores_dict = dict()
    for fa in players:
        stats_dict = fa.stats
        temp_dict = dict()
        for period, scores in stats_dict.items():
            for avg_total, scores_ in scores.items():
                try:
                    stat_type = convert_score_columns_headers(period)
                    temp_dict[stat_type+'.'+avg_total] = calculate_points(scores_)
                except:
                    pass
        scores_dict[fa.name] = temp_dict
        
    scores = DataFrame.from_dict(scores_dict, orient='index')
    scores.reset_index(inplace=True, drop=False)
    scores = scores.rename(columns={'index':'Player'})
    scores['Score'] = scores.apply(lambda x: calculate_weighted_score(x), axis=1)
    columns_to_keep = [
        'Player','Score',
        'Fs.2022.avg','Fs.2022.total',
        'Proj.2022.avg','Proj.2022.total',
        '30_d.2022.avg'
        ]
    return scores[columns_to_keep]


def player_info(players: List[Player]) -> DataFrame:
    """Function to retrieve player info for some players"""
    info_dict = dict()
    for player in players:
        info_dict[player.name] = player.proTeam, player.position, player.injuryStatus, player.injured
    info = DataFrame.from_dict(info_dict, orient='index')
    info.reset_index(inplace=True, drop=False)
    info.columns = ['Player','Team', 'Position', 'Status', 'Injured']
    info = info.drop(columns=['Injured'])
    return info


def retrieve_player_data(players: List[Player]) -> DataFrame:
    """Function to retrieve scores and info of players are combine these"""
    scores = player_scores(players)
    info = player_info(players)
    data = info.merge(scores, how='outer', on='Player')
    return data


def main():
    """Main function for testing"""
    print(retrieve_free_agents())
    players = league.teams[2].roster
    print(retrieve_player_data(players))


if __name__=='__main__':
    main()
