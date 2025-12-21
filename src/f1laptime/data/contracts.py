from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


# ---- Contracts (v0) ----
# Keep the contracts small and enforce only what we truly need.


LAPS_REQUIRED_COLUMNS: tuple[str, ...] = (
    "Year",
    "EventName",
    "Session",
    "Driver",
    "LapNumber",
    "Stint",
    "Compound",
    "LapTime",      # timedelta-like or string; will be normalized later
    "PitInTime",
    "PitOutTime",
)


EXAMPLES_REQUIRED_COLUMNS: tuple[str, ...] = (
    "Year",
    "EventName",
    "Session",
    "Driver",
    "LapNumber",
    "Stint",
    "Compound",
    "LapTime_s",
    "LapTime_next_s",
)


def require_columns(df: pd.DataFrame, required: Iterable[str], *, name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: missing required columns: {missing}")


def validate_laps_table(df: pd.DataFrame) -> None:
    require_columns(df, LAPS_REQUIRED_COLUMNS, name="laps_table")

    # Basic sanity checks (do not overfit to edge cases yet)
    if df["LapNumber"].isna().any():
        raise ValueError("laps_table: LapNumber contains NaN")
    if df["Driver"].isna().any():
        raise ValueError("laps_table: Driver contains NaN")


def validate_examples_table(df: pd.DataFrame) -> None:
    require_columns(df, EXAMPLES_REQUIRED_COLUMNS, name="examples_table")

    # Ensure numeric targets exist
    if df["LapTime_s"].isna().any():
        raise ValueError("examples_table: LapTime_s contains NaN")
    if df["LapTime_next_s"].isna().any():
        raise ValueError("examples_table: LapTime_next_s contains NaN")
