import src.menu_functions


## FIND A WAY TO BYPASS MANUAL INPUT

def tests() -> None:
    """Main function"""
    menu_functions.print_free_players(True)
    menu_functions.print_free_players(False)
    menu_functions.print_and_search_free_player()

    menu_functions.print_free_player_suggestions(True)
    menu_functions.print_free_player_suggestions(False)

    menu_functions.print_optimal_streaming_flow(3, 4, 'ThisWeek')
    menu_functions.print_optimal_streaming_flow(3, 4, 'NextWeek')

    menu_functions.print_roster_stats(True)
    menu_functions.print_roster_stats(False)
    menu_functions.print_matchup_comparison(True)
    menu_functions.print_matchup_comparison(False)

    menu_functions.print_team_schedules('ThisWeek')
    menu_functions.print_team_schedules('NextWeek')
    menu_functions.refresh_schedule_data()

if __name__=='__main__':
    tests()


# Remaining questions:
# Is it a problem to have a child class that CAN'T use certain functions of the parent class?
