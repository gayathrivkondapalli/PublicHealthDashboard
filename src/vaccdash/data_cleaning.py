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

    return cleaned