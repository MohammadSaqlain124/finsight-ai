import time
from collections import defaultdict
from fastapi import HTTPException

# After MAX_FAILURES failed logins from one client within WINDOW_SECONDS,
# further attempts are blocked until the oldest failure rolls off the window.
MAX_FAILURES = 5
WINDOW_SECONDS = 300  # 5 minutes

# In-memory store: client key -> list of failure timestamps.
# NOTE: resets on server restart and is per-process (documented in SECURITY.md).
_failures: dict[str, list[float]] = defaultdict(list)


def _prune(key: str, now: float) -> None:
    _failures[key] = [t for t in _failures[key] if now - t < WINDOW_SECONDS]


def check_login_allowed(key: str) -> None:
    """Raise 429 if this client has too many recent failed logins."""
    now = time.time()
    _prune(key, now)
    if len(_failures[key]) >= MAX_FAILURES:
        retry_after = int(WINDOW_SECONDS - (now - _failures[key][0])) + 1
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Try again in {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )


def record_login_failure(key: str) -> None:
    _failures[key].append(time.time())


def reset_login_failures(key: str) -> None:
    _failures.pop(key, None)