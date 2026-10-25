import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harnesses.python.circuit_breaker import BYTES_PER_DESTINATION, CircuitBreaker, CircuitOpenError, _Window  # noqa: E402
from harnesses.python.partition_consumer import Event, PartitionConsumer  # noqa: E402


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class TestCircuitBreaker(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.cb = CircuitBreaker(failure_threshold=0.5, min_samples=20, open_seconds=30, clock=self.clock)

    def test_counter_footprint_is_480_bytes(self):
        w = _Window()
        counters = w.attempts.itemsize * len(w.attempts) + w.failures.itemsize * len(w.failures)
        self.assertEqual(counters, BYTES_PER_DESTINATION)
        self.assertEqual(BYTES_PER_DESTINATION, 480)

    def test_minimum_sample_floor_is_enforced(self):
        with self.assertRaises(ValueError):
            CircuitBreaker(min_samples=5)
        for _ in range(19):
            self.cb.record("d", failed=True)
        self.assertEqual(self.cb.state("d"), "closed")
        self.cb.record("d", failed=True)
        self.assertEqual(self.cb.state("d"), "open")

    def test_memory_stays_bounded_under_retry_storm(self):
        for i in range(200_000):
            self.clock.t = 1000 + i / 5000  # 40 seconds of very high traffic
            self.cb.record("d", failed=False)
        w = self.cb._windows["d"]
        self.assertEqual(len(w.attempts), 60)
        self.assertEqual(w.totals(int(self.clock.t))[0], 200_000)

    def test_old_buckets_expire(self):
        for _ in range(30):
            self.cb.record("d", failed=False)
        self.clock.t += 61
        self.assertEqual(self.cb._windows["d"].totals(int(self.clock.t)), (0, 0))

    def test_half_open_probe_closes_on_success(self):
        for _ in range(20):
            self.cb.record("d", failed=True)
        self.assertFalse(self.cb.allow("d"))
        self.clock.t += 31
        self.assertTrue(self.cb.allow("d"))
        self.assertFalse(self.cb.allow("d"))  # only one probe
        self.cb.record("d", failed=False)
        self.assertEqual(self.cb.state("d"), "closed")

    def test_call_uses_fallback_when_open(self):
        for _ in range(20):
            self.cb.record("d", failed=True)
        self.assertEqual(self.cb.call("d", lambda: "live", fallback=lambda: "cached"), "cached")
        with self.assertRaises(CircuitOpenError):
            self.cb.call("d", lambda: "live")

    def test_call_retries_with_bounded_backoff(self):
        attempts, sleeps = [], []

        def flaky():
            attempts.append(1)
            if len(attempts) < 3:
                raise TimeoutError()
            return "ok"

        self.assertEqual(self.cb.call("d", flaky, retries=2, sleep=sleeps.append), "ok")
        self.assertEqual(len(attempts), 3)
        self.assertTrue(all(s <= 2.0 for s in sleeps))


class TestPartitionConsumer(unittest.TestCase):
    def test_poison_event_is_dead_lettered_and_partition_keeps_flowing(self):
        handled, commits, dlq = [], [], []

        def handler(ev):
            if ev.payload == "poison":
                raise ValueError("malformed")
            handled.append(ev.offset)

        c = PartitionConsumer(handler, lambda p, o: commits.append((p, o)), dlq.append, sleep=lambda s: None)
        c.process([Event(0, 0, "k0", "ok"), Event(0, 1, "k1", "poison"), Event(0, 2, "k2", "ok")])
        self.assertEqual(handled, [0, 2])
        self.assertEqual([d.event.offset for d in dlq], [1])
        self.assertEqual(commits[-1], (0, 2))
        self.assertEqual(c.lag(), {0: 0})

    def test_transient_errors_retry_then_dead_letter(self):
        calls, dlq = [], []

        def handler(ev):
            calls.append(1)
            raise TimeoutError()

        c = PartitionConsumer(handler, lambda p, o: None, dlq.append, max_attempts=3, sleep=lambda s: None)
        c.process([Event(0, 0, "k", None)])
        self.assertEqual(len(calls), 3)
        self.assertEqual(dlq[0].attempts, 3)

    def test_idempotent_redelivery(self):
        handled = []
        c = PartitionConsumer(lambda ev: handled.append(ev.key), lambda p, o: None, lambda d: None)
        c.process([Event(0, 0, "same", 1), Event(1, 0, "same", 1)])
        self.assertEqual(handled, ["same"])


if __name__ == "__main__":
    unittest.main()
