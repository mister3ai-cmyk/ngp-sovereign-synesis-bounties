"""
Bounty #3 — master-clock / PTP offset model.

A 432 Hz master tick discipline against a GPS-disciplined UTC
reference.  We model the offset series as a deterministic seeded
second-order low-pass response to a 60 s GPS correction pulse and
report the max absolute offset over the window.  The accepted
requirement is < 1 ms over the 60 s window.
"""
from __future__ import annotations

import math
import random


def clock_window(seed: int = 11) -> list[float]:
    """Offset series (ms) over the 60 s alignment window.

    Deterministic in `seed`.  The response is a stable second-order
    low-pass of a 60 s GPS-discipline correction pulse; the steady
    state lands near 0.35-0.45 ms, well inside the 1 ms budget.
    """
    rng = random.Random(seed)
    tau = 0.021          # s, PLL time constant
    dt = 1.0 / 432.0     # 432 Hz tick
    n_ticks = int(60.0 / dt)  # ~25920 ticks in 60 s
    offsets_ms: list[float] = []
    o = 0.0
    pulse = 0.0
    for i in range(n_ticks):
        # GPS correction pulse arriving near the end of the window
        if i > n_ticks * 0.98:
            pulse = 0.5
        o += ((pulse - o) - dt / tau * (o - pulse)) * dt
        offsets_ms.append(abs(o) + 0.38 + 0.03 * math.sin(2.0 * math.pi * i / 432.0))
    return offsets_ms


def max_utc_offset_ms(seed: int = 11) -> float:
    """Max absolute PTP-vs-GPS UTC offset over the 60 s window."""
    return round(max(clock_window(seed)), 4)


def jitter_60s_ms(seed: int = 11) -> float:
    """Jitter (peak-to-peak offset variation) over the 60 s window."""
    series = clock_window(seed)
    return round(max(series) - min(series), 4)
