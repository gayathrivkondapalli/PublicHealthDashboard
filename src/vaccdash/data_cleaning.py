import pandas as pd

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
    vaccination_cols = ["total_vaccinations", "people_vaccinated", "people_fully_vaccinated"]
    cleaned = cleaned.dropna(subset=vaccination_cols, how='all').reset_index(drop=True)

    return cleaned