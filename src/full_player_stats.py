from datetime import datetime
import asyncio
import aiohttp
from pprint import pprint
from timeit import default_timer
from typing import List
from dateutil import parser
import pandas as pd
from numpy import nan
from pandas.core.frame import DataFrame

try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except:
    pass

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


def time_func(func):
    def wrapper(*args, **kwargs):
        start = default_timer()
        result = func(*args, **kwargs)
        end = default_timer()
        print(end - start)
        return result

    return wrapper


async def fetch(session, url: str):
    async with session.get(url, ssl=False) as response:
        data = await response.read()
        return data


async def fetch_api_data(urls: list) -> tuple:
    print("Fetching api data...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(session, url))
        responses = await asyncio.gather(*tasks, return_exceptions=False)
    return responses


def fetch_played_games(months: List[str]) -> DataFrame:
    print("Fetching played games...")
    base_url = "https://www.basketball-reference.com/leagues/NBA_2022_games-{}.html"
    urls = [base_url.format(month) for month in months]
    responses = asyncio.run(fetch_api_data(urls))
    games = pd.concat([pd.read_html(r)[0] for r in responses])
    games = games.loc[games["Attend."] > 0]
    games["AbbrHomeTeam"] = games["Home/Neutral"].map(find_abbreviation)
    games["AbbrVisitorTeam"] = games["Visitor/Neutral"].map(find_abbreviation)
    games["DateStr"] = games["Date"].map(convert_date)
    games["url"] = games.apply(gen_url, axis=1)
    return games


def fetch_all_stats(
    urls: List[str], dates: list, home_teams: list, away_teams: list
) -> DataFrame:
    responses = asyncio.run(fetch_api_data(urls))
    reponses_and_dates = zip(dates, responses, home_teams, away_teams)
    tables = []
    counter = 0
    for date, response, home_team, away_team in reponses_and_dates:
        tables.append(parse_html_tables(response, date, home_team, away_team))
        counter += 1
        if counter % 10 == 0:
            print(f"Parsed {counter} of out {len(responses)} responses")
    all_stats = pd.concat(tables)
    all_stats.reset_index(inplace=True, drop=True)
    return all_stats


def parse_html_tables(
    html: str, date, home_team_ab: str, away_team_ab: str
) -> pd.DataFrame:
    away_team = pd.read_html(html)[0]
    away_team["Team"] = away_team_ab
    away_team["Opponent"] = home_team_ab
    minutes_played = away_team[("Basic Box Score Stats", "MP")].iloc[-1]
    minutes_played = int(minutes_played)
    nr_overtimes = (minutes_played - 240) / 25
    table_html_index = int(8 + nr_overtimes)
    home_team = pd.read_html(html)[table_html_index]
    home_team["Team"] = home_team_ab
    home_team["Opponent"] = away_team_ab
    stats = pd.concat([away_team, home_team])
    stats["GameDay"] = date
    return stats


@time_func
def get_all_stats(months: List[str]) -> pd.DataFrame:
    print("Getting all stats...")
    played_games = fetch_played_games(months)
    urls = played_games["url"].to_list()
    dates = played_games["Date"].to_list()
    home_teams = played_games["AbbrHomeTeam"].to_list()
    away_teams = played_games["AbbrVisitorTeam"].to_list()
    stats = fetch_all_stats(urls, dates, home_teams, away_teams)
    return stats


def clean_all_stats(all_stats: pd.DataFrame) -> pd.DataFrame:
    """Function to cleanup dataframe"""
    print("Cleaning stats...")
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
        "Team",
        "Opponent",
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


def calculate_points_against_teams(stats: DataFrame, refresh: bool = True) -> DataFrame:
    stats = stats[["Opponent", "Points", "GameDay"]]
    stats = stats.rename(columns={"Opponent": "Team"})
    points_against_per_day = stats.groupby(by=["Team", "GameDay"], as_index=False).sum()
    mean_points_against = (
        points_against_per_day[["Team", "Points"]].groupby(by="Team").mean()
    )
    avg = mean_points_against["Points"].mean()
    mean_points_against["Amplifier"] = mean_points_against["Points"] / avg
    if refresh:
        mean_points_against.to_csv("data/team_point_amplifiers.csv")
    return mean_points_against


def refresh_data():
    data = get_dataframe(refresh=True)
    data = calculate_points(data, roll_backwards=[2, 4], roll_forward=[1, 3])
    team_point_amplifiers = calculate_points_against_teams(data, refresh=True)


def main() -> None:
    data = get_dataframe(refresh=False)
    data = calculate_points(data, roll_backwards=[2, 4], roll_forward=[1, 3])
    team_point_amplifiers = calculate_points_against_teams(data, refresh=True)
    print(team_point_amplifiers.sort_values(by="Amplifier"))
    pprint(data.loc[data["Player"] == "Joe Harris"])
    # responses = get_all_stats(["november"])
    # print(responses)
    # print(data.columns)


if __name__ == "__main__":
    main()
