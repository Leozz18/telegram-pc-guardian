from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    def __init__(self, limit: int, window_seconds: float = 60.0, clock=time.monotonic):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self._events: deque[float] = deque()

    def allow(self) -> bool:
        now = self.clock()
        while self._events and now - self._events[0] >= self.window_seconds:
            self._events.popleft()
        if len(self._events) >= self.limit:
            return False
        self._events.append(now)
        return True
