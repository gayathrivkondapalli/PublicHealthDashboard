
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time
import csv

# Query log for timing and export
query_log = []

def log_query_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        # Try to extract the SQL query string if possible
        query_str = ''
        if 'query' in func.__code__.co_varnames:
            # Try to get the query from local variables
            try:
                query_str = func.__code__.co_consts[1] if len(func.__code__.co_consts) > 1 else ''
            except Exception:
                query_str = func.__name__
        else:
            query_str = func.__name__
        query_log.append({
            "function": func.__name__,
            "query": query_str,
            "time_taken": end - start
        })
        return result
    return wrapper

def export_query_log_to_csv(filename="query_log.csv"):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["function", "query", "time_taken"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in query_log:
            writer.writerow(row)

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


@log_query_time
def query_country_by_ISO(conn, iso_code, start_date, end_date):
    query = """
    SELECT * FROM vaccinations 
    WHERE iso_code = ? AND date BETWEEN ? AND ?
    ORDER BY date
    """
    return pd.read_sql_query(query, conn, params=[iso_code, start_date, end_date])
export_query_log_to_csv()



@log_query_time
def query_country(conn, country, start_date, end_date):
    query = """
    SELECT * FROM vaccinations 
    WHERE country = ? AND date BETWEEN ? AND ?
    ORDER BY date
    """
    return pd.read_sql_query(query, conn, params=[country, start_date, end_date])
export_query_log_to_csv()


@log_query_time
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
export_query_log_to_csv()

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
export_query_log_to_csv()

def plot_daily_vaccinations(db_path, country, start_date, end_date):
    """
    Plots daily vaccinations for a given country over a specified date range.
    """
    conn = sqlite3.connect(db_path)
    df = query_country(conn, country, start_date, end_date)

    plt.figure(figsize=(10, 6))
    plt.plot(pd.to_datetime(df['date']), df['daily_vaccinations'], marker='o')
    plt.title(f'Daily Vaccinations in {country} from {start_date} to {end_date}')
    plt.xlabel('Date')
    plt.ylabel('Daily Vaccinations')
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.show()


def plot_vaccine_split(db_path):
    """
    Creates a pie chart showing the split of vaccinations by vaccine type,
    with all labels and percentages in the legend.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM vaccinations", conn)
    conn.close()

    vaccine_cols = [col for col in df.columns if col.startswith('vaccine_')]
    if not vaccine_cols:
        print("No split vaccine columns found.")
        return

    vaccine_counts = df[vaccine_cols].sum().sort_values(ascending=False)
    total = vaccine_counts.sum()
    labels = [
        f"{col.replace('vaccine_', '').replace('_', ' ')} ({count/total:.1%})"
        for col, count in zip(vaccine_counts.index, vaccine_counts)
    ]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, _ = ax.pie(
        vaccine_counts, labels=None, startangle=140
    )
    ax.set_title('Split of Vaccinations by Vaccine Type')
    ax.legend(wedges, labels, title="Vaccine Type", loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.show()

    