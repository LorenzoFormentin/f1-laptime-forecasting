from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import pandas as pd

from f1laptime.data.contracts import validate_examples_table, validate_laps_table
from f1laptime.data.fastf1_loader import SessionSpec, load_session
from f1laptime.data.laps_extract import extract_laps_table
from f1laptime.features.transforms_basic import (
    BasicExampleSpec,
    LapCleanSpec,
    build_next_lap_examples,
    clean_laps,
)


@dataclass(frozen=True)
class BuildPaths:
    interim_dir: Path
    processed_dir: Path


@dataclass(frozen=True)
class BuildArtifacts:
    laps_path: Path
    examples_path: Path | None
    clean_laps_path: Path | None


def build_for_session(
    spec: SessionSpec,
    *,
    paths: BuildPaths,
    examples_task: str = "next_lap",
    examples_spec: BasicExampleSpec = BasicExampleSpec(),
    clean_spec: LapCleanSpec = LapCleanSpec(),
    laps_extra_cols: Sequence[str] = (),
    output_tag: str | None = None,
    save_clean_laps: bool = True,
    with_telemetry: bool = False,
    with_weather: bool = True,
    with_messages: bool = True,
) -> BuildArtifacts:
    """
    Builds (1) interim laps table and (2) processed tables (clean laps, examples).
    Returns paths to the parquet files that were written.
    """
    paths.interim_dir.mkdir(parents=True, exist_ok=True)
    paths.processed_dir.mkdir(parents=True, exist_ok=True)

    session = load_session(
        spec,
        with_telemetry=with_telemetry,
        with_weather=with_weather,
        with_messages=with_messages,
    )

    laps = extract_laps_table(
        session,
        year=spec.year,
        event_name=spec.event_name,
        session_name=spec.session,
        extra_cols=laps_extra_cols,
    )

    validate_laps_table(laps)

    # Stable file names (no overdesign; enough to avoid collisions)
    base = f"year={spec.year}_event={spec.event_name}_session={spec.session}"
    if output_tag:
        base = f"{base}_tag={output_tag}"

    laps_path = paths.interim_dir / f"laps_{base}.parquet"
    laps.to_parquet(laps_path, index=False)
    clean_laps_path: Path | None = None
    examples_path: Path | None = None

    clean_laps_df: pd.DataFrame | None = None
    if save_clean_laps or (examples_task and examples_task != "none"):
        clean_laps_df = clean_laps(laps, spec=clean_spec)

    if save_clean_laps and clean_laps_df is not None:
        clean_laps_path = paths.processed_dir / f"laps_clean_{base}.parquet"
        clean_laps_df.to_parquet(clean_laps_path, index=False)

    if examples_task and examples_task != "none":
        if examples_task != "next_lap":
            raise ValueError(f"Unknown examples_task: {examples_task}")
        if clean_laps_df is None:
            clean_laps_df = clean_laps(laps, spec=clean_spec)
        examples = build_next_lap_examples(clean_laps_df, spec=examples_spec, clean_spec=None)
        validate_examples_table(examples)
        examples_path = paths.processed_dir / f"examples_{examples_task}_{base}.parquet"
        examples.to_parquet(examples_path, index=False)

    return BuildArtifacts(
        laps_path=laps_path,
        examples_path=examples_path,
        clean_laps_path=clean_laps_path,
    )
