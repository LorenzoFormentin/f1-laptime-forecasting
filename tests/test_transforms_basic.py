import pandas as pd

from f1laptime.features.transforms_basic import build_next_lap_examples


def test_build_next_lap_examples_creates_target_and_lags():
    laps = pd.DataFrame(
        {
            "Year": [2024, 2024, 2024, 2024],
            "EventName": ["Bahrain"] * 4,
            "Session": ["R"] * 4,
            "Driver": ["AAA", "AAA", "AAA", "AAA"],
            "LapNumber": [1, 2, 3, 4],
            "Stint": [1, 1, 1, 1],
            "Compound": ["SOFT"] * 4,
            "LapTime": [
                pd.Timedelta(seconds=90),
                pd.Timedelta(seconds=89),
                pd.Timedelta(seconds=91),
                pd.Timedelta(seconds=88),
            ],
            "PitInTime": [pd.NaT] * 4,
            "PitOutTime": [pd.NaT] * 4,
        }
    )

    ex = build_next_lap_examples(laps)
    assert "LapTime_s" in ex.columns
    assert "LapTime_next_s" in ex.columns
    assert "LapTime_lag_1_s" in ex.columns
    # last lap has no next target -> should not appear
    assert ex["LapNumber"].max() == 3
