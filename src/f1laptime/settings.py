from __future__ import annotations

import os
from pathlib import Path


def _project_root() -> Path:
    # src/f1laptime/settings.py -> src/f1laptime -> src -> project root
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT: Path = _project_root()

# Where project data lives (can be overridden)
DATA_DIR: Path = Path(os.environ.get("F1LTF_DATA_DIR", PROJECT_ROOT / "data"))

# FastF1 cache directory (can be overridden)
FASTF1_CACHE_DIR: Path = Path(
    os.environ.get("FASTF1_CACHE_DIR", DATA_DIR / "cache" / "fastf1")
)
