from __future__ import annotations

from pathlib import Path

import fastf1

from f1laptime.settings import FASTF1_CACHE_DIR


def enable_fastf1_cache(cache_dir: Path | None = None) -> Path:
    """
    Enable FastF1 cache in a single, centralized place.

    Returns the cache directory used.
    """
    path = (cache_dir or FASTF1_CACHE_DIR).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(path))
    return path
