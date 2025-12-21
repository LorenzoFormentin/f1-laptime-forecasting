import pandas as pd

from f1laptime.data.contracts import validate_laps_table, validate_examples_table


def test_validate_laps_table_ok():
    df = pd.DataFrame(
        {
            "Year": [2024],
            "EventName": ["Bahrain"],
            "Session": ["R"],
            "Driver": ["VER"],
            "LapNumber": [1],
            "Stint": [1],
            "Compound": ["SOFT"],
            "LapTime": [pd.Timedelta(seconds=90)],
            "PitInTime": [False],
            "PitOutTime": [False],
        }
    )
    validate_laps_table(df)


def test_validate_examples_table_ok():
    df = pd.DataFrame(
        {
            "Year": [2024],
            "EventName": ["Bahrain"],
            "Session": ["R"],
            "Driver": ["VER"],
            "LapNumber": [1],
            "Stint": [1],
            "Compound": ["SOFT"],
            "LapTime_s": [90.0],
            "LapTime_next_s": [89.5],
        }
    )
    validate_examples_table(df)
