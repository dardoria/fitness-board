import streamlit as st
import datetime
from repository import banister, week_over_week

col1, col2 = st.columns(2)
period_start = col1.date_input(
    "Start date",
    datetime.date(2019, 7, 6))
period_end = col2.date_input(
    "End date",
    datetime.datetime.now())

st.write("Fitness")
st.line_chart(banister(period_start, period_end),
              x='date', use_container_width=True)

weekly_col, stats_col, map_col = st.columns(3)
weekly_col.write("Weekly Progress")
weekly_col.line_chart(week_over_week(period_end),
                      x='date', use_container_width=False)

stats_col.write("Sport statistics")
map_col.write("Activities heat map")
