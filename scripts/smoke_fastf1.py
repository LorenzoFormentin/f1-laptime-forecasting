from __future__ import annotations

import argparse

from f1laptime.data.fastf1_loader import SessionSpec, load_session


def main() -> None:
    parser = argparse.ArgumentParser(description="FastF1 smoke test")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--event", type=str, default="Bahrain")
    parser.add_argument("--session", type=str, default="R", help="R, Q, FP1, ...")
    parser.add_argument("--telemetry", action="store_true")
    args = parser.parse_args()

    spec = SessionSpec(year=args.year, event_name=args.event, session=args.session)  # type: ignore[arg-type]
    sess = load_session(spec, with_telemetry=args.telemetry)

    laps = sess.laps
    print(f"Loaded: {args.year} {args.event} {args.session}")
    print(f"Laps rows: {len(laps)}")
    print("Columns:", list(laps.columns)[:15], "...")


if __name__ == "__main__":
    main()
