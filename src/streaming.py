from itertools import combinations_with_replacement
from typing import List, Tuple, Dict
from collections import Counter
from pandas import DataFrame, concat
from src.playergroup import FreeAgentPlayerGroup
from src.players import FREE_AGENTS, retrieve_player_data
from src.schedule import Schedule, NOW

SCHEDULE = Schedule(2022)


def determine_day_range(week: str = "This Week") -> None:
    global CUR_DAY_OF_WEEK
    global DAY_COLUMNS
    global NUM_DAYS_REMAIN

    if week == "This Week":
        CUR_DAY_OF_WEEK = NOW.dayofweek
    else:
        CUR_DAY_OF_WEEK = 0
    DAY_COLUMNS = [n for n in range(0, 7) if n >= CUR_DAY_OF_WEEK]
    NUM_DAYS_REMAIN = 7 - CUR_DAY_OF_WEEK


def build_dataframe(week: str) -> DataFrame:
    """Function to build dataframe with free agents, points, and gamedays"""
    free_agents = FreeAgentPlayerGroup(players=FREE_AGENTS)
    stats = retrieve_player_data(free_agents.players)
    stats = stats[["Player", "Team", "Status", "Score"]].loc[stats["Status"] != "OUT"]
    daily_schedule = SCHEDULE.teams_playing_per_day(week=week, pretty=False)
    dataframe = stats.merge(
        daily_schedule, how="left", left_on="Team", right_index=True
    )
    return dataframe


def game_day_pattern(row: DataFrame) -> str:
    """Function to general the game day pattern used to identify perfectly overlapping players"""
    days_pattern = [str(row[r]) for r in DAY_COLUMNS]
    return "".join(days_pattern)


def drop_strictly_worse_players(dataframe: DataFrame, max_slots: int = 3) -> DataFrame:
    """Function that drops players that have the same game schedule with lower points"""
    dataframe = dataframe.sort_values(by="Score", ascending=False)
    game_day_patterns = dataframe["GameDayPattern"].unique()
    rebuilt_dataframe = DataFrame()
    for pattern in game_day_patterns:
        dataframe_per_pattern = dataframe.loc[dataframe["GameDayPattern"] == pattern]
        rebuilt_dataframe = concat(
            [rebuilt_dataframe, dataframe_per_pattern.head(max_slots)]
        )
    return rebuilt_dataframe


def convert_to_ones(dataframe: DataFrame) -> DataFrame:
    for col in dataframe:
        dataframe[col] = [0 if i == 0 else 1 for i in dataframe[col]]
    return dataframe


def calculate_points_per_day(dataframe: DataFrame) -> DataFrame:
    """Function to convert the binary to points per day"""
    dataframe[DAY_COLUMNS] = convert_to_ones(dataframe[DAY_COLUMNS])
    for day in DAY_COLUMNS:
        dataframe[day] = dataframe[day] * dataframe["Score"]
        dataframe[day] = dataframe[day].astype("float")
    return dataframe


def clean_dataframe_for_operations(dataframe: DataFrame) -> DataFrame:
    columns = ["Player"] + DAY_COLUMNS
    dataframe = dataframe[columns]
    return dataframe


def check_number_of_trades_sequence(solution: Tuple[int], max_trades: int) -> bool:
    legal = True
    count = 1
    while not count > max_trades:
        for day in range(1, NUM_DAYS_REMAIN):
            if solution[day] != solution[day - 1]:
                count += 1
        break
    if count > max_trades:
        legal = False
    return legal


def evaluate_solution(solution: tuple, max_trades: int) -> bool:
    """Function to evaluate a solution"""
    # Solution cannot have more unique players than max trades
    if len(set(solution)) > max_trades:
        return False
    # Solution cannot have more changes than max trades
    if check_number_of_trades_sequence(solution, max_trades) is False:
        return False
    return True


def filter_combos(
    list_of_solutions: List[tuple],
    list_of_solution_points: List[float],
    best_combo: Tuple[int],
) -> Tuple[list, list]:
    """Function to filter solutions containing the most frequent player of best solution"""
    # Find index of best player
    counter = Counter(best_combo)
    most_common_player_index = counter.most_common(1)[0][0]
    # Find indeces of all solutions with said player
    indeces_of_solutions_containing_best_player = set(
        [i for i, x in enumerate(list_of_solutions) if most_common_player_index in x]
    )

    # Rebuild lists excluding combinations including best player
    list_of_solutions = [
        player_combo
        for list_index, player_combo in enumerate(list_of_solutions)
        if list_index not in indeces_of_solutions_containing_best_player
    ]
    list_of_solution_points = [
        player_combo
        for list_index, player_combo in enumerate(list_of_solution_points)
        if list_index not in indeces_of_solutions_containing_best_player
    ]
    return list_of_solutions, list_of_solution_points


