from typing import List
import psycopg2
from pandas import DataFrame, read_sql, concat


def extract_player_stats():
    query = """
    SELECT * FROM PlayerStats
    """
    with psycopg2.connect(database="nba", user="user", password="pass") as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        data = read_sql(query, conn, index_col="id")
    return data


def calc_expanding(stats: DataFrame) -> DataFrame:
    stats = stats.sort_index()
    expanding_mean = (
        stats[["player", "date", "points"]].groupby(["player"]).expanding().mean()
    )
    expanding_mean = expanding_mean.reset_index()
    expanding_mean = expanding_mean[["id", "points"]].set_index("id")
    expanding_mean = expanding_mean.rename(columns={"points": "average_points"})
    stats = stats.merge(expanding_mean, how="left", left_index=True, right_index=True)
    return stats


def calc_rolling(
    stats: DataFrame, windows: List[int], forward: bool = False
) -> DataFrame:
    stats = stats.sort_index()
    for window in windows:
        dir = "Bckw"
        if forward is True:
            stats = stats.sort_index(ascending=False)
            dir = "Fwrd"
        rolling_period = f"Roll{dir}{window}"

        if forward is True:
            rolling = DataFrame()
            for p in stats["player"].unique():
                temp_stats = stats.loc[stats["player"] == p]
                temp_stats = (
                    temp_stats[["player", "date", "points"]]
                    .shift(1)
                    .rolling(window, min_periods=window)
                    .mean()
                )
                rolling = concat([rolling, temp_stats])
        else:
            rolling = (
                stats[["player", "date", "points"]]
                .groupby(["player"])
                .rolling(window, min_periods=window)
                .mean()
            )
            rolling = rolling.reset_index().set_index("id")
        rolling = rolling["points"]
        rolling = rolling.rename(rolling_period)
        stats = concat([stats, rolling], axis=1)
    stats = stats.sort_index()
    return stats


def transform_player_stats(
    data: DataFrame, roll_backwards: List[int], roll_forward: List[int]
) -> DataFrame:
    stats = calc_expanding(data)
    stats = calc_rolling(stats, roll_backwards)
    stats = calc_rolling(stats, roll_forward, forward=True)
    stats = stats[
        [
            "player",
            "date",
            "points",
            "average_points",
            "RollBckw2",
            "RollBckw4",
            "RollBckw6",
            "RollFwrd1",
            "RollFwrd2",
        ]
    ]
    print(stats.loc[stats["player"] == "Joe Harris"])
    return stats


if __name__ == "__main__":
    data = extract_player_stats()
    data = transform_player_stats(data, roll_forward=[1, 2], roll_backwards=[2, 4, 6])
    print(data.loc[data["player"] == "Joe Harris"])
