"""Constitutional harness for OPS-002 / OPS-004: a bounded ring-buffer circuit breaker.

Failure rates are tracked per destination in a fixed ring of 60 one-second
buckets. Each bucket holds two 4-byte counters (attempts, failures), so the
window costs 60 * 2 * 4 = 480 bytes per destination no matter how much traffic
or how many retries hit it. 40,000 destinations fit in about 20-25 MB.

The breaker opens only when the rolling window has at least `min_samples`
attempts (default 20) and the failure ratio crosses `failure_threshold`.
After `open_seconds` it lets one probe through (half-open); success closes it,
failure re-opens it.

Agents must bind to this harness rather than writing retry loops or
timestamp deques (which grow linearly with traffic and crash workers during
retry storms).

pdd: implements OC-RES-DEPENDENCY-FAILURE stratum=workflow id=A-HARNESS-CIRCUIT-BREAKER
"""
from __future__ import annotations

import array
import random
import threading
import time
from typing import Callable, TypeVar

T = TypeVar("T")

WINDOW_SECONDS = 60
BYTES_PER_DESTINATION = WINDOW_SECONDS * 2 * 4  # 480


class CircuitOpenError(RuntimeError):
    pass


class _Window:
    """60 one-second buckets of (attempts, failures) as unsigned 32-bit ints."""

    __slots__ = ("attempts", "failures", "stamps")

    def __init__(self) -> None:
        self.attempts = array.array("I", [0] * WINDOW_SECONDS)
        self.failures = array.array("I", [0] * WINDOW_SECONDS)
        # Second each bucket was last written, used to lazily zero stale buckets.
        # Bookkeeping only; the 480 B budget covers the counters.
        self.stamps = array.array("q", [-1] * WINDOW_SECONDS)

    def _slot(self, now_s: int) -> int:
        i = now_s % WINDOW_SECONDS
        if self.stamps[i] != now_s:
            self.attempts[i] = 0
            self.failures[i] = 0
            self.stamps[i] = now_s
        return i

    def record(self, now_s: int, failed: bool) -> None:
        i = self._slot(now_s)
        self.attempts[i] = min(self.attempts[i] + 1, 0xFFFFFFFF)
        if failed:
            self.failures[i] = min(self.failures[i] + 1, 0xFFFFFFFF)

    def totals(self, now_s: int) -> tuple[int, int]:
        a = f = 0
        for i in range(WINDOW_SECONDS):
            if now_s - self.stamps[i] < WINDOW_SECONDS:
                a += self.attempts[i]
                f += self.failures[i]
        return a, f


class CircuitBreaker:
    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(
        self,
        failure_threshold: float = 0.5,
        min_samples: int = 20,
        open_seconds: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if min_samples < 20:
            raise ValueError("OPS-004 requires a minimum sample floor of at least 20 attempts")
        self.failure_threshold = failure_threshold
        self.min_samples = min_samples
        self.open_seconds = open_seconds
        self._clock = clock
        self._windows: dict[str, _Window] = {}
        self._opened_at: dict[str, float] = {}
        self._probing: set[str] = set()
        self._lock = threading.Lock()

    def state(self, destination: str) -> str:
        with self._lock:
            return self._state(destination, self._clock())

    def _state(self, destination: str, now: float) -> str:
        opened = self._opened_at.get(destination)
        if opened is None:
            return self.CLOSED
        if now - opened >= self.open_seconds:
            return self.HALF_OPEN
        return self.OPEN

    def allow(self, destination: str) -> bool:
        with self._lock:
            st = self._state(destination, self._clock())
            if st == self.CLOSED:
                return True
            if st == self.HALF_OPEN and destination not in self._probing:
                self._probing.add(destination)
                return True
            return False

    def record(self, destination: str, failed: bool) -> None:
        with self._lock:
            now = self._clock()
            st = self._state(destination, now)
            if st == self.HALF_OPEN and destination in self._probing:
                self._probing.discard(destination)
                if failed:
                    self._opened_at[destination] = now
                else:
                    self._opened_at.pop(destination, None)
                    self._windows.pop(destination, None)
                return
            w = self._windows.setdefault(destination, _Window())
            w.record(int(now), failed)
            attempts, failures = w.totals(int(now))
            if attempts >= self.min_samples and failures / attempts >= self.failure_threshold:
                self._opened_at[destination] = now

    def call(
        self,
        destination: str,
        fn: Callable[[], T],
        fallback: Callable[[], T] | None = None,
        retries: int = 2,
        base_delay: float = 0.1,
        max_delay: float = 2.0,
        sleep: Callable[[float], None] = time.sleep,
    ) -> T:
        """Run fn with bounded, jittered exponential backoff behind the breaker."""
        last: Exception | None = None
        for attempt in range(retries + 1):  # pdd: allow OPS-002 (this is the canonical harness)
            if not self.allow(destination):
                if fallback is not None:
                    return fallback()
                raise CircuitOpenError(destination)
            try:
                result = fn()
            except Exception as exc:  # noqa: BLE001 - recorded and re-raised below
                self.record(destination, failed=True)
                last = exc
                if attempt < retries:
                    sleep(min(max_delay, base_delay * 2 ** attempt) * random.uniform(0.5, 1.0))
                continue
            self.record(destination, failed=False)
            return result
        if fallback is not None:
            return fallback()
        assert last is not None
        raise last
