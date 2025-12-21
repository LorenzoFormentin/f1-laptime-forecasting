from __future__ import annotations

import argparse
from pathlib import Path

from f1laptime.data.dataset_build import BuildPaths, build_for_session
from f1laptime.data.fastf1_loader import SessionSpec
from f1laptime.settings import DATA_DIR


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--event", type=str, required=True)
    p.add_argument("--session", type=str, required=True)
    args = p.parse_args()

    spec = SessionSpec(year=args.year, event_name=args.event, session=args.session)  # type: ignore[arg-type]

    paths = BuildPaths(
        interim_dir=DATA_DIR / "interim",
        processed_dir=DATA_DIR / "processed",
    )

    laps_path, examples_path = build_for_session(spec, paths=paths)
    print(f"Interim laps:     {laps_path}")
    print(f"Processed examples: {examples_path}")


if __name__ == "__main__":
    main()
