from datetime import datetime
from typing import List
from dateutil import parser
import pandas as pd
from numpy import nan


basketball_reference_abbreviations = {
    "Atlanta Hawks": "ATL",
    "Boston Celtics": "BOS",
    "Brooklyn Nets": "BRK",
    "Charlotte Hornets": "CHO",
    "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL",
    "Denver Nuggets": "DEN",
    "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW",
    "Houston Rockets": "HOU",
    "Indiana Pacers": "IND",
    "Los Angeles Lakers": "LAL",
    "Los Angeles Clippers": "LAC",
    "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA",
    "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP",
    "New York Knicks": "NYK",
    "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI",
    "Phoenix Suns": "PHO",
    "Portland Trail Blazers": "POR",
    "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR",
    "Utah Jazz": "UTA",
    "Washington Wizards": "WAS",
}
MONTHS = ["october", "november", "december"]
# MONTHS = ["november"]


def find_abbreviation(team: str) -> str:
    return basketball_reference_abbreviations[team]


def convert_date(date, hyphens: bool = False):
    date = parser.parse(date)
    if hyphens is False:
        return datetime.strftime(date, "%Y%m%d")
    return datetime.strftime(date, "%Y-%m-%d")


def gen_url(row) -> str:
    """Function to find url for stats per game"""
    team = row["AbbrHomeTeam"]
    date = parser.parse(row["Date"])
    date = datetime.strftime(date, "%Y%m%d")
    url = f"https://www.basketball-reference.com/boxscores/{date}0{team}.html"
    return url


def scrape_stats(played_games: pd.DataFrame) -> pd.DataFrame:
    all_stats = pd.DataFrame()
    for index, row in played_games.iterrows():
        try:
            url = row["url"]
            away_team = pd.read_html(url)[0]
            minutes_played = int(away_team[("Basic Box Score Stats", "MP")].iloc[-1])

            # Overtime changes the index of score table
            overtime = (minutes_played - 240) / 25
            table_html_index = int(8 + overtime)
            home_team = pd.read_html(url)[table_html_index]
            away_team["GameDay"] = row["Date"]
            home_team["GameDay"] = row["Date"]
            all_stats = pd.concat([all_stats, home_team])
            all_stats = pd.concat([all_stats, away_team])
            print(f"Added data from: {url}")
        except:
            print(f"Failed to retrieve data: {url}")
    return all_stats


def get_all_stats(months: List[str]) -> pd.DataFrame:
    all_stats = pd.DataFrame()
    for month in months:
        try:
            played_games = pd.read_html(
                f"https://www.basketball-reference.com/leagues/NBA_2022_games-{month}.html"
            )[0]
            played_games = played_games.loc[played_games["Attend."] > 0]
            played_games["AbbrHomeTeam"] = played_games["Home/Neutral"].map(
                find_abbreviation
            )
            played_games["DateStr"] = played_games["Date"].map(convert_date)
            played_games["url"] = played_games.apply(gen_url, axis=1)
            monthly_stats = scrape_stats(played_games)
            all_stats = pd.concat([all_stats, monthly_stats])
        except:
            print(f"Failed to retrieve data for {month}")
    return all_stats


def clean_all_stats(all_stats: pd.DataFrame) -> pd.DataFrame:
    """Function to cleanup dataframe"""

    # Rename columns and drop non-data columns
    cols = [
        "Player",
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
        "GameDay",
    ]

    all_stats.to_csv("testing_data.csv")
    all_stats.columns = cols
    all_stats = all_stats.loc[
        (all_stats["Player"] != "Starters")
        & (all_stats["Player"] != "Reserves")
        & (all_stats["Player"] != "Team Totals")
    ]

    # Cast numeric columns to float
    numeric_cols = [
        "FGM",
        "FGA",
        "FG%",
        "PTS",
        "+/-",
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
    ]
    all_stats[numeric_cols] = all_stats[numeric_cols].apply(
        pd.to_numeric, errors="coerce"
    )

    # Convert date format
    all_stats["GameDay"] = all_stats["GameDay"].apply(convert_date, hyphens=True)
    return all_stats


def calculate_stat_points(row):
    """Function to convert stats into points"""
    point_counter = 0
    if row["MP"] == "Did Not Play":
        return nan

    point_counter += row["FGM"] * 2
    point_counter -= row["FGA"]
    point_counter += row["FTM"]
    point_counter -= row["FTA"]
    point_counter += row["3PTM"]
    point_counter += row["REB"]
    point_counter += row["AST"] * 2
    point_counter += row["STL"] * 4
    point_counter += row["BLK"] * 4
    point_counter -= row["TO"] * 2
    point_counter += row["PTS"]
    return round(point_counter, 2)


def get_dataframe(refresh: bool = False) -> pd.DataFrame:
    if refresh is False:
        data = pd.read_csv("data/all_stats.csv", index_col="Unnamed: 0")
        data.reset_index(inplace=True, drop=True)
        return data

    all_stats = get_all_stats(MONTHS)
    cleaned_stats = clean_all_stats(all_stats)
    cleaned_stats.to_csv("data/all_stats.csv")
    return cleaned_stats


def calc_expanding(stats: pd.DataFrame) -> pd.DataFrame:
    expanding_mean = (
        stats[["Player", "GameDay", "Points"]].groupby(["Player"]).expanding().mean()
    )
    expanding_mean = expanding_mean.reset_index().set_index("level_1")
    expanding_mean = expanding_mean.rename(columns={"Points": "AvPoints"})
    expanding_mean = expanding_mean[["AvPoints"]]
    stats = stats.merge(expanding_mean, how="left", left_index=True, right_index=True)
    return stats


def calc_rolling(
    stats: pd.DataFrame, windows: List[int], forward: bool = False
) -> pd.DataFrame:
    stats = stats.sort_index()
    for window in windows:
        dir = "Bckw"
        if forward is True:
            stats = stats.sort_index(ascending=False)
            dir = "Fwrd"
        rolling_period = f"Roll{dir}{window}"

        if forward is True:
            rolling = pd.DataFrame()
            for p in stats["Player"].unique():
                temp_stats = stats.loc[stats["Player"] == p]
                temp_stats = (
                    temp_stats[["Player", "GameDay", "Points"]]
                    .shift(1)
                    .rolling(window, min_periods=window)
                    .mean()
                )
                rolling = pd.concat([rolling, temp_stats])
        else:
            rolling = (
                stats[["Player", "GameDay", "Points"]]
                .groupby(["Player"])
                .rolling(window, min_periods=window)
                .mean()
            )
            rolling = rolling.reset_index().set_index("level_1")
        rolling = rolling["Points"]
        rolling = rolling.rename(rolling_period)
        stats = pd.concat([stats, rolling], axis=1)
    stats = stats.sort_index()
    return stats


def calculate_points(
    stats: pd.DataFrame, roll_forward: List[int], roll_backwards: List[int]
) -> pd.DataFrame:
    stats["Points"] = stats.apply(calculate_stat_points, axis=1)
    stats = stats.sort_values("GameDay")
    stats = calc_expanding(stats)
    stats = calc_rolling(stats, roll_backwards)
    stats = calc_rolling(stats, roll_forward, forward=True)
    return stats


def main() -> None:
    data = get_dataframe(refresh=False)
    data = calculate_points(data, roll_backwards=[1, 2], roll_forward=[1, 3])
    # print(data.loc[data["Player"] == "Joe Harris"])


if __name__ == "__main__":
    main()
