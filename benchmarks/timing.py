#!/usr/bin/env python3
"""Shared high-resolution timing helpers for benchmark runners."""
from __future__ import annotations

from dataclasses import dataclass
import statistics
import time
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class TimingResult(Generic[T]):
    value: T
    median_ms: float
    iqr_ms: float
    repeats_per_sample: int
    samples: int
    timing_unit: str = "ms"
    measurement_status: str = "resolved"


def _percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("values must not be empty")
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def measure(
    fn: Callable[[], T],
    *,
    warmups: int = 2,
    samples: int = 7,
    min_window_ms: float = 20.0,
    max_repeats: int = 1_048_576,
) -> TimingResult[T]:
    """Measure ``fn`` using aggregate windows and robust sample statistics.

    Repetition count doubles until one aggregate sample lasts at least
    ``min_window_ms`` or ``max_repeats`` is reached. Reported latency is the
    per-call median across aggregate samples, with IQR as dispersion.
    """
    if warmups < 0 or samples < 1 or min_window_ms <= 0 or max_repeats < 1:
        raise ValueError("invalid timing configuration")

    value: T | None = None
    for _ in range(warmups):
        value = fn()

    repeats = 1
    while True:
        start = time.perf_counter_ns()
        for _ in range(repeats):
            value = fn()
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        if elapsed_ms >= min_window_ms or repeats >= max_repeats:
            break
        repeats = min(repeats * 2, max_repeats)

    per_call_ms: list[float] = []
    for _ in range(samples):
        start = time.perf_counter_ns()
        for _ in range(repeats):
            value = fn()
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        per_call_ms.append(elapsed_ms / repeats)

    q1 = _percentile(per_call_ms, 0.25)
    q3 = _percentile(per_call_ms, 0.75)
    return TimingResult(
        value=value,  # type: ignore[arg-type]
        median_ms=statistics.median(per_call_ms),
        iqr_ms=q3 - q1,
        repeats_per_sample=repeats,
        samples=samples,
    )
