from __future__ import annotations

import argparse
from pathlib import Path

from f1laptime.data.dataset_build import BuildPaths, build_for_session
from f1laptime.data.fastf1_loader import SessionSpec
from f1laptime.features.transforms_basic import BasicExampleSpec, LapCleanSpec
from f1laptime.settings import DATA_DIR


def _parse_int_list(value: str) -> tuple[int, ...]:
    if not value:
        return ()
    items = [part.strip() for part in value.split(",") if part.strip()]
    return tuple(int(part) for part in items)


def _parse_str_list(value: str) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(part.strip() for part in value.split(",") if part.strip())


def main() -> None:
    p = argparse.ArgumentParser(description="Build datasets from FastF1 sessions")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--event", type=str, required=True)
    p.add_argument("--session", type=str, required=True)
    p.add_argument(
        "--task",
        type=str,
        default="next_lap",
        choices=["next_lap", "none"],
        help="Which example task to build (use 'none' to skip examples)",
    )
    p.add_argument(
        "--lags",
        type=str,
        default="1,2,3",
        help="Comma-separated lag steps for next_lap examples (default: 1,2,3)",
    )
    p.add_argument("--extra-cols", type=str, default="", help="Extra lap columns to keep (comma-separated)")
    p.add_argument("--data-dir", type=str, default="", help="Override base data directory")
    p.add_argument("--interim-dir", type=str, default="", help="Override interim output directory")
    p.add_argument("--processed-dir", type=str, default="", help="Override processed output directory")
    p.add_argument("--tag", type=str, default="", help="Optional tag appended to output file names")
    p.add_argument(
        "--skip-clean-laps-output",
        action="store_true",
        help="Do not write cleaned laps to processed/",
    )
    p.add_argument("--keep-pit-laps", action="store_true", help="Keep pit in/out laps")
    p.add_argument("--keep-missing-driver", action="store_true", help="Keep rows with missing Driver")
    p.add_argument("--keep-missing-lap-number", action="store_true", help="Keep rows with missing LapNumber")
    p.add_argument("--keep-missing-lap-time", action="store_true", help="Keep rows with missing LapTime")
    p.add_argument("--min-lap-time-s", type=float, default=None, help="Drop laps below this time (seconds)")
    p.add_argument("--max-lap-time-s", type=float, default=None, help="Drop laps above this time (seconds)")
    p.add_argument("--with-telemetry", action="store_true", help="Load telemetry (slow)")
    p.add_argument("--no-weather", action="store_true", help="Skip weather data")
    p.add_argument("--no-messages", action="store_true", help="Skip race control messages")
    args = p.parse_args()

    spec = SessionSpec(year=args.year, event_name=args.event, session=args.session)  # type: ignore[arg-type]

    data_dir = Path(args.data_dir) if args.data_dir else DATA_DIR
    interim_dir = Path(args.interim_dir) if args.interim_dir else data_dir / "interim"
    processed_dir = Path(args.processed_dir) if args.processed_dir else data_dir / "processed"

    paths = BuildPaths(
        interim_dir=interim_dir,
        processed_dir=processed_dir,
    )

    lags = _parse_int_list(args.lags)
    extra_cols = _parse_str_list(args.extra_cols)
    examples_spec = BasicExampleSpec(lags=lags) if args.task == "next_lap" else BasicExampleSpec()

    clean_spec = LapCleanSpec(
        drop_pit_laps=not args.keep_pit_laps,
        drop_missing_driver=not args.keep_missing_driver,
        drop_missing_lap_number=not args.keep_missing_lap_number,
        drop_missing_lap_time=not args.keep_missing_lap_time,
        min_lap_time_s=args.min_lap_time_s,
        max_lap_time_s=args.max_lap_time_s,
    )

    artifacts = build_for_session(
        spec,
        paths=paths,
        examples_task=args.task,
        examples_spec=examples_spec,
        clean_spec=clean_spec,
        laps_extra_cols=extra_cols,
        output_tag=args.tag or None,
        save_clean_laps=not args.skip_clean_laps_output,
        with_telemetry=args.with_telemetry,
        with_weather=not args.no_weather,
        with_messages=not args.no_messages,
    )
    print(f"Interim laps:       {artifacts.laps_path}")
    if artifacts.clean_laps_path is not None:
        print(f"Processed clean laps: {artifacts.clean_laps_path}")
    if artifacts.examples_path is not None:
        print(f"Processed examples:  {artifacts.examples_path}")


if __name__ == "__main__":
    main()
