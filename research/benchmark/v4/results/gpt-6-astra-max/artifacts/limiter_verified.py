import asyncio
import math
import threading
import time


class AsyncTokenBucket:
    """Thread-safe shared bucket; full initially; no FIFO fairness guarantee."""

    def __init__(self, capacity: int, refill_rate: float):
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        if isinstance(refill_rate, bool) or not isinstance(refill_rate, (int, float)):
            raise TypeError("refill_rate must be numeric")
        rate = float(refill_rate)
        if not math.isfinite(rate) or rate <= 0:
            raise ValueError("refill_rate must be finite and positive")
        self._capacity = float(capacity)
        self._rate = rate
        self._tokens = float(capacity)
        self._updated = time.monotonic()
        self._lock = threading.Lock()

    async def acquire(self, tokens: int, timeout: float | None = None) -> bool:
        if type(tokens) is not int or not 0 < tokens <= self._capacity:
            raise ValueError("tokens must be a positive integer <= capacity")
        if timeout is not None:
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                raise TypeError("timeout must be numeric or None")
            timeout = float(timeout)
            if not math.isfinite(timeout) or timeout < 0:
                raise ValueError("timeout must be finite and nonnegative")
        deadline = None if timeout is None else time.monotonic() + timeout
        first = True
        while True:
            with self._lock:
                now = time.monotonic()
                if not first and deadline is not None and now >= deadline:
                    return False
                self._tokens = min(
                    self._capacity,
                    self._tokens + (now - self._updated) * self._rate,
                )
                self._updated = now
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
                delay = (tokens - self._tokens) / self._rate
            first = False
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                delay = min(delay, remaining)
            await asyncio.sleep(delay)

async def self_test():
    from concurrent.futures import ThreadPoolExecutor
    from unittest.mock import patch

    class Clock:
        value = 0.0

        @classmethod
        def monotonic(cls):
            return cls.value

    # Fractional refill, saturation and burst with a controlled clock.
    with patch(__name__ + ".time", Clock):
        b = AsyncTokenBucket(2, 0.5)
        assert await b.acquire(2, 0)
        Clock.value = 1.0
        assert not await b.acquire(1, 0)
        Clock.value = 2.0
        assert await b.acquire(1, 0)
        Clock.value = 100.0
        assert await b.acquire(2, 0)
        assert not await b.acquire(1, 0)

    b = AsyncTokenBucket(5, 1e-12)
    results = await asyncio.gather(*(b.acquire(1, 0) for _ in range(50)))
    assert sum(results) == 5
    assert not await b.acquire(1, 0.002)
    waiter = asyncio.create_task(b.acquire(1))
    await asyncio.sleep(0)
    waiter.cancel()
    try:
        await waiter
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("cancellation did not propagate")

    for tokens, timeout in [(0, None), (6, None), (True, None), (1, -1)]:
        try:
            await b.acquire(tokens, timeout)
        except (ValueError, TypeError):
            pass
        else:
            raise AssertionError("invalid request accepted")

    # Separate event loops on several threads share the same state.
    shared = AsyncTokenBucket(5, 1e-12)
    def worker(_):
        return asyncio.run(shared.acquire(1, 0))
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(worker, range(40))) == 5
    print("SELF-TEST PASS: refill, burst, contention, timeout, cancellation, validation, cross-thread loops")


if __name__ == "__main__":
    asyncio.run(self_test())
