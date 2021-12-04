import psycopg2
from pandas import DataFrame
from numpy import nan
from src.full_player_stats import (
    get_all_stats,
    clean_all_stats,
    calculate_stat_points,
)

MONTHS = [
    "october",
    "november",
    "december",
    "january",
    "february",
    "march",
    "april",
]

param_dic = {
    "host": "localhost",
    "database": "nba",
    "user": "user",
    "password": "pass",
}
TABLE_COLS = [
    "Id",
    "Player",
    "Team",
    "Opponent",
    "GameDay",
    "Points",
    "MP",
    "FGM",
    "FGA",
    "FG%",
    "3PTM",
    "3PA",
    "3P%",
    "FTM",
    "FTA",
    "FT%",
    "ORB",
    "DRB",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TO",
    "PF",
    "PTS",
    "+/-",
]


def extract_player_stats():
    all_stats = get_all_stats(MONTHS)
    cleaned_stats = clean_all_stats(all_stats)
    # cleaned_stats = get_dataframe(refresh=False)
    cleaned_stats["Points"] = cleaned_stats.apply(calculate_stat_points, axis=1)
    cleaned_stats.index.name = "Id"
    cleaned_stats.reset_index(inplace=True, drop=False)
    cleaned_stats = cleaned_stats[TABLE_COLS]
    return cleaned_stats


def convert_time_string(minutes: str):
    try:
        split = minutes.split(":")
        minutes = int(split[0])
        seconds = int(split[1])
        minutes_played = minutes + seconds / 60
        return minutes_played
    except:
        return nan


def transform_player_stats(data: DataFrame) -> DataFrame:
    data["MP"] = data["MP"].map(convert_time_string)
    data = data.astype(object)
    return data


def load_player_stats(data: DataFrame) -> None:
    data = data.to_records(index=False)
    records = []
    for tup in data:
        records.append(
            tuple(None if element != element else element for element in tup)
        )
    print(f"Inserting {len(records)} into PlayerStats")
    truncate = """
    TRUNCATE PlayerStats;
    """
    query = """
    INSERT INTO PlayerStats
    (Id, Player, Team, Opponent, Date, Points, MP, FGM, FGA, FGperc, threePTM, threePA, \
    threePperc, FTM, FTA, FTperc, ORB, DRB, REB, AST, STL, BLK, TurnOver, PF, PTS, plus_minus)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    with psycopg2.connect(database="nba", user="user", password="pass") as conn:
        cursor = conn.cursor()
        cursor.execute(truncate)
        conn.commit()

        cursor.executemany(query, records)
        conn.commit()


if __name__ == "__main__":
    data = extract_player_stats()
    data = transform_player_stats(data)
    load_player_stats(data)
