import sqlite3
import pandas as pd

from vaccdash.data_access_module import init_db

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
        ("continent", "TEXT"),
        ("location", "TEXT"),
        ("date", "TEXT"),
        ("total_vaccinations", "INTEGER"),
        ("people_vaccinated", "INTEGER"),
        ("people_fully_vaccinated", "INTEGER"),
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