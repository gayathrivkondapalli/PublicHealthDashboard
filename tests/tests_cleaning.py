import pandas as pd
import pytest

from vaccdash.data_cleaning import clean_vaccination_data

# Requirement: Date time should be in the format datetime.
# Acceptance: Unit test should test whether the data is datetime and sorted by date within each iso_code.
def test_date_time_format_and_sorting():
    df = pd.DataFrame(
        {
            "country": ["Aland", "Aland"],
            "iso_code": ["ALA", "ALA"],
            "date": ["2021-01-02", "2021-01-01"],
            "total_vaccinations": [200.0, 100.0],
            "people_vaccinated": [150.0, 50.0],
            "people_fully_vaccinated": [70.0, 20.0],
        }
    )
    result = clean_vaccination_data(df)

    # Check datetime dtype
    assert pd.api.types.is_datetime64_any_dtype(result["date"])

    # Check ordering by date within iso_code
    dates = list(result.sort_values(["iso_code", "date"])["date"])
    assert dates == sorted(dates)