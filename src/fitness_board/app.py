import streamlit as st
import duckdb
import math
import pandas as pd
from dateutil.relativedelta import relativedelta
import datetime

st.set_page_config(layout='wide')
db_con = duckdb.connect(database='data/activities.duckdb', read_only=True)

general = st.expander(label="Fitness", expanded=True)
col1, col2 = general.columns(2)
period_start = col1.date_input(
    "Start date",
    datetime.date(2019, 7, 6))
period_end = col2.date_input(
    "End date",
    datetime.datetime.now())


def activities():
    return db_con.execute("SELECT * FROM activities").df()


def heart_rate():
    query1 = """SELECT date_trunc('day', datetime) as datetime, avg(heart_rate_bpm) as heart_rate_bpm
                from activity_records
                where datetime between '2022-01-01' and '2022-12-31'
                group by 1 order by 1"""
    return db_con.execute(query1).df()
#    return db_con.execute("SELECT heart_rate_bpm, datetime from activity_records ORDER BY datetime LIMIT 1000").df()


def trimp():
    trimp = f"""
    select sum(duration * (heart_rate_bpm - 35)/(194-35) * 0.64* 2.718281828459^((heart_rate_bpm - 35)/(194-35))) as trimp, day
    from
    (select heart_rate_bpm, date_trunc('day', datetime) as day, count(datetime) / 60.0 as duration
             from activity_records
             where heart_rate_bpm > 35
             and datetime between '{period_start}' and '{period_end}'
             group by 1, 2)
    group by 2
    order by day"""
    return db_con.execute(trimp).df().set_index('day').to_dict()


def banister():
    trimp_data = trimp()
    fitness = 0.0
    fatigue = 0.0
    r1 = 50
    r2 = 11
    k1 = 1.0
    k2 = 2.0
    result = []

    daterange = pd.date_range(
        period_start, period_end + relativedelta(weeks=+2))
    for date in daterange:
        fitness = fitness * math.exp(-1/r1) + trimp_data['trimp'].get(date, 0)
        fatigue = fatigue * math.exp(-1/r2) + trimp_data['trimp'].get(date, 0)
        performance = fitness * k1 - fatigue * k2
        result.append((fitness,
                       fatigue, performance,
                       date))

    return pd.DataFrame(result, columns=['fitness', 'fatigue', 'form', 'date'])


general.line_chart(banister(), x='date', use_container_width=True)
st.dataframe(banister(), use_container_width=True)