def retrieve_best_solutions(
    solution_dictionary: dict, number_solutions: int
) -> Dict[Tuple[int], float]:
    """Function to find the top x solutions based on points"""
    best_solutions_dictionary = dict()
    list_of_solutions = list(solution_dictionary.keys())
    list_of_solution_points = list(solution_dictionary.values())

    # QUESTION: FIRST OPTION IS NO GOOD
    for c in range(0, number_solutions):
        max_value = max(list_of_solution_points)
        best_solution_index = list_of_solution_points.index(max_value)
        best_combo = list_of_solutions[best_solution_index]
        best_solutions_dictionary[best_combo] = max_value
        # Filter out combos containing the most frequent player in the solution
        results = filter_combos(list_of_solutions, list_of_solution_points, best_combo)
        list_of_solutions, list_of_solution_points = results[0], results[1]
    return best_solutions_dictionary


def streaming_options_results(
    dataframe: DataFrame,
    best_solution_players_dictionary: Dict[tuple, float],
    week: str,
    legal_solutions_checked: int,
):
    """Function to print the best streaming options"""
    weekdays = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"][CUR_DAY_OF_WEEK:]
    print(f"Possible solutions checked: {legal_solutions_checked}")

    results = dict()

    count = 0

    for solution, points in best_solution_players_dictionary.items():
        streaming_solution = DataFrame()
        # Find the names of players based on their index
        solution_players: List[str] = [
            dataframe.loc[index, "Player"] for index in solution
        ]
        solution_players_points: List[str] = [
            dataframe.loc[index, d] for d, index in zip(DAY_COLUMNS, solution)
        ]
        # Points of players for the correct day
        streaming_solution["Day"] = weekdays
        streaming_solution["Player"] = solution_players
        streaming_solution["Points"] = solution_players_points
        streaming_solution["Total"] = streaming_solution["Points"].cumsum()
        # streaming_solution.set_index("Day", inplace=True, drop=True)
        results[count] = streaming_solution
        count += 1
    return results

    # for solution, points in best_solution_players_dictionary.items():
    #     # Find the names of players based on their index
    #     solution_players: List[str] = [dataframe.loc[index, "Player"] for index in solution]
    #     solution_players_points: List[str] = [dataframe.loc[index, d] for d, index in zip(DAY_COLUMNS, solution)]
    #     # Points of players for the correct day
    #     stream_schedule = zip(weekdays, solution_players, solution_players_points)
    #     print("-" * 25)
    #     print(f"Projected points: {points}")
    #     print("Player Stream:")
    #     return [(f'{day} {player} - {points}') for day, player, points in stream_schedule]
    #     # [print(f'{day} {player} - {points}') for day, player, points in stream_schedule]
    #     # print()


def brute_force(
    dataframe: DataFrame, max_trades: int, week: str
):  # -> Dict[tuple, float]
    print(f"Brute forcing all combinations...")
    columns = ["Player"] + DAY_COLUMNS
    dataframe = dataframe[columns]
    solution_dictionary = dict()
    legal_solutions_checked = 0
    indexes = dataframe.index
    combinations = list(combinations_with_replacement(indexes, NUM_DAYS_REMAIN))

    for combo in combinations:
        assert len(DAY_COLUMNS) == len(combo)
        legal = evaluate_solution(solution=combo, max_trades=max_trades)
        if legal is True:
            legal_solutions_checked += 1
            points = 0
            # Use index to retrieve points and player name from dataframe
            for day, player_index in zip(DAY_COLUMNS, combo):
                points += dataframe.loc[player_index, day]
                # Dictionary containing all legal solutions and their points
                solution_dictionary[combo] = round(points)
    best_solution_dictionary = retrieve_best_solutions(solution_dictionary, 5)
    solutions = streaming_options_results(
        dataframe, best_solution_dictionary, week, legal_solutions_checked
    )
    return solutions


def prep_dataframe(max_slots: int, week: str):
    """Generates global variables"""
    determine_day_range(week=week)

    dataframe = build_dataframe(week=week)
    dataframe["GameDayPattern"] = dataframe.apply(lambda x: game_day_pattern(x), axis=1)
    dataframe = drop_strictly_worse_players(dataframe, max_slots=max_slots)
    dataframe = calculate_points_per_day(dataframe)
    dataframe = clean_dataframe_for_operations(dataframe)
    return dataframe


def find_optimal_solution(max_slots: int, max_trades: int, week: str):
    dataframe = prep_dataframe(max_slots, week)
    bf = brute_force(dataframe, max_trades, week)
    return bf


# def find_optimal_solution(max_slots: int, max_trades: int, week: str):
#     """Generates global variables"""
#     determine_day_range(week=week)
#
#     """Main function to find optimal streaming options"""
#     dataframe = build_dataframe(week=week)
#     dataframe["GameDayPattern"] = dataframe.apply(lambda x: game_day_pattern(x), axis=1)
#     dataframe = drop_strictly_worse_players(dataframe, max_slots=max_slots)
#     dataframe = calculate_points_per_day(dataframe)
#     dataframe = clean_dataframe_for_operations(dataframe)
#     bf = brute_force(dataframe, max_trades, week)
#     return bf

#
# if __name__ == "__main__":
#     find_optimal_solution(max_slots=2, max_trades=4, week="This Week")
# find_optimal_solution(max_slots=1, max_trades=3, week="NextWeek")
