import asyncio

_stop = asyncio.Event()
RUNNING: set = set()


def is_stopped():
    return _stop.is_set()


def ensure_running():
    global _stop
    if _stop.is_set():
        _stop = asyncio.Event()


def stop_all():
    _stop.set()
    for t in list(RUNNING):
        t.cancel()
    RUNNING.clear()


def track(coro):
    ensure_running()
    t = asyncio.create_task(coro)
    RUNNING.add(t)
    t.add_done_callback(RUNNING.discard)
    return t
