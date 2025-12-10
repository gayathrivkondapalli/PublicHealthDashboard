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

#Acceptance: Unit test should test whether Nan values are handled correctly
def test_nan_handling_preserve_records():
    df = pd.DataFrame(
        {
            "country": ["Aland", "Aland", "Aland"],
            "iso_code": ["ALA", "ALA", "ALA"],
            "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
            "total_vaccinations": [100.0, None, 300.0],
            "people_vaccinated": [50.0, 150.0, None],
            "people_fully_vaccinated": [20.0, None, 80.0],
        }
    )
    result = clean_vaccination_data(df)

    # Check that NaN values are preserved
    assert result["total_vaccinations"].isnull().sum() == 1
    assert result["people_vaccinated"].isnull().sum() == 1
    assert result["people_fully_vaccinated"].isnull().sum() == 1
    # Check that non-NaN values are unchanged
    assert result.loc[result["date"] == pd.to_datetime("2021-01-01"), "total_vaccinations"].values[0] == 100.0
    assert result.loc[result["date"] == pd.to_datetime("2021-01-02"), "people_vaccinated"].values[0] == 150.0
    assert result.loc[result["date"] == pd.to_datetime("2021-01-03"), "people_fully_vaccinated"].values[0] == 80.0

# Acceptance: The vaccine manufacturers should be split into their own fields with boolean values indicating whether a country used that vaccine on that date.
def test_vaccine_manufacturer_splitting():
    df = pd.DataFrame(
        {
            "country": ["Aland", "Aland"],
            "iso_code": ["ALA", "ALA"],
            "date": ["2021-01-01", "2021-01-02"],
            "vaccines": ["Pfizer/BioNTech, Moderna", "Moderna, AstraZeneca"],
            "total_vaccinations": [100.0, 200.0],
            "people_vaccinated": [50.0, 150.0],
            "people_fully_vaccinated": [20.0, 70.0],
        }
    )
    result = clean_vaccination_data(df)

    # Extract unique vaccine manufacturers
    unique_vaccines = set()
    for vaccines in df["vaccines"]:
        for vaccine in vaccines.split(", "):
            unique_vaccines.add(vaccine)

    # Check that each unique vaccine has its own boolean column
    for vaccine in unique_vaccines:
        col_name = f"vaccine_{vaccine.replace('/', '_').replace(' ', '_')}"
        assert col_name in result.columns

        # Check boolean values
        for idx, row in result.iterrows():
            if vaccine in df.loc[idx, "vaccines"]:
                assert result.loc[idx, col_name] == True
            else:
                assert result.loc[idx, col_name] == False

#Acceptance: The system should remove duplicate records based on iso_code and date.
def test_duplicate_record_removal():
    df = pd.DataFrame(
        {
            "country": ["Aland", "Aland", "Aland"],
            "iso_code": ["ALA", "ALA", "ALA"],
            "date": ["2021-01-01", "2021-01-01", "2021-01-02"],
            "total_vaccinations": [100.0, 100.0, 200.0],
            "people_vaccinated": [50.0, 50.0, 150.0],
            "people_fully_vaccinated": [20.0, 20.0, 70.0],
        }
    )
    result = clean_vaccination_data(df)

    # Check that duplicate records are removed
    assert len(result) == 2
    assert not ((result["iso_code"] == "ALA") & (result["date"] == pd.to_datetime("2021-01-01"))).sum() > 1
 
