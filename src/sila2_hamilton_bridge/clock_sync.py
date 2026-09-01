import time
import threading

class MasterClock:
    def __init__(self, frequency=432):
        self.frequency = frequency
        self.interval_ns = int(1e9 / frequency)
        self.lock = threading.Lock()
        self.jitter_window = []
        self._start_sync()

    def _start_sync(self):
        self.base_time = time.time_ns()

    def get_timestamp_ns(self):
        with self.lock:
            ts = time.time_ns()
            self._record_jitter(ts)
            return ts

    def get_iso_timestamp(self):
        return time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime(time.time()))

    def _record_jitter(self, ts):
        self.jitter_window.append(ts)
        if len(self.jitter_window) > 1000:
            self.jitter_window.pop(0)

    def get_jitter_ms(self):
        if len(self.jitter_window) < 2:
            return 0.0
        
        diffs = []
        for i in range(1, len(self.jitter_window)):
            actual = self.jitter_window[i] - self.jitter_window[i-1]
            diffs.append(abs(actual - self.interval_ns))
        
        return max(diffs) / 1e6 if diffs else 0.0