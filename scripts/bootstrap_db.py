import duckdb


def run():
    con = duckdb.connect(database='data/activities.duckdb', read_only=False)
    con.execute(
        "CREATE TABLE activities AS SELECT * FROM read_csv_auto('data/activities.csv');"
    )

    con.execute(
        "CREATE TABLE activity_records AS SELECT * FROM read_csv_auto('data/activity_records.csv');"
    )


if __name__ == '__main__':
    run()
