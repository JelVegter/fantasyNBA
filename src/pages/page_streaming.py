import streamlit as st
from streaming import find_optimal_solution


def app():
    # Side bar
    with st.sidebar:
        PERIOD = st.sidebar.selectbox(label="Week", options=["This Week", "Next Week"])
        a, b = st.columns(2)
        MAX_TRADES = a.number_input(
            label="Max Trades", format="%i", min_value=1, max_value=7, step=1
        )
        MAX_SLOTS = b.number_input(
            label="Max Slots", format="%i", min_value=1, max_value=5, step=1
        )

    solution = find_optimal_solution(
        max_slots=MAX_SLOTS, max_trades=MAX_TRADES, week=PERIOD
    )
    solution1 = solution[0].style.format({"Points": "{:.1f}", "Total": "{:.1f}"})
    solution2 = solution[1].style.format({"Points": "{:.1f}", "Total": "{:.1f}"})
    solution3 = solution[2].style.format({"Points": "{:.1f}", "Total": "{:.1f}"})
    solution4 = solution[3].style.format({"Points": "{:.1f}", "Total": "{:.1f}"})
    solution5 = solution[4].style.format({"Points": "{:.1f}", "Total": "{:.1f}"})

    c, d = st.columns(2)
    c.title("Stream Schedule")
    d.title("Points")
    c.dataframe(solution1)
    c.write(f"Projected points: {round(solution[0]['Points'].sum(),2)}")
    d.area_chart(data=solution[0]["Total"], height=250)

    e, f = st.columns(2)
    e.dataframe(solution2)
    e.write(f"Projected points: {round(solution[1]['Points'].sum(),2)}")
    f.area_chart(data=solution[1]["Total"], height=250)

    g, h = st.columns(2)
    g.dataframe(solution3)
    g.write(f"Projected points: {round(solution[2]['Points'].sum(),2)}")
    h.area_chart(data=solution[2]["Total"], height=250)

    i, j = st.columns(2)
    i.dataframe(solution4)
    i.write(f"Projected points: {round(solution[3]['Points'].sum(),2)}")
    j.area_chart(data=solution[3]["Total"], height=250)

    k, l = st.columns(2)
    k.dataframe(solution5)
    k.write(f"Projected points: {round(solution[4]['Points'].sum(),2)}")
    l.area_chart(data=solution[4]["Total"], height=250)
