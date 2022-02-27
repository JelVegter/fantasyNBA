"""Module containing functions and a class relating to scheduling related information"""
import asyncio
import datetime as dt
from typing import List

from pandas import DataFrame, Timestamp, concat, offsets, read_csv, read_html, to_datetime

from fantasy_nba.league import YEAR
from fantasy_nba.nba_utils import fetch_api_data, time_func
from fantasy_nba.teams import TEAMS, abbreviate_team

try:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except:
    pass

NOW = Timestamp(dt.datetime.now(), unit="s", tz="US/Eastern").normalize()
CURRENT_WEEK = NOW.isocalendar()[1]
MONTHS = ["october", "november", "december", "january", "february", "march"]


class Schedule:
    """Class containing NBA game schedule information"""

    def __init__(self, year: int) -> None:
        self.year: int = year
        self.months: List[str] = MONTHS
        self.schedule: DataFrame = schedule_builder(year, MONTHS)
        self.weeks: List[int] = [CURRENT_WEEK, CURRENT_WEEK + 1]

    def teams_playing_per_day(
        self,
        schedule: DataFrame = None,
        week: str = "This Week",
        sort: str = "Total",
        pretty: bool = True,
        test: bool = False,
    ) -> DataFrame:
        """Method to print the schedule in a daily view"""
        schedule = self.schedule
        week_of_games = CURRENT_WEEK
        if week == "Next Week":
            if week_of_games == 52:
                week_of_games = 1
            else:
                week_of_games += 1
        games = teams_games_per_day(schedule=schedule, week=week_of_games, test=test)
        if pretty is True:
            weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            games.columns = weekdays + ["Total", "Today", "Next3Days"]
            games[weekdays] = games[weekdays].applymap(lambda x: x if isinstance(x, str) else "")
            games = games.sort_values(by=sort, ascending=False)
            games[["Total", "Today", "Next3Days"]] = games[["Total", "Today", "Next3Days"]].astype(
                "int"
            )
        return games


def retrieve_amplifier_ratio(amplifiers: DataFrame, team: str, visitor: bool):
    if team == "PHL":
        team = "PHI"
    elif team == "BKN":
        team = "BRK"
    elif team == "CHA":
        team = "CHO"
    amplifier = amplifiers.loc[team, "AmpHome"]
    if visitor:
        amplifier = amplifiers.loc[team, "AmpAway"]
    return amplifier


def schedule_builder(year: int, months: list) -> DataFrame:
    """Function to create the NBA schedule by scraping data from basketball-reference.com"""
    base_url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html"
    urls = [base_url.format(year, month) for month in months]
    responses = asyncio.run(fetch_api_data(urls))
    print([url for url in urls])
    data = [read_html(r)[0] for r in responses]
    games = concat(data)

    games = games.reset_index()
    games = games[["Date", "Start (ET)", "Visitor/Neutral", "Home/Neutral"]]
    games["Date"] = to_datetime(games["Date"], errors="coerce").dt.tz_localize(tz="US/Eastern")
    games["Week"] = games["Date"].dt.isocalendar().week
    games["Visitor/Neutral"] = games["Visitor/Neutral"].map(abbreviate_team)
    games["Home/Neutral"] = games["Home/Neutral"].map(abbreviate_team)
    amplifier = read_csv("data/team_point_amplifiers.csv", index_col="Team")
    games["Visitor_amp"] = games["Visitor/Neutral"].apply(
        lambda x: retrieve_amplifier_ratio(amplifier, x, visitor=True)
    )
    games["Home_amp"] = games["Home/Neutral"].apply(
        lambda x: retrieve_amplifier_ratio(amplifier, x, visitor=False)
    )
    return games


def convert_timestamp_to_datetime(timestamp: Timestamp):
    """Function to convert a timestamp to a datetime object"""
    return to_datetime(timestamp)


