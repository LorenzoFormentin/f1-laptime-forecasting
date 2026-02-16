from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd


@dataclass(frozen=True)
class LapCleanSpec:
    """
    Configurable but lightweight cleaning rules for laps tables.
    """
    drop_pit_laps: bool = True
    drop_missing_driver: bool = True
    drop_missing_lap_number: bool = True
    drop_missing_lap_time: bool = True
    min_lap_time_s: float | None = None
    max_lap_time_s: float | None = None


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


def clean_laps(
    laps: pd.DataFrame,
    *,
    spec: LapCleanSpec = LapCleanSpec(),
) -> pd.DataFrame:
    """
    Clean laps with a configurable but task-agnostic policy.
    """
    df = laps.copy()

    if spec.drop_pit_laps:
        for col in ["PitInTime", "PitOutTime"]:
            if col in df.columns:
                df = df[df[col].isna()]

    drop_cols: list[str] = []
    if spec.drop_missing_driver and "Driver" in df.columns:
        drop_cols.append("Driver")
    if spec.drop_missing_lap_number and "LapNumber" in df.columns:
        drop_cols.append("LapNumber")
    if spec.drop_missing_lap_time and "LapTime" in df.columns:
        drop_cols.append("LapTime")
    if drop_cols:
        df = df.dropna(subset=drop_cols)

    if spec.min_lap_time_s is not None or spec.max_lap_time_s is not None:
        lap_time_s = _lap_time_to_seconds(df["LapTime"])
        mask = lap_time_s.notna()
        if spec.min_lap_time_s is not None:
            mask &= lap_time_s >= spec.min_lap_time_s
        if spec.max_lap_time_s is not None:
            mask &= lap_time_s <= spec.max_lap_time_s
        df = df[mask].copy()

    return df


def clean_laps_minimal(laps: pd.DataFrame) -> pd.DataFrame:
    """
    Minimal cleaning that is safe and task-agnostic.

    Current policy:
    - drop pit in/out laps
    - drop missing LapTime
    - drop missing Driver / LapNumber
    """
    return clean_laps(laps)


def build_next_lap_examples(
    laps: pd.DataFrame,
    *,
    spec: BasicExampleSpec = BasicExampleSpec(),
    clean_spec: LapCleanSpec | None = LapCleanSpec(),
) -> pd.DataFrame:
    """
    Produce a supervised ML table where each row predicts next lap time.

    Output includes:
    - LapTime_s (current lap time)
    - LapTime_next_s (target)
    - Lag features: LapTime_lag_{k}_s
    """
    if len(set(spec.lags)) != len(spec.lags):
        raise ValueError("BasicExampleSpec.lags must be unique")
    if any(k <= 0 for k in spec.lags):
        raise ValueError("BasicExampleSpec.lags must be positive integers")

    if clean_spec is None:
        df = laps.copy()
    else:
        df = clean_laps(laps, spec=clean_spec)

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
