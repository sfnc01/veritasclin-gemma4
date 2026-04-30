from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RateLimiter:
    max_rps: float
    _last_call: float = 0.0

    def wait(self) -> None:
        if self.max_rps <= 0:
            return
        minimum_interval = 1.0 / self.max_rps
        now = time.monotonic()
        elapsed = now - self._last_call
        if elapsed < minimum_interval:
            time.sleep(minimum_interval - elapsed)
        self._last_call = time.monotonic()
