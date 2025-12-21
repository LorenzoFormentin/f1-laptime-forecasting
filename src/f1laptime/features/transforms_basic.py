from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd


@dataclass(frozen=True)
class BasicExampleSpec:
    """
    Minimal spec for turning laps into supervised examples.

    We keep it small: later we can add other specs for different tasks.
    """
    lags: Sequence[int] = (1, 2, 3)


def _lap_time_to_seconds(series: pd.Series) -> pd.Series:
    """
    Convert a LapTime series to float seconds.

    FastF1 LapTime is typically pandas Timedelta-like; we handle string/None conservatively.
    """
    # If it's timedelta-like:
    if pd.api.types.is_timedelta64_dtype(series):
        return series.dt.total_seconds()

    # Try best-effort conversion:
    converted = pd.to_timedelta(series, errors="coerce")
    return converted.dt.total_seconds()


def clean_laps_minimal(laps: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning that is safe and task-agnostic.

    Current policy:
    - drop pit in/out laps
    - drop missing LapTime
    - drop missing Driver / LapNumber
    """
    df = laps.copy()

    # Ensure required columns exist before using them
    for col in ["PitInTime", "PitOutTime"]:
        if col in df.columns:
            df = df[df[col].isna()]

    df = df.dropna(subset=["Driver", "LapNumber", "LapTime"])
    return df


def build_next_lap_examples(
    laps: pd.DataFrame,
    *,
    spec: BasicExampleSpec = BasicExampleSpec(),
) -> pd.DataFrame:
    """
    Produce a supervised ML table where each row predicts next lap time.

    Output includes:
    - LapTime_s (current lap time)
    - LapTime_next_s (target)
    - Lag features: LapTime_lag_{k}_s
    """
    df = clean_laps_minimal(laps)

    # Sort by driver and lap number for temporal consistency
    df = df.sort_values(["Year", "EventName", "Session", "Driver", "LapNumber"]).copy()

    df["LapTime_s"] = _lap_time_to_seconds(df["LapTime"])

    # Drop if conversion failed
    df = df.dropna(subset=["LapTime_s"]).copy()

    # Group per (event, session, driver) to avoid mixing contexts
    group_cols = ["Year", "EventName", "Session", "Driver"]
    g = df.groupby(group_cols, sort=False)

    # Lag features
    for k in spec.lags:
        df[f"LapTime_lag_{k}_s"] = g["LapTime_s"].shift(k)

    # Target: next lap
    df["LapTime_next_s"] = g["LapTime_s"].shift(-1)

    # Keep only rows where target exists
    df = df.dropna(subset=["LapTime_next_s"]).copy()

    return df
