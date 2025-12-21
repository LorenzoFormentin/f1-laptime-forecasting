from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import fastf1

from f1laptime.data.fastf1_cache import enable_fastf1_cache

SessionType = Literal["R", "Q", "FP1", "FP2", "FP3", "S", "SQ"]


@dataclass(frozen=True)
class SessionSpec:
    year: int
    event_name: str
    session: SessionType


def load_session(
    spec: SessionSpec,
    *,
    with_telemetry: bool = False,
    with_weather: bool = True,
    with_messages: bool = True,
) -> fastf1.core.Session:
    """
    Load a FastF1 session with a centralized cache policy.

    This function intentionally does NOT:
    - engineer features
    - filter laps
    - decide targets
    It only loads a session in a consistent, testable way.
    """
    enable_fastf1_cache()

    session = fastf1.get_session(spec.year, spec.event_name, spec.session)
    session.load(
        telemetry=with_telemetry,
        weather=with_weather,
        messages=with_messages,
    )
    return session
