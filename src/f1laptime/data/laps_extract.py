from __future__ import annotations

import pandas as pd

import fastf1


def extract_laps_table(
    session: fastf1.core.Session,
    *,
    year: int,
    event_name: str,
    session_name: str,
) -> pd.DataFrame:
    """
    Extract a tabular laps table from a FastF1 Session.

    This function does not decide ML targets or advanced features.
    It only standardizes metadata columns and keeps the raw lap fields we need.
    """
    laps = session.laps.copy()
    # Add stable identifiers
    laps["Year"] = int(year)
    laps["EventName"] = str(event_name)
    laps["Session"] = str(session_name)

    # Select a conservative set of columns.
    # We include core fields; you can extend later without breaking the pipeline.
    keep_cols = [
        "Year",
        "EventName",
        "Session",
        "Driver",
        "LapNumber",
        "Stint",
        "Compound",
        "LapTime",
        "PitInTime",
        "PitOutTime",
    ]

    # Some columns might be missing for certain sessions/years.
    # We'll keep only those that exist, but the contract will enforce essentials.
    keep_cols_existing = [c for c in keep_cols if c in laps.columns]
    out = laps[keep_cols_existing].copy()

    return out
