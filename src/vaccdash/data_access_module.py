import pandas as pd
import sqlite3

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
