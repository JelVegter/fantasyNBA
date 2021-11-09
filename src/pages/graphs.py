import streamlit as st
from typing import List
from league import league
from playergroup import MyPlayerGroup, OtherPlayerGroup, FreeAgentPlayerGroup, choose_team
from players import FREE_AGENTS, retrieve_free_agents
from streaming import find_optimal_solution
from teams import TEAMS
from schedule import SCHEDULE, Schedule


## Graph to show cumulative score per day
