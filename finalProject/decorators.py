"""
decorators.py  –  Reusable decorators
──────────────────────────────────────
Two decorators that can wrap ANY function (sync or async):

1. log_action   – prints what's happening and catches errors gracefully
2. timer        – measures how long a function takes to run
"""

from __future__ import annotations

import asyncio
import functools
import time


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  1.  log_action  –  logs entry / exit / errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def log_action(func):
    """Decorator that logs when a function starts, finishes, or raises.

    Works with both regular *and* async functions.

    Example usage:
        @log_action
        async def load_students(): ...
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        print(f"  ▸ Starting: {func.__name__}()")
        try:
            result = await func(*args, **kwargs)
            print(f"  ✔ Finished: {func.__name__}()")
            return result
        except Exception as exc:
            print(f"  ✖ Error in {func.__name__}(): {exc}")
            raise                          # re‑raise so callers can still catch it

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        print(f"  ▸ Starting: {func.__name__}()")
        try:
            result = func(*args, **kwargs)
            print(f"  ✔ Finished: {func.__name__}()")
            return result
        except Exception as exc:
            print(f"  ✖ Error in {func.__name__}(): {exc}")
            raise

    # Return the right wrapper depending on whether the function is async
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  2.  timer  –  measures execution time
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def timer(func):
    """Decorator that prints how long a function took to execute.

    Example usage:
        @timer
        async def generate_report(): ...
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  ⏱  {func.__name__}() took {elapsed:.4f}s")
        return result

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  ⏱  {func.__name__}() took {elapsed:.4f}s")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
