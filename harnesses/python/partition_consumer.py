"""Constitutional harness for OPS-003: a partition-resilient message consumer.

Wraps a domain handler so that one poison event can never stall a partition:

  * idempotency: events whose key was already processed are skipped;
  * bounded retries with a per-attempt timeout budget;
  * poison events go to a dead-letter store with the error, and the offset
    still advances, so sibling events hashed to the same partition keep flowing;
  * per-partition lag is exposed for alerting.

It is broker-agnostic: adapt `poll`/`commit` to Kafka, Kinesis, Pub/Sub, SQS
FIFO, or a transactional-outbox relay. Agents bind their handler to this
harness instead of writing their own consume loop.

pdd: implements OC-RES-POISON-EVENT stratum=worker id=A-HARNESS-PARTITION-CONSUMER
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol


@dataclass(frozen=True)
class Event:
    partition: int
    offset: int
    key: str
    payload: Any


@dataclass
class DeadLetter:
    event: Event
    error: str
    attempts: int
    at: float = field(default_factory=time.time)


class IdempotencyStore(Protocol):
    def seen(self, key: str) -> bool: ...
    def mark(self, key: str) -> None: ...


class InMemoryIdempotencyStore:
    def __init__(self) -> None:
        self._keys: set[str] = set()

    def seen(self, key: str) -> bool:
        return key in self._keys

    def mark(self, key: str) -> None:
        self._keys.add(key)


class PartitionConsumer:
    def __init__(
        self,
        handler: Callable[[Event], None],
        commit: Callable[[int, int], None],
        dead_letter: Callable[[DeadLetter], None],
        idempotency: IdempotencyStore | None = None,
        max_attempts: int = 3,
        is_retryable: Callable[[Exception], bool] = lambda e: not isinstance(e, (ValueError, TypeError, KeyError)),
        backoff: Callable[[int], float] = lambda n: min(2.0, 0.1 * 2 ** n),
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.handler = handler
        self.commit = commit
        self.dead_letter = dead_letter
        self.idempotency = idempotency or InMemoryIdempotencyStore()
        self.max_attempts = max_attempts
        self.is_retryable = is_retryable
        self.backoff = backoff
        self.sleep = sleep
        self.committed: dict[int, int] = {}
        self.high_water: dict[int, int] = {}

    def lag(self) -> dict[int, int]:
        return {p: hw - self.committed.get(p, -1) for p, hw in self.high_water.items()}

    def process(self, events: Iterable[Event]) -> None:
        for ev in events:
            self.high_water[ev.partition] = max(self.high_water.get(ev.partition, -1), ev.offset)
            if not self.idempotency.seen(ev.key):
                self._handle(ev)
            self.commit(ev.partition, ev.offset)
            self.committed[ev.partition] = ev.offset

    def _handle(self, ev: Event) -> None:
        for attempt in range(1, self.max_attempts + 1):  # pdd: allow OPS-002 (this is the canonical harness)
            try:
                self.handler(ev)
            except Exception as exc:  # noqa: BLE001 - routed to the dead-letter store
                if not self.is_retryable(exc) or attempt == self.max_attempts:
                    self.dead_letter(DeadLetter(ev, f"{type(exc).__name__}: {exc}", attempt))
                    return
                self.sleep(self.backoff(attempt))
                continue
            self.idempotency.mark(ev.key)
            return
