"""Module containing functions and a class relating to scheduling related information"""
from typing import List
import datetime as dt
import asyncio
import aiohttp
from timeit import default_timer
from pandas import (
    DataFrame,
    Timestamp,
    to_datetime,
    read_html,
    concat,
    offsets,
)
from teams import TEAMS, abbreviate_team
from league import YEAR

try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except:
    pass
NOW = Timestamp(dt.datetime.now(), unit="s", tz="US/Eastern").normalize()
CURRENT_WEEK = NOW.isocalendar()[1]
MONTHS = ["october", "november", "december"]


class Schedule:
    """Class containing NBA game schedule information"""

    def __init__(self, year: int) -> None:
        self.year: int = year
        self.months: List[str] = MONTHS
        self.schedule: DataFrame = schedule_builder(year, MONTHS)
        self.weeks: List[int] = [CURRENT_WEEK, CURRENT_WEEK + 1]

    def teams_playing_per_day(
        self, week: str = "This Week", sort: str = "Total", pretty: bool = True
    ) -> DataFrame:
        """Method to print the schedule in a daily view"""
        week_of_games = CURRENT_WEEK
        if week == "Next Week":
            if week_of_games == 52:
                week_of_games = 1
            else:
                week_of_games += 1
        games = teams_games_per_day(week=week_of_games, sort=sort)
        if pretty is True:
            weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            games.columns = weekdays + ["Total", "Today", "Next3Days"]
            games[weekdays] = games[weekdays].applymap(
                lambda x: x if isinstance(x, str) else ""
            )  # TODO changed
            games = games.sort_values(by=sort, ascending=False)
            games[["Total", "Today", "Next3Days"]] = games[
                ["Total", "Today", "Next3Days"]
            ].astype("int")
        return games


def time_func(func):
    def wrapper(*args, **kwargs):
        start = default_timer()
        func(*args, **kwargs)
        end = default_timer()
        print(end - start)

    return wrapper


# def get_tasks(session, year: int, months: list, url: str):
#     tasks = []
#     for month in months:
#         tasks.append(session.get(url.format(year, month.lower()), ssl=False))
#     return tasks
#
#
# async def get_api_data(year: int, months: list):
#     url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"
#     async with aiohttp.ClientSession() as session:
#         tasks = get_tasks(session, year, months, url)
#         responses = await asyncio.gather(*tasks)
#     return responses


async def fetch(session, url: str):
    async with session.get(url, ssl=False) as response:
        data = await response.read()
        return data


async def fetch_api_data(year: int, months: list):
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"
    async with aiohttp.ClientSession() as session:
        tasks = []
        for month in months:
            tasks.append(fetch(session, url.format(year, month.lower())))
        responses = await asyncio.gather(*tasks, return_exceptions=False)
    return responses


def schedule_builder(year: int, months: list) -> DataFrame:
    """Function to create the NBA schedule by scraping data from basketball-reference.com"""
    responses = asyncio.run(fetch_api_data(year, months))
    data = [read_html(r)[0] for r in responses]
    games = concat(data)

    games = games.reset_index()
    games = games[["Date", "Start (ET)", "Visitor/Neutral", "Home/Neutral"]]
    games["Date"] = to_datetime(games["Date"], errors="coerce").dt.tz_localize(
        tz="US/Eastern"
    )
    games["Week"] = games["Date"].dt.isocalendar().week
    games = games.loc[games["Week"] >= CURRENT_WEEK]
    games["Visitor/Neutral"] = games["Visitor/Neutral"].map(abbreviate_team)
    games["Home/Neutral"] = games["Home/Neutral"].map(abbreviate_team)
    return games


# def schedule_builder(year: int, months: list) -> DataFrame:
#     """Function to create the NBA schedule by scraping data from basketball-reference.com"""
#     first = True
#     games = DataFrame()
#     for month in months:
#         try:
#             schedule = read_html(
#                 f"https://www.basketball-reference.com/leagues/NBA_{year}_games-{month.lower()}.html"
#             )
#             if first:
#                 games = schedule[0]
#                 first = False
#             else:
#                 games = games.append(schedule[0])
#         except Exception as error:
#             print(f"schedule_builder.Error extracting data for {year},{month}")
#             print(error)
#
#     games = games.reset_index()
#     games = games[["Date", "Start (ET)", "Visitor/Neutral", "Home/Neutral"]]
#     games["Date"] = to_datetime(games["Date"], errors="coerce").dt.tz_localize(
#         tz="US/Eastern"
#     )
#     games["Week"] = games["Date"].dt.isocalendar().week
#     games = games.loc[games["Week"] >= CURRENT_WEEK]
#     games["Visitor/Neutral"] = games["Visitor/Neutral"].map(abbreviate_team)
#     games["Home/Neutral"] = games["Home/Neutral"].map(abbreviate_team)
#     return games


