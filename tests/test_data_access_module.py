import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from vaccdash.data_access_module import init_db, load_csv_to_sqlite, query_country_by_ISO, query_country, plot_source_distribution, plot_daily_vaccinations


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
# Acceptance: Query function to retreive country records by date retrieves correct records
def test_query_country_by_ISO_retrieves_correct_records(tmp_path):
    db_path = tmp_path / "test.db"

    # Act
    init_db(db_path)
    load_csv_to_sqlite("/Users/gayathrivkondapalli/Desktop/PGAI-Coursework/country_vaccinations.csv", db_path)

    conn = sqlite3.connect(db_path)
    result_df = query_country_by_ISO(conn, "USA", "2021-01-01", "2021-01-31")
    conn.close()

    # Assert: all records match the query criteria
    assert not result_df.empty
    assert all(result_df["iso_code"] == "USA")
    assert all(
        (result_df["date"] >= "2021-01-01") & (result_df["date"] <= "2021-01-31")
    )

    #Acceptance: Query function to retreive country records by date retrieves records in date order
def test_query_country_retrieves_records(tmp_path):
    db_path = tmp_path / "test.db"

    init_db(db_path)
    load_csv_to_sqlite("/Users/gayathrivkondapalli/Desktop/PGAI-Coursework/country_vaccinations.csv", db_path)

    conn = sqlite3.connect(db_path)
    result_df = query_country(conn, "Algeria", "2021-01-01", "2021-01-31")
    conn.close()

    # Assert: records are in date order
    assert not result_df.empty

def test_plot_source_distribution(tmp_path, monkeypatch):
    # Create a temporary SQLite database
    db_path = tmp_path / "test.db"
    init_db(db_path)

    # Insert mock data with different source_names
    conn = sqlite3.connect(db_path)
    df = pd.DataFrame({
        "iso_code": ["AAA", "BBB", "CCC"],
        "country": ["CountryA", "CountryB", "CountryC"],
        "location": ["LocA", "LocB", "LocC"],
        "date": ["2021-01-01"]*3,
        "total_vaccinations": [100, 200, 300],
        "people_vaccinated": [50, 150, 250],
        "people_fully_vaccinated": [25, 75, 125],
        "daily_vaccinations_raw": [10, 20, 30],
        "daily_vaccinations": [10, 20, 30],
        "total_vaccinations_per_hundred": [1.0, 2.0, 3.0],
        "people_vaccinated_per_hundred": [0.5, 1.5, 2.5],
        "people_fully_vaccinated_per_hundred": [0.25, 0.75, 1.25],
        "daily_vaccinations_per_million": [100, 200, 300],
        "vaccines": ["A", "B", "C"],
        "source_name": ["Source1", "Source2", "Source1"],
        "source_website": ["site1", "site2", "site1"]
    })
    df.to_sql('vaccinations', conn, if_exists='append', index=False)
    conn.close()

    # Patch plt.show to prevent the plot window from blocking the test
    monkeypatch.setattr(plt, "show", lambda: None)

    # This should run without error and call plt.show (which is patched)
    plot_source_distribution(db_path)

def test_count_countries_using_vaccine(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    # Insert mock data
    conn = sqlite3.connect(db_path)
    df = pd.DataFrame({
        "iso_code": ["AAA", "BBB", "CCC", "DDD"],
        "country": ["CountryA", "CountryB", "CountryC", "CountryD"],
        "location": ["LocA", "LocB", "LocC", "LocD"],
        "date": ["2021-01-01"]*4,
        "total_vaccinations": [100, 200, 300, 400],
        "people_vaccinated": [50, 150, 250, 350],
        "people_fully_vaccinated": [25, 75, 125, 175],
        "daily_vaccinations_raw": [10, 20, 30, 40],
        "daily_vaccinations": [10, 20, 30, 40],
        "total_vaccinations_per_hundred": [1.0, 2.0, 3.0, 4.0],
        "people_vaccinated_per_hundred": [0.5, 1.5, 2.5, 3.5],
        "people_fully_vaccinated_per_hundred": [0.25, 0.75, 1.25, 1.75],
        "daily_vaccinations_per_million": [100, 200, 300, 400],
        "vaccines": ["VaccineA", "VaccineB", "VaccineA", "VaccineC"],
        "source_name": ["Source1"]*4,
        "source_website": ["site1"]*4
    })
    df.to_sql('vaccinations', conn, if_exists='append', index=False)

    # Act
    from vaccdash.data_access_module import count_countries_using_vaccine
    country_count = count_countries_using_vaccine(conn, "VaccineA")

    # Assert
    assert country_count == 2  # CountryA and CountryC use VaccineA

    conn.close()

def test_create_visualisation_for_daily_vaccine_rates_for_a_date_range_for_a_country(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    # Insert mock data
    conn = sqlite3.connect(db_path)
    df = pd.DataFrame({
        "iso_code": ["AAA"] * 5,
        "country": ["CountryA"] * 5,
        "location": ["LocA"] * 5,
        "date": pd.date_range(start="2021-01-01", periods=5).astype(str),
        "total_vaccinations": [100, 200, 300, 400, 500],
        "people_vaccinated": [50, 150, 250, 350, 450],
        "people_fully_vaccinated": [25, 75, 125, 175, 225],
        "daily_vaccinations_raw": [10, 20, 30, 40, 50],
        "daily_vaccinations": [10, 20, 30, 40, 50],
        "total_vaccinations_per_hundred": [1.0, 2.0, 3.0, 4.0, 5.0],
        "people_vaccinated_per_hundred": [0.5, 1.5, 2.5, 3.5, 4.5],
        "people_fully_vaccinated_per_hundred": [0.25, 0.75, 1.25, 1.75, 2.25],
        "daily_vaccinations_per_million": [100, 200, 300, 400, 500],
        "vaccines": ["VaccineA"] * 5,
        "source_name": ["Source1"] * 5,
        "source_website": ["site1"] * 5
    })
    df.to_sql('vaccinations', conn, if_exists='append', index=False)

    # Patch plt.show to prevent the plot window from blocking the test
    monkeypatch.setattr(plt, "show", lambda: None)

    plot_daily_vaccinations(db_path, "CountryA", "2021-01-01", "2021-01-05")
    conn.close()


