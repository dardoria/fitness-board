import duckdb
import math
import pandas as pd
from dateutil.relativedelta import *
import datetime

db_con = duckdb.connect(database='data/activities.duckdb', read_only=True)


def _trimp(from_date, to_date):
    trimp = f"""
    select sum(duration * (heart_rate_bpm - 35)/(194-35) * 0.64* 2.718281828459^((heart_rate_bpm - 35)/(194-35))) as trimp, date
    from
    (select heart_rate_bpm, date_trunc('day', datetime) as date, count(datetime) / 60.0 as duration
             from activity_records
             where heart_rate_bpm > 35
             and datetime between '{from_date}' and '{to_date}'
             group by 1, 2)
    group by 2
    order by date"""
    return db_con.execute(trimp).df().set_index('date').to_dict()


def banister(from_date, to_date):
    trimp_data = _trimp(from_date, to_date)
    fitness = 0.0
    fatigue = 0.0
    r1 = 50
    r2 = 11
    k1 = 1.0
    k2 = 2.0
    result = []

    daterange = pd.date_range(
        from_date, to_date + relativedelta(weeks=+2))
    for date in daterange:
        fitness = fitness * math.exp(-1/r1) + trimp_data['trimp'].get(date, 0)
        fatigue = fatigue * math.exp(-1/r2) + trimp_data['trimp'].get(date, 0)
        performance = fitness * k1 - fatigue * k2
        result.append((fitness, fatigue, performance, date))

    return pd.DataFrame(result, columns=['fitness', 'fatigue', 'form', 'date'])


def _week_over_week(from_date, to_date):
    trimp_data = _trimp(from_date, to_date)

    daterange = pd.date_range(from_date, to_date)

    result = dict([(day, []) for day in range(7)])

    load = 0
    for date in daterange:
        if date.weekday() % 7 == 0:
            load = trimp_data['trimp'].get(date, 0)
        else:
            load += trimp_data['trimp'].get(date, 0)

        result[date.weekday()].append(load)

    final_result = []
    for key, value in result.items():
        final_result.append((key, value[0], value[1]))
    return pd.DataFrame(final_result, columns=['date', 'previous week', 'current week'])


def week_over_week(effective_date):
    # previous monday
    from_date = effective_date + relativedelta(weekday=MO(-2))
    # next sunday in same week
    to_date = effective_date + relativedelta(weekday=SU)

    return _week_over_week(from_date, to_date)
