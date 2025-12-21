from __future__ import annotations

import argparse
from pathlib import Path

from f1laptime.data.fastf1_loader import SessionSpec, load_session
from f1laptime.data.laps_extract import extract_laps_table
from f1laptime.data.contracts import validate_laps_table


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--event", type=str, required=True)
    p.add_argument("--session", type=str, required=True)
    p.add_argument("--out", type=str, required=True)
    args = p.parse_args()

    spec = SessionSpec(year=args.year, event_name=args.event, session=args.session)  # type: ignore[arg-type]
    sess = load_session(spec, with_telemetry=False)

    laps = extract_laps_table(sess, year=args.year, event_name=args.event, session_name=args.session)
    validate_laps_table(laps)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    laps.to_parquet(out_path, index=False)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