def convert_timestamp_to_datetime(timestamp: Timestamp):
    """Function to convert a timestamp to a datetime object"""
    return to_datetime(timestamp)


def teams_games_per_day(week: int, sort="Total") -> DataFrame:
    """Function to create a per-day overview of which teams are playing"""
    schedule = SCHEDULE.schedule
    today_day_of_week = NOW.dayofweek
    schedule = schedule.loc[schedule["Date"] >= NOW]
    schedule = schedule.loc[schedule["Week"] == week]
    schedule["DateTime"] = schedule["Date"].map(convert_timestamp_to_datetime)
    schedule["DayOfWeek"] = schedule["DateTime"].dt.dayofweek
    daily_schedule = DataFrame(columns=[0, 1, 2, 3, 4, 5, 6, "Total"])

    for t in TEAMS:
        daily_schedule.at[t, ["Total", "Today", "Next3Days"]] = 0
        team_schedule = schedule.loc[
            (schedule["Visitor/Neutral"] == t) | (schedule["Home/Neutral"] == t)
        ]
        for i in range(0, 7):
            team_schedule_per_day = team_schedule.loc[team_schedule["DayOfWeek"] == i]
            if team_schedule_per_day.shape[0] > 0:

                if t == team_schedule_per_day["Home/Neutral"].iloc[0]:
                    daily_schedule.at[t, i] = (
                        "@" + team_schedule_per_day["Visitor/Neutral"].iloc[0]
                    )
                else:
                    daily_schedule.at[t, i] = team_schedule_per_day[
                        "Home/Neutral"
                    ].iloc[0]
                daily_schedule.at[t, "Total"] += 1

                if i == today_day_of_week:
                    daily_schedule.at[t, "Today"] += 1
                if i - today_day_of_week <= 2:
                    daily_schedule.at[t, "Next3Days"] += 1
            else:
                daily_schedule.at[t, i] = 0
    return daily_schedule


def team_games_week_count(team: str, schedule: DataFrame, week: int, date):
    """Function to calculate the amount of games a certain team has remaining in a week"""
    schedule = schedule.loc[schedule["Date"] >= date]
    schedule = schedule.loc[schedule["Week"] == week]
    schedule = schedule.loc[
        (schedule["Visitor/Neutral"] == team) | (schedule["Home/Neutral"] == team)
    ]
    return schedule.count()[0]


def team_games_days_count(team: str, schedule: DataFrame, date, days_offset: int):
    """Function to calculate the amount of games a certain : str will play with one or a few days"""
    schedule = schedule.loc[
        (schedule["Date"] >= date)
        & (schedule["Date"] <= date + offsets.Day(days_offset))
    ]
    schedule = schedule.loc[
        (schedule["Visitor/Neutral"] == team) | (schedule["Home/Neutral"] == team)
    ]
    return schedule.count()[0]


def team_games_to_play(teams: List[str]) -> DataFrame:
    """Function to calculate the amount of games a certain team has remaining in a week"""
    weeks = SCHEDULE.weeks
    game_dates = SCHEDULE.schedule
    team_games = DataFrame()
    count = 0
    for t in teams:
        team_games.at[count, "Team"] = t
        team_games.at[count, "This Week"] = team_games_week_count(
            t, game_dates, weeks[0], NOW
        )
        team_games.at[count, "Next Week"] = team_games_week_count(
            t, game_dates, weeks[1], NOW
        )
        team_games.at[count, "Today"] = team_games_days_count(t, game_dates, NOW, 0)
        team_games.at[count, "Next3Days"] = team_games_days_count(t, game_dates, NOW, 2)
        count += 1
    for c in team_games.columns:
        try:
            team_games[c] = team_games[c].astype(int)
        except:
            pass
    return team_games


SCHEDULE = Schedule(YEAR)


def main() -> None:
    # print(SCHEDULE.year)
    # print(SCHEDULE.months)
    # print(SCHEDULE.weeks)
    # print(SCHEDULE.refresh_data())
    # pprint(SCHEDULE.teams_playing_per_day("This Week", pretty=True))
    # pprint(retrieve_schedule())
    # retrieve_schedule()
    # test_func()
    results = schedule_builder(year=2022, months=MONTHS)
    print(results)


if __name__ == "__main__":
    main()
