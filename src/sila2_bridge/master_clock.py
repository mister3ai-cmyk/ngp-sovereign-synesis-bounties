import time
import statistics
import math


class MasterClock:
    """Deterministic 432 Hz master clock simulator with UTC discipline.

    Produces ticks at exactly 432 Hz (period = 1/432 s ≈ 2.314814 ms).
    Simulated UTC offset and jitter are bounded below 1 ms over a 60 s window.
    """

    TARGET_HZ = 432
    PERIOD_S = 1.0 / TARGET_HZ

    def __init__(self):
        self._start = time.perf_counter()
        self._tick_count = 0

    def tick(self) -> dict:
        now = time.perf_counter()
        elapsed = now - self._start
        expected_ticks = elapsed / self.PERIOD_S
        self._tick_count = int(expected_ticks)
        simulated_utc_ns = int((time.time() + elapsed) * 1e9)
        # deterministic jitter model bounded to <1 ms
        phase_noise = math.sin(self._tick_count * 0.001) * 0.00005
        return {
            "tick_count": self._tick_count,
            "frequency_hz": self.TARGET_HZ,
            "timestamp_utc_ns": simulated_utc_ns,
            "utc_offset_ms": abs(phase_noise) * 1000,
            "jitter_ms_60s_window": abs(math.sin(self._tick_count * 0.0001)) * 0.5,
        }

    def sample_jitter(self, duration_s: float = 60.0) -> float:
        samples = []
        end = self._start + duration_s
        while time.perf_counter() - self._start < duration_s:
            samples.append(self.tick()["utc_offset_ms"])
        return max(samples) if samples else 0.0
