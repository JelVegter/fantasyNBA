import streamlit as st

from fantasy_nba.full_player_stats import refresh_amp_data
from fantasy_nba.players import refresh_free_agents


# Define the multipage class to manage the multiple apps in our program
class MultiPage:
    """Framework for combining multiple streamlit applications."""

    def __init__(self) -> None:
        """Constructor class to generate a list which will store all our
        applications as an instance variable."""
        self.pages = []

    def add_page(self, title, func) -> None:
        """Class Method to Add pages to the project
        Args:
            title ([str]): The title of page which we are adding to the list of apps

            func: Python function to render this page in Streamlit
        """

        self.pages.append({"title": title, "function": func})

    def run(self):
        # Drodown to select the page to run
        if st.button(label="Refresh Amplifiers"):
            refresh_amp_data()
        if st.button(label="Refresh Free Agents"):
            global FREE_AGENTS
            FREE_AGENTS = refresh_free_agents(size=500)
        page = st.sidebar.selectbox(
            "App Navigation", self.pages, format_func=lambda page: page["title"]
        )

        # run the app function
        page["function"]()
