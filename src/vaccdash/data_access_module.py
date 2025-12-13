import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

def init_db(db_path):
   

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create vaccinations table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vaccinations (
            iso_code TEXT,
            country TEXT,
            location TEXT,
            date TEXT,
            total_vaccinations INTEGER,
            people_vaccinated INTEGER,
            people_fully_vaccinated INTEGER,
            daily_vaccinations_raw INTEGER,
            daily_vaccinations INTEGER,
            total_vaccinations_per_hundred REAL,
            people_vaccinated_per_hundred REAL,
            people_fully_vaccinated_per_hundred REAL,
            daily_vaccinations_per_million REAL,
            vaccines TEXT,
            source_name TEXT,
            source_website TEXT
        );
        """)


    conn.commit()
    

    conn.close()

def load_csv_to_sqlite(csv_path, db_path):
     df = pd.read_csv(csv_path)
     conn = sqlite3.connect(db_path)
     df.to_sql('vaccinations', conn, if_exists='append', index=False)
     conn.close()

def query_country_by_ISO(conn, iso_code, start_date, end_date):
    query = """
    SELECT * FROM vaccinations 
    WHERE iso_code = ? AND date BETWEEN ? AND ?
    ORDER BY date
    """
    return pd.read_sql_query(query, conn, params=[iso_code, start_date, end_date])

def query_country(conn, country, start_date, end_date):
    query = """
    SELECT * FROM vaccinations 
    WHERE country = ? AND date BETWEEN ? AND ?
    ORDER BY date
    """
    return pd.read_sql_query(query, conn, params=[country, start_date, end_date])

def count_countries_using_vaccine(conn, vaccine_name):
    """
    Returns the number of distinct countries that use the specified vaccine.
    """
    query = """
    SELECT COUNT(DISTINCT country) as country_count
    FROM vaccinations
    WHERE vaccines LIKE '%' || ? || '%'
    """
    result = pd.read_sql_query(query, conn, params=[vaccine_name])
    return result['country_count'].iloc[0]

def plot_source_distribution(db_path):
    """
    Creates a pie chart showing the distribution of data sources in the vaccinations table.
    """
    conn = sqlite3.connect(db_path)
    query = "SELECT source_name, COUNT(*) as count FROM vaccinations GROUP BY source_name"
    df = pd.read_sql_query(query, conn)
    conn.close()

    plt.figure(figsize=(8, 8))
    plt.pie(df['count'], labels=df['source_name'], autopct='%1.1f%%', startangle=140)
    plt.title('Distribution of Data Sources')
    plt.tight_layout()
    plt.show()