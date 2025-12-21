from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from f1laptime.data.contracts import validate_examples_table, validate_laps_table
from f1laptime.data.fastf1_loader import SessionSpec, load_session
from f1laptime.data.laps_extract import extract_laps_table
from f1laptime.features.transforms_basic import BasicExampleSpec, build_next_lap_examples


@dataclass(frozen=True)
class BuildPaths:
    interim_dir: Path
    processed_dir: Path


def build_for_session(
    spec: SessionSpec,
    *,
    paths: BuildPaths,
    examples_spec: BasicExampleSpec = BasicExampleSpec(),
    with_telemetry: bool = False,
) -> tuple[Path, Path]:
    """
    Builds (1) interim laps table and (2) processed examples table for one session.
    Returns paths to the two parquet files.
    """
    paths.interim_dir.mkdir(parents=True, exist_ok=True)
    paths.processed_dir.mkdir(parents=True, exist_ok=True)

    session = load_session(spec, with_telemetry=with_telemetry)

    laps = extract_laps_table(
        session,
        year=spec.year,
        event_name=spec.event_name,
        session_name=spec.session,
    )

    validate_laps_table(laps)

    examples = build_next_lap_examples(laps, spec=examples_spec)
    validate_examples_table(examples)

    # Stable file names (no overdesign; enough to avoid collisions)
    base = f"year={spec.year}_event={spec.event_name}_session={spec.session}"

    laps_path = paths.interim_dir / f"laps_{base}.parquet"
    examples_path = paths.processed_dir / f"examples_{base}.parquet"

    laps.to_parquet(laps_path, index=False)
    examples.to_parquet(examples_path, index=False)

    return laps_path, examples_path
