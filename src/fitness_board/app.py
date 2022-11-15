import streamlit as st
import datetime
from repository import banister, week_over_week, sports_stats, gpx
import pydeck as pdk

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
stats_col.bar_chart(sports_stats(
    period_start, period_end), x='sport', y='hours')

map_col.write("Activities heatmap")
map_col.pydeck_chart(pdk.Deck(
    map_style='light_no_labels',
    initial_view_state=pdk.ViewState(
        latitude=42.6977,
        longitude=23.3219,
        zoom=4.7,
        pitch=40,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=gpx(period_start, period_end),
            get_position='[longitude_degrees, latitude_degrees]',
            get_color='[200, 30, 0, 160]',
            get_radius=2000,
        ),
    ],
))
