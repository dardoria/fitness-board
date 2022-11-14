import streamlit as st
import duckdb

st.set_page_config(layout='wide')
db_con = duckdb.connect(database='data/activities.duckdb', read_only=True)

st.write("""# Sport Dashboard""")


def activities():
    return db_con.execute("SELECT * FROM activities").df()


def heart_rate():
    query1 = """SELECT date_trunc('day', datetime) as datetime, avg(heart_rate_bpm) as heart_rate_bpm 
                from activity_records 
                where datetime between '2022-01-01' and '2022-12-31'
                group by 1 order by 1"""
    return db_con.execute(query1).df()
#    return db_con.execute("SELECT heart_rate_bpm, datetime from activity_records ORDER BY datetime LIMIT 1000").df()


def fitness():
    trimp = """select heart_rate_bpm, date_trunc('day', datetime), count(datetime) / 60.0
             from activity_records
             where heart_rate_bpm > 0 
             and datetime between '2022-01-01' and '2022-12-31'
             group by 1, 2"""
    return db_con.execute(trimp).df()


st.dataframe(fitness(), use_container_width=True)
st.dataframe(activities(), use_container_width=True)
