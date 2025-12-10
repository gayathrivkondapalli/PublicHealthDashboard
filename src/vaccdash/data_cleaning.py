import pandas as pd
import logging
logger = logging.getLogger("data_cleaning")

def clean_vaccination_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the 'date' column to datetime and sort records
    by iso_code then date.
    """
    cleaned = df.copy()

    # Convert date to datetime
    cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce")

    # Sort by iso_code then date
    cleaned = cleaned.sort_values(["iso_code", "date"]).reset_index(drop=True)

    #Drop rows where all vaccination columns are NaN. If only one or two columns are NaN, we keep the record.
    logger.info("Dropping records with all vaccination data missing")
    vaccination_cols = ["total_vaccinations", "people_vaccinated", "people_fully_vaccinated"]
    cleaned = cleaned.dropna(subset=vaccination_cols, how='all').reset_index(drop=True)

    # Split vaccine manufacturers into separate boolean columns (AI enhancement)
    logger.info("Splitting vaccine manufacturers into separate boolean columns")
    if "vaccines" in cleaned.columns:
        unique_vaccines = set()
        for vaccines in cleaned["vaccines"].dropna():
            for vaccine in vaccines.split(", "):
                unique_vaccines.add(vaccine)

        for vaccine in sorted(unique_vaccines):
            col_name = f"vaccine_{vaccine.replace('/', '_').replace(' ', '_')}"
            cleaned[col_name] = cleaned["vaccines"].apply(lambda x: vaccine in x.split(", ") if pd.notna(x) else False)

    # Remove duplicate records based on iso_code and date, keeping the first occurrence
    logger.info("Removing duplicate records based on iso_code and date")
    cleaned = cleaned.drop_duplicates(subset=["iso_code", "date"], keep="first").reset_index(drop=True)

    # Calculate the ratio of people fully vaccinated to total vaccinations
    logger.info("Calculating fully vaccinated ratio")
    cleaned["fully_vaccinated_ratio"] = cleaned["people_fully_vaccinated"] / cleaned["total_vaccinations"]

    return cleaned


