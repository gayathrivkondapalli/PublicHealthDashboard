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