def teams_games_per_day(schedule: DataFrame, week: int, test: bool = False) -> DataFrame:
    """Function to create a per-day overview of which teams are playing"""
    today_day_of_week = NOW.dayofweek
    if not test:
        schedule = schedule.loc[
            schedule["Date"] >= NOW
        ]  # removed as it ruins pytest on past weeks
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
                    daily_schedule.at[t, i] = team_schedule_per_day["Home/Neutral"].iloc[0]
                daily_schedule.at[t, "Total"] += 1

                if i == today_day_of_week:
                    daily_schedule.at[t, "Today"] += 1
                if i - today_day_of_week <= 2:
                    daily_schedule.at[t, "Next3Days"] += 1
            else:
                daily_schedule.at[t, i] = 0
    return daily_schedule


def calculate_total_amplifier_ratio(row: DataFrame, team: str):
    calculated_amp = 0
    if row.shape[0] > 0:
        if row["Home/Neutral"] == team:
            calculated_amp = row["Visitor_amp"]
        else:
            calculated_amp = row["Home_amp"]
    return calculated_amp


def team_games_week_count(team: str, schedule: DataFrame, week: int, date):
    """Function to calculate the amount of games a certain team has remaining in a week"""
    schedule = schedule.loc[schedule["Date"] >= date]
    schedule = schedule.loc[schedule["Week"] == week]
    schedule = schedule.loc[
        (schedule["Visitor/Neutral"] == team) | (schedule["Home/Neutral"] == team)
    ]
    schedule["Calculated_amp"] = schedule.apply(
        lambda x: calculate_total_amplifier_ratio(x, team),
        axis=1,
    )
    return schedule.count()[0], schedule["Calculated_amp"].sum()


def team_games_days_count(team: str, schedule: DataFrame, date, days_offset: int):
    """Function to calculate the amount of games a certain : str will play with one or a few days"""
    schedule = schedule.loc[
        (schedule["Date"] >= date) & (schedule["Date"] <= date + offsets.Day(days_offset))
    ]
    schedule = schedule.loc[
        (schedule["Visitor/Neutral"] == team) | (schedule["Home/Neutral"] == team)
    ]
    schedule["Calculated_amp"] = schedule.apply(
        lambda x: calculate_total_amplifier_ratio(x, team),
        axis=1,
    )
    return schedule.count()[0], schedule["Calculated_amp"].sum()


def team_games_to_play(teams: List[str]) -> DataFrame:
    """Function to calculate the amount of games a certain team has remaining in a week"""
    SCHEDULE = Schedule(2022)
    weeks = SCHEDULE.weeks
    game_dates = SCHEDULE.schedule
    team_games = DataFrame()
    count = 0
    for team in teams:
        team_games.at[count, "Team"] = team
        (
            team_games.at[count, "This Week"],
            team_games.at[count, "ThisWeekAmp"],
        ) = team_games_week_count(team, game_dates, weeks[0], NOW)
        (
            team_games.at[count, "Next Week"],
            team_games.at[count, "NextWeekAmp"],
        ) = team_games_week_count(team, game_dates, weeks[1], NOW)
        (
            team_games.at[count, "Today"],
            team_games.at[count, "TodayAmp"],
        ) = team_games_days_count(team, game_dates, NOW, 0)
        (
            team_games.at[count, "Next3Days"],
            team_games.at[count, "Next3DaysAmp"],
        ) = team_games_days_count(team, game_dates, NOW, 2)
        count += 1
        int_cols = ["This Week", "Next Week", "Today", "Next3Days"]
        for col in int_cols:
            try:
                team_games[col] = team_games[col].astype(int)
            except:
                pass
    return team_games


def main() -> None:
    SCHEDULE = Schedule(YEAR)
    # print(SCHEDULE.year)
    # print(SCHEDULE.months)
    # print(SCHEDULE.weeks)
    # print(SCHEDULE.refresh_data())
    # pprint(SCHEDULE.teams_playing_per_day("This Week", pretty=True))
    # pprint(retrieve_schedule())
    # retrieve_schedule()
    # test_func()
    results = schedule_builder(year=2022, months=["october"])
    print(SCHEDULE.schedule)
    print(results)


if __name__ == "__main__":
    main()
