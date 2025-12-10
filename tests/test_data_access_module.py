import sqlite3
import pandas as pd

from vaccdash.data_access_module import init_db, load_csv_to_sqlite, query_country

# Requirement: System shall load cleaned vaccination data into SQLite.
def test_init_db_creates_vaccinations_table(tmp_path):
    db_path = tmp_path / "test.db"

    # Act
    init_db(db_path)

    # Assert: table exists
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='vaccinations';"
    )
    row = cur.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "vaccinations"

# Requirement: System shall load cleaned vaccination data into SQLite.
def test_init_db_table_schema(tmp_path):
    db_path = tmp_path / "test.db"

    # Act
    init_db(db_path)

    # Assert: table schema is correct
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(vaccinations);")
    columns = cur.fetchall()
    conn.close()

    expected_columns = [
        ("iso_code", "TEXT"),
        ("country", "TEXT"),
        ("location", "TEXT"),
        ("date", "TEXT"),
        ("total_vaccinations", "INTEGER"),
        ("people_vaccinated", "INTEGER"),
        ("people_fully_vaccinated", "INTEGER"),
        ("daily_vaccinations_raw", "INTEGER"),
        ("daily_vaccinations", "INTEGER"),
        ("total_vaccinations_per_hundred", "REAL"),
        ("people_vaccinated_per_hundred", "REAL"),
        ("people_fully_vaccinated_per_hundred", "REAL"),
        ("daily_vaccinations_per_million", "REAL"),
        ("vaccines", "TEXT"),
        ("source_name", "TEXT"),
        ("source_website", "TEXT"),
    ]

    for idx, (col_name, col_type) in enumerate(expected_columns):
        assert columns[idx][1] == col_name
        assert columns[idx][2] == col_type

# Acceptance: SQLLite Database contains records after initialization
def test_init_db_inserts_records(tmp_path):
    db_path = tmp_path / "test.db"

    # Act
    init_db(db_path)
    load_csv_to_sqlite("/Users/gayathrivkondapalli/Desktop/PGAI-Coursework/country_vaccinations.csv", db_path)

    # Assert: table is empty
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM vaccinations;")
    count = cur.fetchone()[0]
    conn.close()

    assert count > 0
# Acceptance: Query function retrieves correct records
def test_query_country_retrieves_correct_records(tmp_path):
    db_path = tmp_path / "test.db"

    # Act
    init_db(db_path)
    load_csv_to_sqlite("/Users/gayathrivkondapalli/Desktop/PGAI-Coursework/country_vaccinations.csv", db_path)

    conn = sqlite3.connect(db_path)
    result_df = query_country(conn, "USA", "2021-01-01", "2021-01-31")
    conn.close()

    # Assert: all records match the query criteria
    assert not result_df.empty
    assert all(result_df["iso_code"] == "USA")
    assert all(
        (result_df["date"] >= "2021-01-01") & (result_df["date"] <= "2021-01-31")
    )